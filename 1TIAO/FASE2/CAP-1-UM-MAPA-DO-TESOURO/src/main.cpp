
#include <Arduino.h>
#include <DHTesp.h>

// ------------------------------------------
// FarmTech Solutions - ArabicaSense
// FIAP - FASE 2
// ------------------------------------------

// Sensores
#define PIN_N     18
#define PIN_P     19
#define PIN_K     21
#define PIN_PH    34
#define PIN_DHT   15
#define PIN_RELE  26

// Parametros da simulacao
const float PH_MIN = 5.5;
const float PH_MAX = 6.0;

const float UMIDADE_LIGAR = 40.0;
const float UMIDADE_DESLIGAR = 45.0;

// Rele validado no Wokwi
const int RELE_LIGADO = HIGH;
const int RELE_DESLIGADO = LOW;

DHTesp dhtSensor;

// Estados do sistema
bool bombaLigada = false;

// -1 = Previsao indisponivel
//  0 = Sem bloqueio por chuva
//  1 = Chuva significativa prevista
int chuvaPrevista = -1;

// Controle do rele
void controlarBomba(bool ligar) {
  bombaLigada = ligar;

  digitalWrite(
    PIN_RELE,
    ligar ? RELE_LIGADO : RELE_DESLIGADO
  );
}

// Recebe dados meteorologicos pelo Serial
void processarComando(String comando) {

  comando.trim();
  comando.toUpperCase();

  if (comando == "CHUVA_PREVISTA=1") {
    chuvaPrevista = 1;
    controlarBomba(false);

    Serial.println();
    Serial.println("[METEO] Chuva prevista!");
    Serial.println("[METEO] Irrigacao bloqueada.");

  } else if (comando == "CHUVA_PREVISTA=0") {
    chuvaPrevista = 0;

    Serial.println();
    Serial.println("[METEO] Sem bloqueio por chuva.");
    Serial.println("[METEO] Avaliar umidade.");

  } else if (
    comando == "CHUVA_PREVISTA=INDEFINIDA"
  ) {
    chuvaPrevista = -1;
    controlarBomba(false);

    Serial.println();
    Serial.println("[METEO] Previsao indisponivel.");
    Serial.println("[METEO] Bomba desligada.");

  } else if (comando.length() > 0) {
    Serial.println("[ERRO] Comando desconhecido.");
  }
}

void setup() {

  Serial.begin(115200);
  Serial.setTimeout(100);

  pinMode(PIN_N, INPUT_PULLUP);
  pinMode(PIN_P, INPUT_PULLUP);
  pinMode(PIN_K, INPUT_PULLUP);

  analogReadResolution(12);

  dhtSensor.setup(PIN_DHT, DHTesp::DHT22);

  digitalWrite(PIN_RELE, RELE_DESLIGADO);
  pinMode(PIN_RELE, OUTPUT);

  controlarBomba(false);

  delay(1000);

  Serial.println();
  Serial.println("------------------------------");
  Serial.println(" FARMTECH SOLUTIONS");
  Serial.println(" ArabicaSense");
  Serial.println(" Sitio Alto da Serra");
  Serial.println(" Manhuacu/MG");
  Serial.println("------------------------------");

  Serial.println("Aguardando previsao do Python.");
  Serial.println("Comandos aceitos:");
  Serial.println("CHUVA_PREVISTA=0");
  Serial.println("CHUVA_PREVISTA=1");
  Serial.println("CHUVA_PREVISTA=INDEFINIDA");
}

void loop() {

  // 1. Receber comandos do Python
  if (Serial.available() > 0) {
    String comando = Serial.readStringUntil('\n');
    processarComando(comando);
  }

  // 2. Ler nutrientes NPK
  bool n = digitalRead(PIN_N) == LOW;
  bool p = digitalRead(PIN_P) == LOW;
  bool k = digitalRead(PIN_K) == LOW;

  float nitrogenio = n ? 29.0 : 20.0;
  float fosforo = p ? 18.0 : 8.0;
  float potassio = k ? 110.0 : 35.0;

  // 3. Ler pH simulado
  int leituraLDR = analogRead(PIN_PH);
  float ph = leituraLDR * 14.0 / 4095.0;

  bool phAdequado =
    (ph >= PH_MIN && ph <= PH_MAX);

  // 4. Ler umidade simulada
  TempAndHumidity dados =
    dhtSensor.getTempAndHumidity();

  float umidade = dados.humidity;
  bool leituraValida = !isnan(umidade);

  // 5. Decisao de irrigacao
  if (!leituraValida || chuvaPrevista != 0) {

    controlarBomba(false);

  } else if (umidade < UMIDADE_LIGAR) {

    controlarBomba(true);

  } else if (umidade > UMIDADE_DESLIGAR) {

    controlarBomba(false);

  }
  // Entre 40 e 45, preserva estado anterior

  // 6. Monitoramento
  Serial.println();
  Serial.println("----->>> ArabicaSense <<<-----");

  Serial.printf(
    "N foliar: %.1f g/kg - %s\r\n",
    nitrogenio,
    n ? "ADEQUADO" : "DEFICIENTE"
  );

  Serial.printf(
    "P solo: %.1f mg/dm3 - %s\r\n",
    fosforo,
    p ? "ADEQUADO" : "DEFICIENTE"
  );

  Serial.printf(
    "K solo: %.1f mg/dm3 - %s\r\n",
    potassio,
    k ? "ADEQUADO" : "DEFICIENTE"
  );

  Serial.printf("pH simulado: %.2f\r\n", ph);

  if (!phAdequado) {
    Serial.println("ALERTA: pH Crítico, verificar!");
  }

  if (!n || !p || !k) {
    Serial.println("ALERTA: Nutricao crítica, verificar!");
  }

  if (leituraValida) {
    Serial.printf(
      "Umidade simulada: %.1f%%\r\n",
      umidade
    );
  } else {
    Serial.println("ERRO: Falha no DHT22!");
  }

  // Previsao meteorologica
  Serial.println("---[ METEOROLOGIA ]---");

  if (chuvaPrevista == 1) {
    Serial.println("Previsao: CHUVA SIGNIFICATIVA");

  } else if (chuvaPrevista == 0) {
    Serial.println("Previsao: SEM BLOQUEIO");

  } else {
    Serial.println("Previsao: INDISPONIVEL");
  }

  // Estado da irrigacao
  Serial.println("---[ IRRIGACAO ]---");

  Serial.printf(
    "Bomba: %s\r\n",
    bombaLigada ? "LIGADA" : "DESLIGADA"
  );

  if (!leituraValida) {
    Serial.println("Motivo: Falha no sensor.");
  } else if (chuvaPrevista == -1) {
    Serial.println("Motivo: Aguardando previsao.");
  } else if (chuvaPrevista == 1) {
    Serial.println("Motivo: Chuva prevista.");
  } else if (bombaLigada) {
    Serial.println("Motivo: Umidade baixa.");
  } else {
    Serial.println("Motivo: Umidade suficiente.");
  }

  Serial.println("------------------------------");


// -------------------------------------
// SAIDA ESTRUTURADA PARA ANALISE EM R
// -------------------------------------
// Prefixo identifica registros de dados entre as demais mensagens do terminal.
// 

  Serial.printf(
                "DADOS_CSV,%lu,%.1f,%.1f,%.1f,%.2f,%.1f,%d,%d\r\n",
                millis(),
                nitrogenio,
                fosforo,
                potassio,
                ph,
                leituraValida ? umidade : -1.0,
                chuvaPrevista,
                bombaLigada ? 1 : 0
    );

  delay(2000);
}
