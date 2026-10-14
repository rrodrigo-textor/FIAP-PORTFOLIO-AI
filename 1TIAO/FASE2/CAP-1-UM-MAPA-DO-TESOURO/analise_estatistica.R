# ------------------------------------------------------------
# FARMTECH SOLUTIONS - ArabicaSense | FIAP
# Sitio Alto da Serra - Manhuacu/MG
# ------------------------------------------------------------

if (!requireNamespace("ggplot2", quietly = TRUE)) {
  stop("Instale ggplot2: install.packages('ggplot2')")
}
library(ggplot2)

entrada <- file.path("dados", "historico_sensores.csv")
saida <- "resultados"

if (!file.exists(entrada)) 
  stop("CSV nao encontrado: execute a partir da pasta Fase2")

dir.create(saida, recursive = TRUE, showWarnings = FALSE)

# Limpa somente imagens/relatorio gerados por ESTE script; nunca apaga o CSV.
nomes_saida <- c("01_umidade.png", "02_irrigacao.png", "03_ph.png",
                 "04_npk.png", "05_meteorologia.png",
                 "06_decisoes_irrigacao.png", "relatorio_estatistico.txt")

dados <- read.csv(entrada, stringsAsFactors = FALSE,
                  fileEncoding = "UTF-8-BOM", check.names = FALSE)

colunas <- c("data_hora", "tempo_ms", "nitrogenio", "fosforo",
             "potassio", "ph", "umidade", "chuva_prevista", "bomba")

if (!all(colunas %in% names(dados))) 
  stop("CSV sem as colunas esperadas")

if (nrow(dados) == 0) stop("Historico vazio")

dados$registro <- seq_len(nrow(dados))
dados$umidade[dados$umidade == -1] <- NA_real_
dados$chuva_prevista[dados$chuva_prevista == -1] <- NA_integer_
if (any(!is.na(dados$bomba) & !dados$bomba %in% c(0,1))) stop("Estado da bomba invalido")
if (any(!is.na(dados$chuva_prevista) & !dados$chuva_prevista %in% c(0,1))) stop("Estado meteorologico invalido")

media <- function(x) if (all(is.na(x))) NA_real_ else mean(x, na.rm=TRUE)
minimo <- function(x) if (all(is.na(x))) NA_real_ else min(x, na.rm=TRUE)
maximo <- function(x) if (all(is.na(x))) NA_real_ else max(x, na.rm=TRUE)
pct <- function(t, n) if (n == 0) NA_real_ else round(100*t/n,1)
formatar <- function(x, casas=2) ifelse(is.na(x), "indisponivel", format(round(x,casas), nsmall=casas))

# Referencias didaticas: LDR e DHT22 NAO medem solo ou pH real.
ph_ok <- !is.na(dados$ph) & dados$ph >= 5.5 & dados$ph <= 6.0
bomba_ligada <- sum(dados$bomba == 1, na.rm=TRUE)
bomba_desligada <- sum(dados$bomba == 0, na.rm=TRUE)
meteo_chuva <- sum(dados$chuva_prevista == 1, na.rm=TRUE)
meteo_sem <- sum(dados$chuva_prevista == 0, na.rm=TRUE)
meteo_indisp <- sum(is.na(dados$chuva_prevista))
npk <- data.frame(
  nutriente = c("Nitrogenio", "Fosforo", "Potassio"),
  adequada = c(sum(dados$nitrogenio == 29, na.rm=TRUE),
               sum(dados$fosforo == 18, na.rm=TRUE),
               sum(dados$potassio == 110, na.rm=TRUE))
)
npk$percentual <- 100 * npk$adequada / nrow(dados)

base_tema <- theme_minimal(base_size=12) +
  theme(plot.title=element_text(face="bold"),
        plot.subtitle=element_text(colour="grey40"))
subtitulo <- "Sitio Alto da Serra - Manhuacu/MG | Dados simulados no Wokwi"

# 1. Umidade: serie historica unica
g1 <- ggplot(dados, aes(registro, umidade)) +
  geom_line(colour="#2166AC", linewidth=.8, na.rm=TRUE) +
  geom_hline(yintercept=40, linetype="dashed", colour="#B35806") +
  geom_hline(yintercept=45, linetype="dotted", colour="#1B7837") +
  labs(title="ArabicaSense | Monitoramento da umidade",
       subtitle=paste(subtitulo,"| Referencias didaticas: 40% e 45%"),
       x="Sequencia de leituras", y="Umidade simulada (%)") + base_tema

# 2. Estado da bomba na serie completa
g2 <- ggplot(dados, aes(registro, bomba)) +
  geom_step(colour="#D95F02", linewidth=.85, na.rm=TRUE) +
  scale_y_continuous(breaks=c(0,1), labels=c("Desligada","Ligada"), limits=c(-.1,1.1)) +
  labs(title="ArabicaSense | Controle da irrigacao", subtitle=subtitulo,
       x="Sequencia de leituras", y="Bomba") + base_tema

# 3. pH representado pelo LDR
g3 <- ggplot(dados, aes(registro, ph)) +
  annotate("rect", xmin=-Inf, xmax=Inf, ymin=5.5, ymax=6,
           alpha=.14, fill="#41AB5D") +
  geom_line(colour="#238B45", linewidth=.8, na.rm=TRUE) +
  geom_hline(yintercept=c(5.5,6), linetype="dashed", colour="#238B45") +
  labs(title="ArabicaSense | Monitoramento do pH simulado",
       subtitle=paste(subtitulo,"| Referencia 5,5 a 6,0"),
       x="Sequencia de leituras", y="pH simulado pelo LDR") + base_tema

# 4. Frequencia NPK (estados binarios, nao composicao quimica)
g4 <- ggplot(npk, aes(nutriente, percentual)) +
  geom_col(fill="#2C7FB8", width=.6) +
  geom_text(aes(label=sprintf("%.1f%%",percentual)), vjust=-.4) +
  coord_cartesian(ylim=c(0,105)) +
  labs(title="ArabicaSense | Condicoes simuladas de NPK",
       subtitle=paste(subtitulo,"| Estados dos botoes, nao analise laboratorial"),
       x="Nutriente", y="Leituras adequadas (%)") + base_tema

# 5. Distribuicao dos estados da previsao
meteo <- data.frame(
  estado=c("Chuva prevista", "Sem bloqueio", "Indisponivel"),
  registros=c(meteo_chuva,meteo_sem,meteo_indisp))
g5 <- ggplot(meteo, aes(reorder(estado, registros), registros)) +
  geom_col(fill="#4292C6", width=.6) +
  geom_text(aes(label=registros), hjust=-.2) +
  coord_flip() +
  scale_y_continuous(expand=expansion(mult=c(0,.15))) +
  labs(title="ArabicaSense | Condicoes meteorologicas",
       subtitle=subtitulo, x=NULL, y="Numero de leituras") + base_tema

# 6. Decisoes integradas: chuva + bomba, registro a registro
decisoes <- data.frame(
  registro=dados$registro,
  situacao=ifelse(is.na(dados$chuva_prevista), "Previsao indisponivel",
           ifelse(dados$chuva_prevista == 1, "Bloqueio por chuva",
           ifelse(dados$bomba == 1, "Irrigacao ativa", "Sem irrigacao"))))
decisoes$situacao <- factor(decisoes$situacao,
 levels=c("Previsao indisponivel","Bloqueio por chuva","Sem irrigacao","Irrigacao ativa"))
g6 <- ggplot(decisoes, aes(registro, situacao, colour=situacao)) +
  geom_point(size=1.7, alpha=.85) +
  scale_colour_manual(values=c("#777777","#3182BD","#74A9CF","#238B45"), guide="none") +
  labs(title="ArabicaSense | Historico das decisoes de irrigacao",
       subtitle=subtitulo, x="Sequencia de leituras", y="Condicao registrada") + base_tema

imagens <- list("01_umidade.png"=g1, "02_irrigacao.png"=g2,
               "03_ph.png"=g3, "04_npk.png"=g4,
               "05_meteorologia.png"=g5, "06_decisoes_irrigacao.png"=g6)
for (nome in names(imagens)) {
  ggsave(file.path(saida, nome), plot=imagens[[nome]],
         width=11, height=6, dpi=160)
}

relatorio <- c(
 "ARABICASENSE - RELATORIO ESTATISTICO CONSOLIDADO",
 "Sitio Alto da Serra - Manhuacu/MG",
 "Fonte: ESP32/Wokwi",
 "-----------------------------------------------------------",
 paste("Total de leituras:", nrow(dados)),
 paste0("Umidade: media ",formatar(media(dados$umidade)),
        "%, minima ",formatar(minimo(dados$umidade)),
        "%, maxima ",formatar(maximo(dados$umidade)),"%"),
 paste0("pH simulado medio: ",formatar(media(dados$ph))),
 paste("Leituras de pH na faixa 5,5 a 6,0:",sum(ph_ok)),
 paste("Bomba ligada:",bomba_ligada,"leituras (",pct(bomba_ligada,nrow(dados)),"%)"),
 paste("Bomba desligada:",bomba_desligada,"leituras"),
 paste("Previsao de chuva:",meteo_chuva,"leituras"),
 paste("Sem bloqueio meteorologico:",meteo_sem,"leituras"),
 paste("Previsao indisponivel:",meteo_indisp,"leituras"),
 paste("N adequado (estado simulado):",npk$adequada[1],"leituras"),
 paste("P adequado (estado simulado):",npk$adequada[2],"leituras"),
 paste("K adequado (estado simulado):",npk$adequada[3],"leituras"),
 "-----------------------------------------------------------",
 "O percentual de leituras com bomba ligada NAO e o tempo real de acionamento.",
  "LDR representa pH e DHT22 representa umidade do solo."
)
writeLines(relatorio, file.path(saida,"relatorio_estatistico.txt"), useBytes=TRUE)
cat(paste(relatorio, collapse="\n"),"\n")
cat("\nArquivos produzidos em:",normalizePath(saida),"\n")
