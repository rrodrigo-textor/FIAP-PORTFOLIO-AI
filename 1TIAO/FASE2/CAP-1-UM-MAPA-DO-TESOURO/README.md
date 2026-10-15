# ArabicaSense — Monitoramento Inteligente e Gestão da Irrigação do Café Arábica

**FIAP — Graduação ON em Inteligência Artificial | 1TIAO — Fase 2**  
**Atividade:** Capítulo 1 — Um Mapa do Tesouro  
**Projeto:** FarmTech Solutions  
**Estudo de caso:** Sítio Alto da Serra — Agricultura Familiar, Manhuaçu/MG

## Identificação do grupo

**Grupo:** FarmTech Solutions

### Integrantes

- **Pedro Victor Pires** 
- **Raiane Sirlene da Silva** 
- **Rodrigo Textor de Textor** 



### Professores

- **Tutor(a):** Sabrina Otoni
- **Coordenador:** André Godoi Chiovato 

## Resumo e descrição do projeto

O **ArabicaSense** é um protótipo acadêmico de monitoramento agrícola e automação da irrigação para o café arábica. A continuidade da Fase 1 do FarmTech Solutions — que considerou café arábica e cana-de-açúcar — motivou uma pesquisa sobre regiões e propriedades associadas à agricultura familiar. Para a Fase 2, foi escolhido um estudo de caso em Manhuaçu/MG, centrado no café arábica e contextualizado com referências técnicas da Embrapa e da Emater-MG. A arquitetura reúne simulação ESP32/Wokwi, lógica de controle, integração meteorológica em Python e análise estatística em R.

**Transparência dos dados:** a fundamentação agronômica recorre a publicações reais, mas os sensores e as 220 leituras utilizadas na análise são **simulados**, não medições realizadas no sítio.

## 1. Apresentação

O **ArabicaSense** é um protótipo para monitoramento agrícola e gerenciamento inteligente da irrigação, desenvolvido para atender a Fase 2 do projeto FarmTech Solutions, da FIAP.

A proposta é investigar como tecnologias acessíveis, como microcontroladores, sensores, programação e análise de dados, podem apoiar pequenos produtores rurais nas decisões relacionadas ao cultivo do café arábica.
O sistema combina a simulação de parâmetros do solo com informações meteorológicas e regras automáticas para início da irrigação.

**Tecnologias centrais:** ESP32, Wokwi, C/C++, Python, API Open-Meteo e R.

## 2. Objetivos

### Objetivo geral

Desenvolver um protótipo de monitoramento agrícola e controle automatizado da irrigação para o café arábica, com foco na acessibilidade tecnológica para propriedades de agricultura familiar.

### Objetivos específicos

- Simular o monitoramento de nutrientes NPK.
- Representar o pH e a umidade do solo com os componentes estabelecidos na atividade.
- Implementar o acionamento automático de um relé utilizando o ESP32.
- Consultar previsões meteorológicas através do uso de API pública.
- Integrar as decisões meteorológicas ao controle de irrigação.
- Registrar um histórico das leituras e decisões do sistema.
- Aplicar métodos estatísticos utilizando R.
- Apresentar resultados por meio de gráficos e indicadores.

## 3. Contextualização da propriedade

O estudo de caso utiliza como referência o Sítio Alto da Serra, localizado em Manhuaçu, Minas Gerais.

| Característica | Informação |
|---|---|
| Propriedade | Sítio Alto da Serra |
| Município | Manhuaçu/MG |
| Área total informada | Aproximadamente 11 hectares |
| Cultura estudada | Café arábica |
| Público-alvo | Pequenos produtores e agricultura familiar |
| Tipo de implementação | Simulação acadêmica |

A localização da sede foi utilizada para parametrizar a consulta meteorológica, sem pressupor que toda a área informada esteja efetivamente cultivada com café.


## 4. Tecnologias utilizadas

| Tecnologia | Aplicação |
|---|---|
| ESP32 | Processamento e controle dos componentes |
| C/C++ e Arduino | Firmware do microcontrolador |
| PlatformIO | Compilação e gerenciamento do projeto |
| Wokwi | Simulação do circuito eletrônico |
| Python | Integração meteorológica e coleta de dados |
| Open-Meteo | API de fornecimento para previsão meteorológica |
| RFC2217 | Comunicação serial com o ESP32 virtual |
| R | Estatísticas e gráficos |
| VS Code | Desenvolvimento e execução |
| GitHub | Versionamento e disponibilização do projeto |

## 5. Arquitetura e componentes

O circuito é composto pelos seguintes elementos:

| Componente | GPIO | Função |
|---|---|---|
| Botão N | 18 | Simulação do estado do nitrogênio |
| Botão P | 19 | Simulação do estado do fósforo |
| Botão K | 21 | Simulação do estado do potássio |
| LDR | 34 | Representação analógica do pH |
| DHT22 | 15 | Representação da umidade do solo |
| Relé | 26 | Simulação do acionamento da bomba |

### Limitações dos sensores

Os botões não medem concentrações reais de nutrientes. Seus estados somente selecionam valores previamente definidos dentro do programa.

O LDR é um sensor de luminosidade, utilizado didaticamente para representar o pH. A conversão da leitura analógica para a escala de 0 a 14 não constitui uma calibração química real.

O DHT22 mede temperatura e umidade relativa do ar. Nesta atividade, a umidade informada é utilizada como substituta didática da umidade do solo.



### Imagem do circuito

![Circuito eletrônico do ArabicaSense](image.png)


## 6. Parâmetros agronômicos de referência

Para contextualizar a simulação do café arábica, foram adotados os seguintes valores ilustrativos:

| Indicador | Condição adequada simulada | Condição deficiente simulada |
|---|---|---|
| Nitrogênio foliar | 29 g/kg | 20 g/kg |
| Fósforo no solo | 18 mg/dm³ | 8 mg/dm³ |
| Potássio no solo | 110 mg/dm³ | 35 mg/dm³ |
| pH | Faixa-alvo de 5,5 a 6,0 | Fora da faixa-alvo |

As referências nutricionais dependem do estágio da cultura, das características do solo e dos métodos de análise. Os valores adotados não substituem uma recomendação de adubação.

Os alertas nutricionais são tratados separadamente das decisões de irrigação.

## 7. Controle automatizado da irrigação

O ESP32 monitora a umidade simulada e aplica regras de acionamento com histerese.

| Condição | Comportamento |
|---|---|
| Umidade inferior a 40% | Solicita irrigação |
| Umidade entre 40% e 45% | Preserva o estado anterior |
| Umidade superior a 45% | Desliga a irrigação |
| Chuva significativa prevista | Bloqueia a irrigação |
| Previsão indisponível | Mantém a bomba desligada |
| Falha no sensor de umidade | Desliga a bomba por segurança |

Os limites de umidade são demonstrativos e não representam uma prescrição agronômica de irrigação.

A histerese é utilizada para evitar alternâncias frequentes do relé nas proximidades dos limites configurados.

## 8. Ir Além 1 — Integração meteorológica com Python

O sistema utiliza a API pública Open-Meteo para consultar a previsão meteorológica da propriedade. A consulta considera a precipitação prevista nas próximas 24 horas e a maior probabilidade de chuva.

Para a demonstração, foi adotada a seguinte regra:

- Precipitação acumulada prevista igual ou superior a 3 mm.
- Probabilidade horária máxima igual ou superior a 60%.

Quando ambas as condições são atendidas, o programa sinaliza um bloqueio climático de irrigação.

Esses limites são parâmetros experimentais e não representam recomendação agronômica.

### Integração com ESP32

O Python produz os comandos:

- `CHUVA_PREVISTA=0`: sem bloqueio climático.
- `CHUVA_PREVISTA=1`: bloqueio por chuva.
- `CHUVA_PREVISTA=INDEFINIDA`: informação indisponível.

A transmissão é realizada por comunicação serial RFC2217 com o ESP32 simulado no Wokwi.

O script `integrar_meteorologia.py` executa a consulta e transmite a decisão automaticamente em cada execução. Nessa versão, ainda não está disponível o disparo automático de novas consultas pelo ESP32.

## 9. Ir Além 2 — Análise estatística em R

As informações geradas pelo ESP32 são organizadas em um `historico_sensores.csv` e posteriormente analisadas utilizando R.

Geramos uma base consolidada contendo **220 registros simulados**, com diferentes condições de umidade, pH, nutrientes, meteorologia e acionamento do relé.

### Indicadores analisados

- Média, valores mínimos e máximos da umidade.
- Comportamento do pH ao longo do monitoramento.
- Frequência dos estados nutricionais simulados.
- Acionamentos e desligamentos da bomba.
- Registros de bloqueio meteorológico.
- Relação entre condições de umidade e decisões de irrigação.

### Resultados da validação

Durante a validação funcional, foram avaliados seis cenários controlados, envolvendo umidade suficiente, solo seco, histerese, recuperação da umidade, bloqueio por chuva e retomada da irrigação.

Os 120 registros desses cenários apresentaram **zero divergências em relação ao estado esperado da bomba**.

Esse resultado corresponde a 100% de conformidade nos cenários simulados avaliados. Não constitui comprovação de desempenho equivalente em condições reais de campo.

### Gráficos estatísticos

Os resultados a seguir representam uma série histórica consolidada de **220 leituras simuladas**. No conjunto, a umidade média foi de **40,69%**; a bomba esteve ligada em **60 registros (27,3%)** e desligada em **160**. A avaliação específica de seis cenários controlados encontrou **zero divergências** nos 120 registros desses cenários.

#### Monitoramento da umidade

O gráfico apresenta a evolução da umidade simulada nas 220 leituras, destacando condições de baixa umidade e recuperação.

![Evolução da umidade simulada](resultados/01_umidade.png)

#### Controle da irrigação

O gráfico mostra os estados de acionamento e desligamento da bomba ao longo do monitoramento.

![Estados da bomba de irrigação](resultados/02_irrigacao.png)

#### Monitoramento do pH

O gráfico apresenta o pH simulado em relação à faixa de referência adotada para o cenário de café arábica.

![Monitoramento do pH simulado](resultados/03_ph.png)

#### Nutrientes NPK

O gráfico apresenta a frequência dos estados adequados e deficientes simulados de nitrogênio, fósforo e potássio.

![Estados nutricionais simulados](resultados/04_npk.png)

#### Monitoramento meteorológico

O gráfico apresenta os registros com chuva prevista, sem bloqueio meteorológico e com previsão indisponível.

![Estados meteorológicos registrados](resultados/05_meteorologia.png)

#### Decisões de irrigação

O gráfico relaciona as decisões registradas com as regras de umidade e bloqueio meteorológico.

![Decisões automatizadas de irrigação](resultados/06_decisoes_irrigacao.png)

Os gráficos representam uma única série histórica, sem separar visualmente os conjuntos de testes.



## Estrutura de pastas

A pasta desta atividade é `1TIAO/FASE2/CAP-1-UM-MAPA-DO-TESOURO/`. Os arquivos `platformio.ini`, `diagram.json` e `wokwi.toml` permanecem na raiz da atividade para preservar a execução do PlatformIO/Wokwi.

```text
CAP-1-UM-MAPA-DO-TESOURO/
├── README.md
├── image.png
├── platformio.ini
├── diagram.json
├── wokwi.toml
├── config_fazenda.json
├── src/
│   └── main.cpp
├── dados/
│   ├── historico_sensores.csv
│   └── previsao_atual.json
├── resultados/
│   ├── 01_umidade.png
│   ├── 02_irrigacao.png
│   ├── 03_ph.png
│   ├── 04_npk.png
│   ├── 05_meteorologia.png
│   ├── 06_decisoes_irrigacao.png
│   └── relatorio_estatistico.txt
├── IR-ALEM/
│   ├── src/
│   │   ├── meteorologia.py
│   │   ├── integrar_meteorologia.py
│   │   ├── enviar_serial.py
│   │   ├── coletar_dados.py
│   │   ├── coleta_experimental.py
│   │   ├── analise_estatistica.R
│   │   └── config_fazenda.json  
│   ├── data/
│   ├── docs/
│   └── notebooks/
├── data/                  
├── docs/                  
└── notebooks/             
```

**Atenção à publicação:** a estrutura acima descreve a organização esperada após a migração. Confirme com `git ls-files` e `git status` se os arquivos em `IR-ALEM/src` e a configuração foram realmente registrados e enviados ao GitHub. O histórico CSV e os resultados permanecem nos diretórios `dados/` e `resultados/`, acessados a partir da raiz da atividade.

## Links do projeto

- **[Vídeo de apresentação no YouTube](https://youtu.be/ZsISBQwn38Q)** — demonstração do ArabicaSense.
- **[Pasta desta atividade no GitHub](https://github.com/rrodrigo-textor/FIAP-PORTFOLIO-AI/tree/master/1TIAO/FASE2/CAP-1-UM-MAPA-DO-TESOURO)** — firmware, scripts, dados, gráficos e documentação.
- **[Portfólio acadêmico FIAP](https://github.com/rrodrigo-textor/FIAP-PORTFOLIO-AI)** — repositório baseado no template oficial.

## Decisões técnicas e justificativas

| Escolha | Justificativa |
|---|---|
| ESP32 + Arduino/C++ | Centralizar leituras e regras de acionamento em um microcontrolador acessível. |
| Wokwi | Permitir testes reproduzíveis em ambiente virtual, sem dependência de componentes físicos. |
| PlatformIO | Gerenciar compilação, bibliotecas e configuração do firmware. |
| Botões, LDR e DHT22 | Representar didaticamente NPK, pH e umidade, conforme escopo da simulação; não são sensores agrícolas equivalentes. |
| Histerese de 40%/45% | Reduzir alternâncias do relé nas proximidades dos limites demonstrativos. |
| Relé desativado com previsão ausente ou leitura inválida | Priorizar comportamento seguro diante de dados insuficientes. |
| Python + Open-Meteo | Consultar previsão meteorológica e transmitir a decisão ao ESP32 virtual. |
| Serial RFC2217 | Comunicar scripts Python com a simulação Wokwi em execução. |
| CSV + R | Preservar o histórico de leituras para estatísticas e gráficos reproduzíveis. |

## Como executar o código

### Pré-requisitos

- Visual Studio Code, PlatformIO e extensão Wokwi para VS Code;
- Python 3 com `pyserial` e dependências adicionais utilizadas pelo módulo meteorológico;
- R com `ggplot2`, `dplyr` e `readr` para a análise;
- acesso à internet para consultar a API Open-Meteo;
- Wokwi configurado para usar a serial RFC2217 na porta local `4000`.

### 1. Preparar o ambiente

Clone o portfólio e abra **a pasta da atividade** como projeto do PlatformIO. No PowerShell, partindo da pasta onde deseja armazenar o repositório:

```powershell
cd C:\Projetos
git clone https://github.com/rrodrigo-textor/FIAP-PORTFOLIO-AI.git
cd .\FIAP-PORTFOLIO-AI\1TIAO\FASE2\CAP-1-UM-MAPA-DO-TESOURO
python -m pip install pyserial requests
```

Se o repositório já estiver clonado, entre diretamente na pasta da atividade; não execute `git clone` outra vez na mesma pasta.

### 2. Compilar o ESP32 e iniciar o Wokwi

Com a pasta da atividade aberta no VS Code, execute o comando **PlatformIO: Build**, ou, se a CLI estiver instalada:

```powershell
platformio run
```

Abra `diagram.json` e inicie **Wokwi: Start Simulator**. Verifique o console do ESP32; a previsão começa indisponível até a transmissão da informação meteorológica.

### 3. Ir Além 1 — Meteorologia

Execute estes comandos **a partir da raiz da atividade**, com o Wokwi em funcionamento:

```powershell
python .\IR-ALEM\src\meteorologia.py --automatico
python .\IR-ALEM\src\integrar_meteorologia.py
```

**Importante:** a versão atual de `meteorologia.py` busca `config_fazenda.json` em `IR-ALEM/src/`. Verifique a presença do arquivo nesse local antes da execução. Essa cópia evita alterar o código já validado; futuramente, os caminhos poderão ser centralizados. Para testar manualmente a liberação/bloqueio climático:

```powershell
python .\IR-ALEM\src\enviar_serial.py CHUVA_PREVISTA=0
python .\IR-ALEM\src\enviar_serial.py CHUVA_PREVISTA=1
```

**Observação:** o script realiza a consulta quando é executado; não existe, nesta versão, uma consulta meteorológica sob demanda iniciada automaticamente pelo ESP32.

### 4. Ir Além 2 — Estatísticas em R

Abra um terminal R e defina o diretório de trabalho como a **raiz da atividade** (ajuste o caminho ao computador):

```r
setwd("C:/Projetos/FIAP-PORTFOLIO-AI/1TIAO/FASE2/CAP-1-UM-MAPA-DO-TESOURO")
source("IR-ALEM/src/analise_estatistica.R", encoding = "UTF-8")
```

O script lê `dados/historico_sensores.csv` e salva gráficos e relatório em `resultados/`. **Não é necessário executar scripts de coleta para reproduzir a análise dos 220 registros existentes.**

## Limitações e possibilidades de evolução

Esta entrega é uma prova de conceito acadêmica. Os limites configurados não substituem recomendações agronômicas. O histórico contém leituras simuladas; as porcentagens de acionamento do relé não equivalem a tempo efetivo de irrigação nem comprovam economia de água.

Possíveis evoluções: sensores de solo apropriados e calibrados, consulta meteorológica sob demanda, verificação de validade da previsão, limites de tempo de irrigação, aferição de vazão e validação em campo.

## Referências

- [Embrapa (2022) — Boas práticas agrícolas aplicadas à lavoura cafeeira para o estado de Minas Gerais](https://www.infoteca.cnptia.embrapa.br/infoteca/handle/doc/1148365).
- [Embrapa (2017) — Controlled irrigation and nitrogen, phosphorus and potassium fertilization affect the biochemical composition and quality of Arabica coffee beans](https://www.embrapa.br/en/busca-de-publicacoes/-/publicacao/1065059/controlled-irrigation-and-nitrogen-phosphorus-and-potassium-fertilization-affect-the-biochemical-composition-and-quality-of-arabica-coffee-beans).
- [Emater-MG — Manual do Manejo Orgânico do Cafeeiro](https://www.emater.mg.gov.br/download.do?id=87853).
- [Open-Meteo — API](https://open-meteo.com/en/docs).
- [Wokwi — Documentação](https://docs.wokwi.com/).
- [PlatformIO — Documentação](https://docs.platformio.org/).
- [R Project](https://www.r-project.org/).

## Licença e atribuição

O [template oficial FIAP-PORTFOLIO-AI](https://github.com/fiap-tutoria/FIAP-PORTFOLIO-AI) identifica a licença **Creative Commons Atribuição 4.0 Internacional (CC BY 4.0)** para o material do template. Isso não determina automaticamente a licença dos códigos autorais deste projeto; sua licença deve ser definida pelos responsáveis antes de declarar permissão de reutilização.

---

**FarmTech Solutions | FIAP — Fase 2 | Capítulo 1: Um Mapa do Tesouro**
