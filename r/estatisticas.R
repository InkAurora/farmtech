#!/usr/bin/env Rscript
# ---------------------------------------------------------------------------
# FarmTech Solutions - estatisticas dos plantios
#
# Le o arquivo dados/plantios.csv exportado pelo menu em Python e calcula, por
# cultura: media, desvio-padrao, minimo, mediana, maximo e soma da area e do
# insumo. Usa apenas R base (nenhum pacote externo).
#
# Uso:  Rscript r/estatisticas.R [caminho/para/plantios.csv]
# ---------------------------------------------------------------------------

argumentos <- commandArgs(trailingOnly = TRUE)

diretorio_script <- function() {
  alvo <- grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)
  if (length(alvo) == 0) return(getwd())
  normalizePath(dirname(sub("^--file=", "", alvo[1])))
}

localizar_csv <- function() {
  # caminho informado na linha de comando tem prioridade e nao cai para os padroes
  if (length(argumentos) > 0 && nzchar(argumentos[1])) {
    if (!file.exists(argumentos[1])) {
      cat("ERRO: arquivo informado nao existe:", argumentos[1], "\n")
      quit(status = 1)
    }
    return(argumentos[1])
  }
  raiz <- dirname(diretorio_script())
  candidatos <- c(
    file.path(raiz, "dados", "plantios.csv"),
    file.path("dados", "plantios.csv"),
    file.path("..", "dados", "plantios.csv")
  )
  for (caminho in candidatos) {
    if (nzchar(caminho) && file.exists(caminho)) return(caminho)
  }
  NULL
}

formatar <- function(valor, casas = 2) {
  if (length(valor) != 1 || is.na(valor) || !is.finite(valor)) return("n/d")
  formatC(valor, format = "f", digits = casas, big.mark = ".", decimal.mark = ",")
}

resumir <- function(valores) {
  valores <- valores[is.finite(valores)]
  list(
    n        = length(valores),
    media    = if (length(valores) >= 1) mean(valores)   else NA_real_,
    # sd() precisa de pelo menos dois valores; com um so registro devolve NA
    desvio   = if (length(valores) >= 2) sd(valores)     else NA_real_,
    minimo   = if (length(valores) >= 1) min(valores)    else NA_real_,
    mediana  = if (length(valores) >= 1) median(valores) else NA_real_,
    maximo   = if (length(valores) >= 1) max(valores)    else NA_real_,
    soma     = if (length(valores) >= 1) sum(valores)    else NA_real_
  )
}

linha <- function(rotulo, estatisticas, unidade) {
  cat(sprintf(
    "  %-12s n=%-3d media=%12s  dp=%12s  min=%12s  mediana=%12s  max=%12s  soma=%12s  %s\n",
    rotulo, estatisticas$n,
    formatar(estatisticas$media), formatar(estatisticas$desvio),
    formatar(estatisticas$minimo), formatar(estatisticas$mediana),
    formatar(estatisticas$maximo), formatar(estatisticas$soma), unidade
  ))
}

bloco <- function(titulo, dados) {
  cat("\n", titulo, " (", nrow(dados), " registro(s))\n", sep = "")
  cat(strrep("-", 118), "\n", sep = "")
  linha("Area", resumir(dados$area_ha), "ha")
  linha("Insumo", resumir(dados$total_insumo_l), "L")
  if (nrow(dados) < 2) {
    cat("  Aviso: com menos de dois registros o desvio-padrao nao e definido (sd() devolve NA).\n")
  }
}

# ------------------------------------------------------------------ leitura
caminho <- localizar_csv()
if (is.null(caminho)) {
  cat("ERRO: arquivo plantios.csv nao encontrado.\n")
  cat("Gere o arquivo pela opcao 5 do menu em Python ou informe o caminho:\n")
  cat("  Rscript r/estatisticas.R caminho/para/plantios.csv\n")
  quit(status = 1)
}

plantios <- tryCatch(
  read.csv(caminho, stringsAsFactors = FALSE, encoding = "UTF-8"),
  error = function(e) {
    cat("ERRO ao ler o CSV:", conditionMessage(e), "\n")
    quit(status = 1)
  }
)

obrigatorias <- c("id", "cultura", "area_m2", "area_ha", "produto", "dose", "total_insumo_l")
faltando <- setdiff(obrigatorias, names(plantios))
if (length(faltando) > 0) {
  cat("ERRO: colunas ausentes no CSV:", paste(faltando, collapse = ", "), "\n")
  quit(status = 1)
}

if (nrow(plantios) == 0) {
  cat("O arquivo", caminho, "nao possui registros. Cadastre plantios no menu em Python.\n")
  quit(status = 0)
}

plantios$area_ha        <- suppressWarnings(as.numeric(plantios$area_ha))
plantios$area_m2        <- suppressWarnings(as.numeric(plantios$area_m2))
plantios$total_insumo_l <- suppressWarnings(as.numeric(plantios$total_insumo_l))

invalidos <- is.na(plantios$area_ha) | is.na(plantios$total_insumo_l)
if (any(invalidos)) {
  cat("Aviso:", sum(invalidos), "linha(s) com valores nao numericos foram ignoradas.\n")
  plantios <- plantios[!invalidos, ]
}

# ----------------------------------------------------------------- relatorio
cat("\n==============================================================\n")
cat("FarmTech Solutions - Analise estatistica dos plantios\n")
cat("Arquivo: ", caminho, "\n", sep = "")
cat("==============================================================\n")

for (nome_cultura in sort(unique(plantios$cultura))) {
  bloco(toupper(nome_cultura), plantios[plantios$cultura == nome_cultura, ])
}

bloco("TODAS AS CULTURAS", plantios)

cat("\nProdutos utilizados:\n")
contagem <- table(plantios$produto)
for (produto in names(sort(contagem, decreasing = TRUE))) {
  cat(sprintf("  %-28s %d aplicacao(oes)\n", produto, contagem[[produto]]))
}
cat("\nObservacao: a coluna 'dose' mistura unidades (L/ha na cana, mL/m de rua\n")
cat("na laranja); por isso a estatistica e feita sobre area e insumo total.\n\n")
