
import csv
import time
import sys
import serial

from pathlib import Path
from datetime import datetime

# ==========================================
# FARMTECH SOLUTIONS - ARABICASENSE
# FIAP
# Coleta de dados para analise em R
# ==========================================

PORTA = "rfc2217://localhost:4000"
BAUDRATE = 115200

# Limite de registros por execucao
MAX_REGISTROS = 100

PASTA = Path(__file__).resolve().parent
PASTA_DADOS = PASTA / "dados"
ARQUIVO = PASTA_DADOS / "historico_sensores.csv"

COLUNAS = [
    "data_hora",
    "tempo_ms",
    "nitrogenio",
    "fosforo",
    "potassio",
    "ph",
    "umidade",
    "chuva_prevista",
    "bomba"
]


def salvar_registro(linha, escritor):
    if not linha.startswith("DADOS_CSV,"):
        return False

    partes = linha.split(",")

    if len(partes) != 9:
        print("Registro incompleto ignorado.")
        return False

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
            raise ValueError("Previsao invalida")

        if valores[7] not in (0, 1):
            raise ValueError("Estado da bomba invalido")

        escritor.writerow([
            datetime.now().astimezone().isoformat(
                timespec="seconds"
            ),
            *valores
        ])

        return True

    except ValueError:
        print("Registro numerico invalido.")
        return False


def main():
    PASTA_DADOS.mkdir(
        parents=True,
        exist_ok=True
    )

    novo = (
        not ARQUIVO.exists()
        or ARQUIVO.stat().st_size == 0
    )

    print("================================")
    print(" ArabicaSense - COLETA DE DADOS")
    print("================================")
    print(f"Arquivo: {ARQUIVO}")
    print(f"Limite: {MAX_REGISTROS} registros")
    print("Para interromper: Ctrl+C")

    total = 0

    with open(
        ARQUIVO,
        "a",
        newline="",
        encoding="utf-8"
    ) as arquivo:

        escritor = csv.writer(arquivo)

        if novo:
            escritor.writerow(COLUNAS)

        with serial.serial_for_url(
            PORTA,
            baudrate=BAUDRATE,
            timeout=3
        ) as conexao:

            print("\nConectado ao ESP32 virtual.")

            while total < MAX_REGISTROS:
                linha = conexao.readline().decode(
                    "utf-8",
                    errors="replace"
                ).strip()

                if salvar_registro(linha, escritor):
                    total += 1
                    arquivo.flush()

                    print(
                        f"Registro {total}/{MAX_REGISTROS}"
                    )

    print("\nColeta concluida!")
    print(f"Total registrado: {total}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nColeta interrompida pelo usuario.")
    except (serial.SerialException, OSError) as erro:
        print(f"\nErro de comunicacao: {erro}")
        sys.exit(1)
