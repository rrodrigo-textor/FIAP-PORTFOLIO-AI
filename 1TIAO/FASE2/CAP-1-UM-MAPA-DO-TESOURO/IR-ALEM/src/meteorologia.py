"""ArabicaSense 

Consulta a previsão meteorológica para a sede cadastrada em config_fazenda.json.
Usa apenas a biblioteca padrao de Python. A regra de bloqueio por enquanto é somente 
didática, não uma recomendação agronômica para acionamento de irrigação real.
"""

import argparse
import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

BASE = Path(__file__).resolve().parent
CONFIG_PATH = BASE / "config_fazenda.json"
SAIDA_PATH = BASE / "dados" / "previsao_atual.json"

ESTADOS = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapa", 
    "AM": "Amazonas", "BA": "Bahia", "CE": "Ceara", 
    "DF": "Distrito Federal", "ES": "Espirito Santo", 
    "GO": "Goias", "MA": "Maranhao", "MT": "Mato Grosso", 
    "MS": "Mato Grosso do Sul", "MG": "Minas Gerais", 
    "PA": "Para", "PB": "Paraiba", "PR": "Parana", 
    "PE": "Pernambuco", "PI": "Piaui", "RJ": "Rio de Janeiro", 
    "RN": "Rio Grande do Norte", "RS": "Rio Grande do Sul", 
    "RO": "Rondonia", "RR": "Roraima", "SC": "Santa Catarina", 
    "SP": "Sao Paulo", "SE": "Sergipe", "TO": "Tocantins",
}

def normalizar(texto):
    sem_acentos = "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )
    return sem_acentos.strip().casefold()


def carregar_config():
    with CONFIG_PATH.open("r", encoding="utf-8") as arq:
        config = json.load(arq)
    sede = config["propriedade"]["localizacao"]["sede"]
    lat, lon = float(sede["latitude"]), float(sede["longitude"])
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Latitude ou longitude invalida em config_fazenda.json")
    return config


def consultar_json(url_base, parametros):
    url = url_base + "?" + urlencode(parametros)
    with urlopen(url, timeout=20) as resposta:
        dados = json.load(resposta)
    if dados.get("error"):
        raise ValueError(dados.get("reason", "Erro na API"))
    return dados


def selecionar_municipio(texto):
    """Uma entrada Município/UF unica evita menu; ambiguidades exibem opções."""
    partes = re.split(r"\s*[/,]\s*", texto.strip(), maxsplit=1)
    nome = partes[0].strip()
    uf = partes[1].strip().upper() if len(partes) == 2 else None
    if not nome:
        raise ValueError("Nome de município vazio")
    if uf and uf not in ESTADOS:
        raise ValueError(f"UF invalida: {uf}")

    dados = consultar_json(
        "https://geocoding-api.open-meteo.com/v1/search",
        {"name": nome, "count": 100, "countryCode": "BR", "language": "pt"},
    )
    locais = dados.get("results", [])
    exatos = [l for l in locais if normalizar(l["name"]) == normalizar(nome)]
    if uf:
        estado = normalizar(ESTADOS[uf])
        exatos = [l for l in exatos if normalizar(l.get("admin1", "")) == estado]
        if not exatos:
            raise ValueError(f"Não foi encontrado o município: {nome}/{uf}")
        locais = exatos
    else:
        locais = exatos or locais

    if not locais:
        raise ValueError("Município não encontrado")
    if len(locais) == 1:
        return {
            "nome": locais[0]["name"],
            "uf": uf,
            "latitude": locais[0]["latitude"],
            "longitude": locais[0]["longitude"],
            "tipo": "centro_municipio",
        }

    print("\nMunicipios encontrados:")
    for i, local in enumerate(locais, 1):
        print(f"  {i} - {local['name']} / {local.get('admin1', 'Estado desconhecido')}")
    escolha = input("Escolha um numero: ").strip()
    if not escolha.isdigit() or not (1 <= int(escolha) <= len(locais)):
        raise ValueError("Opcao de municipio invalida")
    local = locais[int(escolha) - 1]
    return {
        "nome": local["name"], "uf": uf,
        "latitude": local["latitude"], "longitude": local["longitude"],
        "tipo": "centro_municipio",
    }


def obter_local(config, entrada):
    local = config["propriedade"]["localizacao"]
    if not entrada.strip():
        return {
            "nome": config["propriedade"]["nome"],
            "municipio": local["municipio"],
            "uf": local["uf"],
            "latitude": local["sede"]["latitude"],
            "longitude": local["sede"]["longitude"],
            "tipo": "sede_propriedade",
        }
    return selecionar_municipio(entrada)


def consultar_previsao(local, config):
    meteo = config["meteorologia"]
    horas = int(meteo["horas_previsao"])
    if not 1 <= horas <= 168:
        raise ValueError("horas_previsao deve estar entre 1 e 168")
    dados = consultar_json(
        "https://api.open-meteo.com/v1/forecast",
        {
            "latitude": local["latitude"],
            "longitude": local["longitude"],
            "hourly": "precipitation,precipitation_probability",
            "forecast_hours": horas,
            "timezone": "America/Sao_Paulo",
        },
    )
    hourly = dados["hourly"]
    precipitacao = hourly["precipitation"]
    prob = hourly["precipitation_probability"]
    horarios = hourly["time"]
    if len(precipitacao) != horas or len(prob) != horas or len(horarios) != horas:
        raise ValueError("API retornou série horária incompleta")
    if any(v is None for v in precipitacao) or any(v is None for v in prob):
        raise ValueError("API retornou dados meteorológicos faltantes")

    chuva = sum(float(v) for v in precipitacao)
    prob_max = max(float(v) for v in prob)
    bloquear = (
        chuva >= float(meteo["chuva_acumulada_minima_mm"])
        and prob_max >= float(meteo["probabilidade_horaria_maxima_minima_pct"])
    )
    return {
        "status": "ok",
        "projeto": config["projeto"]["nome"],
        "consultado_em": datetime.now().astimezone().isoformat(timespec="seconds"),
        "local": local,
        "fonte": "Open-Meteo",
        "inicio_previsao": horarios[0],
        "fim_previsao": horarios[-1],
        "horas_previsao": horas,
        "chuva_acumulada_mm": round(chuva, 2),
        "maior_probabilidade_horaria_pct": round(prob_max, 1),
        "chuva_prevista": int(bloquear),
        "regra_demonstrativa": meteo["regra"],
    }


def salvar_resultado(resultado):
    SAIDA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SAIDA_PATH.open("w", encoding="utf-8") as arq:
        json.dump(resultado, arq, indent=2, ensure_ascii=False)
        arq.write("\n")


def main():
    parser = argparse.ArgumentParser(description="Previsão meteorológica ArabicaSense")
    parser.add_argument("--automatico", action="store_true", help="Usar a sede sem perguntas")
    parser.add_argument("--municipio", help="Testar outra cidade, ex: Rio de Janeiro/RJ")
    args = parser.parse_args()
    config = carregar_config()
    local_cfg = config["propriedade"]["localizacao"]

    print("=" * 45)
    print("FarmTech Solutions - ArabicaSense")
    print("---- >>> Previsão de Chuva <<<----")
    print("=" * 45)
    print(f"Propriedade: {config['propriedade']['nome']}")
    print(f"Localização: {local_cfg['municipio']}/{local_cfg['uf']}")
    print(f"Área total aproximada: {config['propriedade']['area_total_estimada_ha']} ha")

    if args.automatico and args.municipio:
        parser.error("Use --automatico OU --municipio")
    if args.automatico:
        entrada = ""
    elif args.municipio:
        entrada = args.municipio
    else:
        entrada = input("\nEnter = sede do sitio | ou digite Municipio/UF: ").strip()

    local = obter_local(config, entrada)
    print(f"\nPonto consultado: {local['nome']} ({local['tipo']})")
    print(f"Latitude: {local['latitude']}; Longitude: {local['longitude']}")

    try:
        resultado = consultar_previsao(local, config)
    except (HTTPError, URLError, TimeoutError, ValueError, KeyError, TypeError) as erro:
        # Nunca converte falha de consulta em CHUVA_PREVISTA=0.
        salvar_resultado({
            "status": "indisponivel", "local": local,
            "consultado_em": datetime.now().astimezone().isoformat(timespec="seconds"),
            "chuva_prevista": None,
            "erro": str(erro),
        })
        print(f"\nERRO: Previsao indisponivel: {erro}")
        print("NÃO ALTERAR o estado da irrigação com base nesta consulta.")
        return 1

    salvar_resultado(resultado)
    print("\n-------->>> PREVISAO METEOROLOGICA <<<--------")
    print(f"Chuva acumulada prevista: {resultado['chuva_acumulada_mm']:.1f} mm")
    print(f"Maior probabilidade horária: {resultado['maior_probabilidade_horaria_pct']:.0f}%")
    print(f"Horas avaliadas: {resultado['horas_previsao']}")
    print("\n----->>> Decisão Climática <<<-----")

    if resultado["chuva_prevista"]:
        print("Recomendação demonstrativa: SUSPENDER irrigacao.")
    else:
        print("Sem bloqueio climático; avaliar umidade no ESP32.")

    print(f"CHUVA_PREVISTA={resultado['chuva_prevista']}")
    print(f"Resultado salvo em: {SAIDA_PATH}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as erro:
        print(f"[ERRO DE CONFIGURAÇÃO]: {erro}")
        raise SystemExit(1)
