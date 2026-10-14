
import sys
import time
import serial

# ArabicaSense - FIAP Fase 2
# Envio de comandos ao ESP32 virtual

PORTA = "rfc2217://localhost:4000"

COMANDOS_VALIDOS = {
    "CHUVA_PREVISTA=0",
    "CHUVA_PREVISTA=1",
    "CHUVA_PREVISTA=INDEFINIDA"
}

if len(sys.argv) != 2:
    print("Uso: enviar_serial.py CHUVA_PREVISTA=1")
    sys.exit(1)

comando = sys.argv[1].strip().upper()

if comando not in COMANDOS_VALIDOS:
    print("ERRO: Comando invalido.")
    sys.exit(1)

try:
    with serial.serial_for_url(
        PORTA,
        baudrate=115200,
        timeout=2
    ) as conexao:

        time.sleep(1)

        conexao.write(
            (comando + "\n").encode("ascii")
        )

        conexao.flush()
        time.sleep(0.5)

        print(f"Comando enviado: {comando}")

except (serial.SerialException, OSError) as erro:
    print(f"Erro na comunicacao: {erro}")
