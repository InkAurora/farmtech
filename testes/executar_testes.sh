#!/usr/bin/env bash
# Roda as três sessões de teste sem interação e junta as evidências em
# testes/saida_demo.txt. Executar a partir de qualquer diretório.
set -u
cd "$(dirname "$0")/.."
# arquivos auxiliares com caminho fixo: mantem saida_r.txt igual a cada execucao
TMPDIR_TESTE="testes/tmp"
mkdir -p "$TMPDIR_TESTE"
trap 'rm -rf "$TMPDIR_TESTE"' EXIT
rm -f dados/plantios.csv
{
  echo "########## SESSÃO 1 - CRUD completo + validações (entrada_demo.txt) ##########"
  python3 python/main.py < testes/entrada_demo.txt
  echo
  echo "########## SESSÃO 2 - operações com vetores vazios (entrada_vazio.txt) ##########"
  python3 python/main.py < testes/entrada_vazio.txt
  echo
  echo "########## SESSÃO 3 - recarga do CSV e cancelamentos (entrada_edge.txt) ##########"
  python3 python/main.py < testes/entrada_edge.txt
} > testes/saida_demo.txt 2>&1
echo "Evidências gravadas em testes/saida_demo.txt"
echo "CSV gerado:"
cat dados/plantios.csv

if command -v Rscript >/dev/null 2>&1; then
  {
    echo "########## estatisticas.R - CSV completo ##########"
    Rscript r/estatisticas.R
    echo
    echo "########## estatisticas.R - cultura com um unico registro ##########"
    # cabecalho + 2 registros de cana + 1 de laranja: sd() da laranja vira NA
    { head -3 dados/plantios.csv; sed -n '5p' dados/plantios.csv; } > "$TMPDIR_TESTE/um_registro.csv"
    Rscript r/estatisticas.R "$TMPDIR_TESTE/um_registro.csv"
    echo
    echo "########## estatisticas.R - arquivo inexistente ##########"
    Rscript r/estatisticas.R "$TMPDIR_TESTE/nao_existe.csv"
    echo
    echo "########## clima.R - clima atual da fazenda ##########"
    Rscript r/clima.R
    echo
    echo "########## clima.R - sem acesso a internet ##########"
    http_proxy=http://127.0.0.1:9 https_proxy=http://127.0.0.1:9 Rscript r/clima.R
  } > testes/saida_r.txt 2>&1
  echo "Evidências dos scripts em R gravadas em testes/saida_r.txt"
else
  echo "Rscript não encontrado: a parte em R não foi executada."
  echo "Instale com 'sudo apt install r-base' e rode este script de novo."
fi
