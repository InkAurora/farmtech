#!/usr/bin/env Rscript
# ---------------------------------------------------------------------------
# FarmTech Solutions - clima atual da fazenda (API publica Open-Meteo)
#
# Documentacao: https://open-meteo.com/en/docs  (nao exige chave de API)
#
# Uso:  Rscript r/clima.R [latitude] [longitude]
# Sem argumentos usa a sede da fazenda, em Ribeirao Preto - SP.
#
# Pacotes: usa httr2 ou jsonlite quando disponiveis e, na falta dos dois,
# cai para leitura direta com R base.
# ---------------------------------------------------------------------------

LAT_PADRAO <- -21.1775   # Ribeirao Preto / SP
LON_PADRAO <- -47.8103
FUSO <- "America/Sao_Paulo"

VARIAVEIS <- c("temperature_2m", "relative_humidity_2m", "precipitation", "wind_speed_10m")

argumentos <- commandArgs(trailingOnly = TRUE)

ler_coordenada <- function(texto, padrao, nome, limite) {
  if (is.na(texto)) return(padrao)
  valor <- suppressWarnings(as.numeric(texto))
  if (is.na(valor) || abs(valor) > limite) {
    cat("Aviso: ", nome, " invalida ('", texto, "'). Usando o valor padrao.\n", sep = "")
    return(padrao)
  }
  valor
}

latitude  <- ler_coordenada(argumentos[1], LAT_PADRAO, "latitude", 90)
longitude <- ler_coordenada(argumentos[2], LON_PADRAO, "longitude", 180)

url_consulta <- sprintf(
  "https://api.open-meteo.com/v1/forecast?latitude=%s&longitude=%s&current=%s&timezone=%s",
  format(latitude, digits = 6), format(longitude, digits = 6),
  paste(VARIAVEIS, collapse = ","), utils::URLencode(FUSO, reserved = TRUE)
)

tem_pacote <- function(nome) requireNamespace(nome, quietly = TRUE)

# ------------------------------------------------------------------ coleta
baixar_com_httr2 <- function(endereco) {
  resposta <- httr2::req_perform(httr2::req_timeout(httr2::request(endereco), 20))
  if (httr2::resp_status(resposta) != 200) {
    stop("a API respondeu com status ", httr2::resp_status(resposta))
  }
  httr2::resp_body_json(resposta, simplifyVector = TRUE)
}

baixar_com_jsonlite <- function(endereco) {
  jsonlite::fromJSON(endereco)
}

# Ultimo recurso: le o texto e extrai os numeros do bloco "current".
extrair_numero <- function(texto, chave) {
  padrao <- paste0('"', chave, '"[[:space:]]*:[[:space:]]*(-?[0-9]+\\.?[0-9]*)')
  achado <- regmatches(texto, regexec(padrao, texto))[[1]]
  if (length(achado) < 2) return(NA_real_)
  as.numeric(achado[2])
}

baixar_com_base <- function(endereco) {
  conexao <- url(endereco, open = "r")
  on.exit(close(conexao), add = TRUE)
  texto <- paste(readLines(conexao, warn = FALSE), collapse = "")
  atual <- list()
  for (variavel in VARIAVEIS) atual[[variavel]] <- extrair_numero(texto, variavel)
  list(current = atual, current_units = list())
}

coletar <- function(endereco) {
  if (tem_pacote("httr2"))    return(list(dados = baixar_com_httr2(endereco),    via = "httr2"))
  if (tem_pacote("jsonlite")) return(list(dados = baixar_com_jsonlite(endereco), via = "jsonlite"))
  cat("Aviso: pacotes httr2/jsonlite nao instalados; usando leitura basica.\n")
  cat("       Para a versao completa: install.packages(c(\"httr2\", \"jsonlite\"))\n")
  list(dados = baixar_com_base(endereco), via = "R base")
}

resposta <- tryCatch(
  coletar(url_consulta),
  error = function(e) {
    cat("\nNao foi possivel consultar a previsao do tempo.\n")
    cat("Motivo: ", conditionMessage(e), "\n", sep = "")
    cat("Verifique a conexao com a internet e tente novamente.\n\n")
    quit(status = 1)
  }
)

dados <- resposta$dados
if (is.null(dados$current)) {
  cat("\nResposta da API em formato inesperado (bloco 'current' ausente).\n\n")
  quit(status = 1)
}

# --------------------------------------------------------------- exibicao
valor_ou_na <- function(bloco, chave) {
  if (is.null(bloco) || !(chave %in% names(bloco))) return(NA_real_)
  valor <- bloco[[chave]]
  if (length(valor) == 0) return(NA_real_)
  suppressWarnings(as.numeric(valor[1]))
}

unidade <- function(bloco, chave, padrao) {
  if (is.null(bloco) || !(chave %in% names(bloco))) return(padrao)
  valor <- bloco[[chave]]
  if (length(valor) == 0) return(padrao)
  as.character(valor[1])
}

mostrar <- function(rotulo, valor, unidade_medida) {
  if (is.na(valor)) {
    cat(sprintf("%-14s n/d (valor nao informado pela API)\n", paste0(rotulo, ":")))
  } else {
    cat(sprintf("%-14s %s %s\n", paste0(rotulo, ":"),
                formatC(valor, format = "f", digits = 1, decimal.mark = ","),
                unidade_medida))
  }
}

atual    <- dados$current
unidades <- dados$current_units

cat("\n==============================\n")
cat("Clima da fazenda\n")
cat("==============================\n")
cat(sprintf("Coordenadas:   %.4f, %.4f\n", latitude, longitude))
if (!is.null(atual$time)) cat("Leitura:       ", as.character(atual$time[1]), "\n", sep = "")
mostrar("Temperatura",  valor_ou_na(atual, "temperature_2m"),       unidade(unidades, "temperature_2m", "C"))
mostrar("Umidade",      valor_ou_na(atual, "relative_humidity_2m"), unidade(unidades, "relative_humidity_2m", "%"))
mostrar("Precipitacao", valor_ou_na(atual, "precipitation"),        unidade(unidades, "precipitation", "mm"))
mostrar("Vento",        valor_ou_na(atual, "wind_speed_10m"),       unidade(unidades, "wind_speed_10m", "km/h"))
cat("------------------------------\n")
cat("Fonte: Open-Meteo (", resposta$via, ")\n", sep = "")

chuva <- valor_ou_na(atual, "precipitation")
vento <- valor_ou_na(atual, "wind_speed_10m")
if (!is.na(chuva) && !is.na(vento)) {
  if (chuva > 0 || vento > 10) {
    cat("Recomendacao: adiar a pulverizacao (chuva no momento ou vento acima de 10 km/h).\n")
  } else {
    cat("Recomendacao: condicoes adequadas para pulverizacao.\n")
  }
}
cat("\n")
