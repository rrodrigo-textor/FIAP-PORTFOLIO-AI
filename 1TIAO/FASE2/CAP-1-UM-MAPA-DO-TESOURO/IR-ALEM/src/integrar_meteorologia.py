
import re
import sys
import time
import subprocess
from pathlib import Path

import serial

# =========================================
# FARMTECH SOLUTIONS - ARABICASENSE
# FIAP
# Integracao automatica Python / ESP32
# =========================================

PASTA_PROJETO = Path(__file__).resolve().parent
SCRIPT_METEO = PASTA_PROJETO / "meteorologia.py"

PORTA_ESP32 = "rfc2217://localhost:4000"
VELOCIDADE = 115200


def obter_previsao():
    print("Consultando a previsao meteorologica...\n")

    try:
        resultado = subprocess.run(
            [sys.executable, str(SCRIPT_METEO),
             "--automatico"],
            cwd=PASTA_PROJETO,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60
        )

        print(resultado.stdout)

        if resultado.stderr:
            print(resultado.stderr)

        if resultado.returncode != 0:
            raise RuntimeError(
                "Falha na consulta meteorologica."
            )

        correspondencias = re.findall(
            r"^CHUVA_PREVISTA=([01])\s*$",
            resultado.stdout,
            flags=re.MULTILINE
        )

        if len(correspondencias) != 1:
            raise ValueError(
                "Decisao meteorologica nao identificada."
            )

        return "CHUVA_PREVISTA=" + correspondencias[0]

    except (
        subprocess.TimeoutExpired,
        OSError,
        ValueError,
        RuntimeError
    ) as erro:
        print(f"Falha na previsao: {erro}")

        # Falha segura: nao autorizar irrigacao
        return "CHUVA_PREVISTA=INDEFINIDA"


def enviar_esp32(comando):
    print(f"\nEnviando ao ESP32: {comando}")

    try:
        with serial.serial_for_url(
            PORTA_ESP32,
            baudrate=VELOCIDADE,
            timeout=2
        ) as conexao:

            time.sleep(1)

            conexao.write(
                (comando + "\n").encode("ascii")
            )

            conexao.flush()

            print("Comando transmitido ao ESP32.")

            return True

    except (serial.SerialException, OSError) as erro:
        print(f"Erro de comunicacao: {erro}")
        return False


def main():
    print("=" * 45)
    print("FARMTECH SOLUTIONS - ARABICASENSE")
    print("SITIO ALTO DA SERRA - MANHUACU/MG")
    print("INTEGRACAO METEOROLOGICA AUTOMATICA")
    print("=" * 45)

    comando = obter_previsao()

    if enviar_esp32(comando):
        print("\nTransmissao concluida.")
        print("Confira a decisao no Wokwi.")
    else:
        print("\nTransmissao nao concluida.")
        sys.exit(1)


if __name__ == "__main__":
    main()
