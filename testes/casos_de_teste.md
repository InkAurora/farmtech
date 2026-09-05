# Casos de teste - FarmTech Solutions

Ambiente da bateria de testes: Python 3.14.4 e R 4.5.2 (pacote httr2 disponível) em Linux.
Todos os cálculos foram conferidos "na mão" antes de comparar com a saída do programa.

## Como reproduzir

```bash
bash testes/executar_testes.sh
```

O script roda três sessões não interativas e grava tudo em
[`saida_demo.txt`](saida_demo.txt):

| Sessão | Roteiro | O que exercita |
|--------|---------|----------------|
| 1 | [`entrada_demo.txt`](entrada_demo.txt) | cadastro das duas culturas, listagem, atualização, exclusão, exportação e validações |
| 2 | [`entrada_vazio.txt`](entrada_vazio.txt) | listar, exportar, atualizar e excluir com os vetores vazios |
| 3 | [`entrada_edge.txt`](entrada_edge.txt) | recarga do CSV, manutenção de valores com ENTER e cancelamentos |

Quando o `Rscript` está instalado, o mesmo script executa os cenários em R e grava
[`saida_r.txt`](saida_r.txt).

Para rodar o menu manualmente: `python3 python/main.py`.

## 1. Cálculo de área e de insumo

| # | Cultura | Entradas | Conta esperada | Resultado obtido | Situação |
|---|---------|----------|----------------|------------------|----------|
| 1.1 | Cana (retângulo) | 800 m x 450 m; 3,5 L/ha | 800 x 450 = 360.000 m²; ÷10.000 = 36 ha; 36 x 3,5 | 360.000,00 m² / 36,00 ha / 126,00 L | OK (sessão 1) |
| 1.2 | Cana (retângulo) | 1.250 m x 600 m; 0,9 L/ha | 750.000 m²; 75 ha; 75 x 0,9 | 750.000,00 m² / 75,00 ha / 67,50 L | OK (sessão 1) |
| 1.3 | Laranja (trapézio) | bases 420 m e 300 m, altura 260 m; 48 ruas de 250 m; 500 mL/m | (420+300) x 260 ÷ 2 = 93.600 m²; 48 x 250 = 12.000 m; 12.000 x 500 ÷ 1.000 | 93.600,00 m² / 9,36 ha / 6.000,00 L | OK (sessão 1) |
| 1.4 | Laranja (trapézio) | bases 380 m e 260 m, altura 240 m; 40 ruas de 230 m; 300 mL/m | 76.800 m²; 9.200 m; 9.200 x 300 ÷ 1.000 | 76.800,00 m² / 7,68 ha / 2.760,00 L | OK (sessão 1) |
| 1.5 | Recálculo após update | cana de 620x380 passa para 650x400, dose 4 L/ha | 260.000 m²; 26 ha; 26 x 4 | 260.000,00 m² / 26,00 ha / 104,00 L | OK (sessão 1) |

## 2. Menu e vetores (CRUD)

| # | Ação | Passos | Resultado esperado | Situação |
|---|------|--------|--------------------|----------|
| 2.1 | Cadastrar | opção 1 -> cultura -> dimensões -> produto -> dose | registro entra na mesma posição dos 10 vetores e o resumo é exibido | OK (sessão 1) |
| 2.2 | Listar sem dados | opção 2 com os vetores vazios | "Nenhum plantio cadastrado ainda. Use a opção 1 do menu." | OK (sessão 2) |
| 2.3 | Listar | opção 2 com 6 registros | tabela com índice, ID, valores com 2 casas decimais e resumo por cultura | OK (sessão 1) |
| 2.4 | Atualizar dimensões | opção 3 -> índice 1 -> submenu 1 -> 650 e 400 | área e insumo recalculados (ver caso 1.5) | OK (sessão 1) |
| 2.5 | Manter valor com ENTER | opção 3 -> submenu 2 -> ENTER no produto e na dose | valores entre colchetes são preservados | OK (sessão 3) |
| 2.6 | Excluir confirmando | opção 4 -> índice 5 -> "s" | registro sai de todos os vetores; total cai de 6 para 5 | OK (sessão 1) |
| 2.7 | Excluir cancelando | opção 4 -> índice 0 -> "n" | "Exclusão cancelada"; nada é removido | OK (sessão 3) |
| 2.8 | Cancelar pelo índice | opção 4 -> ENTER | "Exclusão cancelada" | OK (sessão 3) |
| 2.9 | Atualizar/excluir sem dados | opções 3 e 4 com vetores vazios | aviso de vetores vazios, sem erro | OK (sessão 2) |
| 2.10 | Sair | opção 6 | oferece exportar (se houver dados) e encerra o laço `while` | OK (sessões 1 a 3) |
| 2.11 | Consistência dos vetores | após cada operação | `total_registros()` compara o tamanho de todos os vetores e levanta erro se divergirem | OK (executado a cada opção) |

## 3. Validações

| # | Entrada inválida | Onde | Mensagem esperada | Situação |
|---|------------------|------|-------------------|----------|
| 3.1 | `9` | opção do menu | "Opção inválida. Escolha uma entre: 1, 2, 3, 4, 5, 6." | OK (sessão 1) |
| 3.2 | `abc` | comprimento do talhão | "Valor inválido. Use apenas números" (try/except) | OK (sessão 1) |
| 3.3 | `-100` | comprimento do talhão | "O valor precisa ser maior que 0.00" | OK (sessão 1) |
| 3.4 | `0` | dose | "O valor precisa ser maior que 0.00" | OK (sessão 3) |
| 3.5 | `48,5` | quantidade de ruas | "Digite um número inteiro (sem casas decimais)" | OK (sessão 1) |
| 3.6 | `99` | índice para atualizar | "Índice inexistente. Use um valor entre 0 e 5." | OK (sessão 1) |
| 3.7 | `3,5` | dose | vírgula aceita como separador decimal (3,5 = 3.5) | OK (sessão 1) |
| 3.8 | `2`, `5`, `6` | confirmação s/n | "Responda com 's' ou 'n'" | OK (verificado em execução manual) |
| 3.9 | fim de entrada (Ctrl+D) | qualquer pergunta | "Entrada encerrada. Encerrando o programa." sem traceback | OK (verificado em execução manual) |

## 4. Exportação e integração com R

Evidência dos scripts em R: [`saida_r.txt`](saida_r.txt) (gerado pelo mesmo
`executar_testes.sh` quando o `Rscript` está disponível).

| # | Ação | Resultado esperado | Situação |
|---|------|--------------------|----------|
| 4.1 | Opção 5 com registros | gera `dados/plantios.csv` com o cabeçalho `id,cultura,area_m2,area_ha,produto,dose,total_insumo_l` | OK (sessão 1) |
| 4.2 | Opção 5 sem registros | avisa que não há dados e não escreve o arquivo | OK (sessão 2) |
| 4.3 | Reabrir o programa | pergunta se deseja carregar o CSV e recarrega os 5 registros | OK (sessão 3) |
| 4.4 | `Rscript r/estatisticas.R` | estatísticas por cultura iguais à tabela abaixo | OK (R 4.5.2) |
| 4.5 | Cultura com um único registro | desvio-padrão exibido como `n/d` mais aviso sobre `sd()` | OK |
| 4.6 | CSV inexistente | mensagem orientando gerar o arquivo pela opção 5; `exit 1` | OK |
| 4.7 | Caminho informado que não existe | "ERRO: arquivo informado nao existe: ..."; `exit 1` | OK |
| 4.8 | CSV só com o cabeçalho | "nao possui registros. Cadastre plantios no menu em Python"; `exit 0` | OK |
| 4.9 | `Rscript r/clima.R` | bloco "Clima da fazenda" com temperatura, umidade, precipitação e vento | OK (via httr2) |
| 4.10 | `r/clima.R` sem internet | "Nao foi possivel consultar a previsao do tempo"; `exit 1` | OK (simulado com proxy inválido) |
| 4.11 | `Rscript r/clima.R abc 200` | avisa que latitude e longitude são inválidas e usa as coordenadas padrão | OK |

### Valores conferidos no caso 4.4

Calculados a partir do `dados/plantios.csv` gerado pela sessão 1. A coluna "obtido" é a
saída do `estatisticas.R`; a conferência foi feita contra o mesmo cálculo em Python
(`mean` e `sd` amostral).

| Grupo | Métrica | n | Média | Desvio-padrão | Mínimo | Mediana | Máximo | Soma |
|-------|---------|---|-------|---------------|--------|---------|--------|------|
| Cana-de-açúcar | área (ha) | 3 | 45,67 | 25,89 | 26,00 | 36,00 | 75,00 | 137,00 |
| Cana-de-açúcar | insumo (L) | 3 | 99,17 | 29,55 | 67,50 | 104,00 | 126,00 | 297,50 |
| Laranja | área (ha) | 2 | 8,52 | 1,19 | 7,68 | 8,52 | 9,36 | 17,04 |
| Laranja | insumo (L) | 2 | 4.380,00 | 2.291,03 | 2.760,00 | 4.380,00 | 6.000,00 | 8.760,00 |
| Todas | área (ha) | 5 | 30,81 | 27,38 | 7,68 | 26,00 | 75,00 | 154,04 |
| Todas | insumo (L) | 5 | 1.811,50 | 2.609,65 | 67,50 | 126,00 | 6.000,00 | 9.057,50 |

Os seis valores conferem com a saída do R registrada em `saida_r.txt`.
