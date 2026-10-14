
import csv
import sys
import time
from pathlib import Path
from datetime import datetime

import serial

# ===========================================
# FARMTECH SOLUTIONS - ARABICASENSE
# FIAP
# Experimento - Coleta integrada
# Sitio Alto da Serra - Manhuacu/MG
# ===========================================

BASE = Path(__file__).resolve().parent
ARQUIVO = BASE / "dados" / "historico_sensores.csv"

PORTA = "rfc2217://localhost:4000"
BAUDRATE = 115200

REGISTROS_ORIGINAIS = 100
REGISTROS_POR_CENARIO = 20

COLUNAS = [
    "data_hora", "tempo_ms", "nitrogenio",
    "fosforo", "potassio", "ph", "umidade",
    "chuva_prevista", "bomba"
]

# Umidade, comando meteorologico e estado esperado
CENARIOS = [
    (55, -1, 0, "Condicao inicial"),
    (30,  0, 1, "Solo seco"),
    (42,  0, 1, "Teste de histerese"),
    (50,  0, 0, "Umidade recuperada"),
    (25,  1, 0, "Bloqueio por chuva"),
    (30,  0, 1, "Retomada da irrigacao")
]


def contar_registros():
    if not ARQUIVO.exists():
        raise FileNotFoundError(
            f"Historico nao encontrado: {ARQUIVO}"
        )

    with ARQUIVO.open(
        "r", encoding="utf-8-sig", newline=""
    ) as arquivo:
        leitor = csv.reader(arquivo)
        cabecalho = next(leitor, None)

        if cabecalho != COLUNAS:
            raise ValueError(
                "Colunas do CSV diferentes das esperadas."
            )

        return sum(1 for linha in leitor if linha)


def converter_linha(texto):
    if not texto.startswith("DADOS_CSV,"):
        return None

    partes = texto.split(",")

    if len(partes) != 9:
        return None

    try:
        valores = [
            int(partes[1]),
            float(partes[2]),
            float(partes[3]),
            float(partes[4]),
            float(partes[5]),
            float(partes[6]),
            int(partes[7]),
            int(partes[8])
        ]

        if valores[6] not in (-1, 0, 1):
            return None

        if valores[7] not in (0, 1):
            return None

        return valores

    except ValueError:
        return None


def enviar_comando(conexao, previsao):
    valor = (
        "INDEFINIDA" if previsao == -1
        else str(previsao)
    )

    comando = f"CHUVA_PREVISTA={valor}"

    conexao.write(
        (comando + "\n").encode("ascii")
    )
    conexao.flush()

    print(f"Comando enviado: {comando}")


def executar_cenario(
    conexao, escritor, arquivo,
    numero, cenario
):
    umidade_alvo, previsao, bomba, nome = cenario

    print("\n" + "=" * 45)
    print(f"CENARIO {numero}: {nome}")
    print(f"Umidade esperada: {umidade_alvo}%")
    print(f"Previsao: {previsao}")
    print(f"Bomba esperada: {bomba}")
    print("=" * 45)

    print("\nAjuste o DHT22 no Wokwi.")
    print("Ajuste NPK e LDR, se desejar.")

    input(
        "\nPressione ENTER quando estiver pronto..."
    )

    # Descartar mensagens antigas recebidas
    conexao.reset_input_buffer()

    # Enviar a previsao pela mesma conexao
    enviar_comando(conexao, previsao)

    total = 0
    divergencias = 0
    inicio = time.monotonic()

    print("\nIniciando coleta...")

    while total < REGISTROS_POR_CENARIO:

        if time.monotonic() - inicio > 180:
            raise TimeoutError(
                f"Tempo esgotado no cenario {numero}. "
                f"Coletados: {total}"
            )

        texto = conexao.readline().decode(
            "utf-8", errors="replace"
        ).strip()

        valores = converter_linha(texto)

        if valores is None:
            continue

        # Indices:
        # 0 tempo, 5 umidade, 6 previsao, 7 bomba
        umidade_atual = valores[5]
        previsao_atual = valores[6]
        bomba_atual = valores[7]

        # Esperar o ESP32 processar os novos dados
        if previsao_atual != previsao:
            continue

        if abs(umidade_atual - umidade_alvo) > 2:
            continue

        escritor.writerow([
            datetime.now().astimezone().isoformat(
                timespec="seconds"
            ),
            *valores
        ])

        arquivo.flush()
        total += 1

        if bomba_atual != bomba:
            divergencias += 1

        print(
            f"Cenario {numero}: "
            f"{total}/{REGISTROS_POR_CENARIO} | "
            f"Umidade: {umidade_atual:.1f}% | "
            f"Bomba: {bomba_atual}"
        )

    print(f"\nCenario {numero} concluido!")

    if divergencias:
        print(
            f"ATENCAO: {divergencias} registros "
            "com bomba diferente do esperado."
        )


def main():
    existentes = contar_registros()

    print("===================================")
    print(" ARABICASENSE - EXPERIMENTO 02")
    print("===================================")
    print(f"Registros existentes: {existentes}")

    if existentes != REGISTROS_ORIGINAIS:
        raise ValueError(
            "Esperados exatamente 100 registros "
            "anteriores. Confira o CSV antes "
            "de iniciar para evitar duplicacao."
        )

    print("Novos registros previstos: 120")
    print("Total esperado: 220")

    print("\nMantenha o Wokwi executando.")
    print("Feche outros monitores RFC2217.")

    input("\nPressione ENTER para conectar...")

    with serial.serial_for_url(
        PORTA,
        baudrate=BAUDRATE,
        timeout=3
    ) as conexao:

        with ARQUIVO.open(
            "a", encoding="utf-8", newline=""
        ) as arquivo:

            escritor = csv.writer(arquivo)

            for numero, cenario in enumerate(
                CENARIOS, start=1
            ):
                executar_cenario(
                    conexao, escritor,
                    arquivo, numero, cenario
                )

    print("\n===================================")
    print(" EXPERIMENTO CONCLUIDO")
    print("===================================")
    print(
        f"Total no CSV: {contar_registros()}"
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nColeta interrompida.")
        print("Os registros salvos foram preservados.")
    except (
        serial.SerialException,
        OSError,
        ValueError,
        TimeoutError
    ) as erro:
        print(f"\nERRO: {erro}")
        sys.exit(1)
