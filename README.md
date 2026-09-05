# FarmTech Solutions - Fase 1

Sistema de apoio ao manejo de uma fazenda no interior de São Paulo, com duas culturas:

| Cultura | Formato do talhão | Fórmula da área | Manejo do insumo |
|---------|-------------------|-----------------|------------------|
| Cana-de-açúcar | retângulo | `comprimento x largura` | dose em **L/ha** aplicada sobre a área |
| Laranja | trapézio | `((base maior + base menor) x altura) / 2` | dose em **mL por metro de rua** |

O menu em Python cadastra os plantios, calcula área e insumo, mantém os dados em
vetores e exporta um CSV. Os scripts em R leem esse CSV para gerar estatísticas e
consultam uma API pública de meteorologia.

## Estrutura

```
farmtech/
├── python/
│   ├── main.py          menu, vetores paralelos e CRUD
│   ├── calculos.py      geometria, insumos e cadastro de culturas
│   └── validacoes.py    leitura e validação das entradas
├── r/
│   ├── estatisticas.R   média, desvio-padrão e outras medidas por cultura
│   └── clima.R          clima atual da fazenda via API Open-Meteo
├── dados/
│   └── plantios.csv     exportado pela opção 5 do menu
├── documentos/
│   └── Resumo VANTs.odt  resumo do artigo da Embrapa (Formação Social)
├── testes/
│   ├── casos_de_teste.md   casos, resultados esperados e obtidos
│   ├── executar_testes.sh  roda as três sessões automatizadas
│   ├── entrada_demo.txt    roteiro do fluxo CRUD completo
│   ├── entrada_edge.txt    roteiro de casos extremos e cancelamentos
│   ├── entrada_vazio.txt   roteiro de operações sem registros
│   ├── saida_demo.txt      evidência das sessões em Python
│   └── saida_r.txt         evidência das execuções em R
├── .gitignore
├── README.md
└── video.txt               link do vídeo de demonstração
```

## Pré-requisitos

- Python 3.10 ou superior (sem bibliotecas externas)
- R 4.x para os scripts em R (`sudo apt install r-base` ou https://cran.r-project.org)
- Opcional, para o `clima.R`: `install.packages(c("httr2", "jsonlite"))`
  (sem esses pacotes o script ainda funciona com leitura básica do R)

## Como executar

Menu principal (a partir da pasta `farmtech`):

```bash
python3 python/main.py
```

```
1 - Cadastrar plantio
2 - Listar dados e resultados
3 - Atualizar registro
4 - Excluir registro
5 - Exportar dados para CSV
6 - Sair
```

Bateria de testes automatizada (gera `dados/plantios.csv`, `testes/saida_demo.txt` e,
se o R estiver instalado, `testes/saida_r.txt`):

```bash
bash testes/executar_testes.sh
```

Estatísticas dos plantios (usa o CSV exportado):

```bash
Rscript r/estatisticas.R
```

Clima da fazenda (padrão: Ribeirão Preto/SP; aceita outras coordenadas):

```bash
Rscript r/clima.R -21.1775 -47.8103
```

## Como os dados são guardados

Os registros ficam em **vetores paralelos**: o plantio de índice `2` ocupa a posição
`2` em todos eles.

```python
ids, culturas, areas_m2, areas_ha, produtos, doses, totais_insumo_l
dimensoes, manejos, unidades_dose   # auxiliares, permitem recalcular tudo
```

Toda inclusão, alteração e exclusão passa por `adicionar()`, `substituir()` e
`remover()`, que percorrem o dicionário `VETORES`. Assim nenhum vetor fica fora de
sincronia, e `total_registros()` levanta erro se os tamanhos divergirem.

## Formato do CSV

```
id,cultura,area_m2,area_ha,produto,dose,total_insumo_l
1,cana-de-acucar,360000.0,36.0,Herbicida Tebutiurom,3.5,126.0
4,laranja,93600.0,9.36,Oleo mineral,500.0,6000.0
```

A coluna `dose` guarda o número informado pelo usuário; a unidade depende da cultura
(L/ha na cana, mL/m de rua na laranja). Por isso as estatísticas em R são feitas sobre
`area_ha` e `total_insumo_l`, que são comparáveis entre culturas.

## Trocar de cultura

As culturas ficam no dicionário `CULTURAS`, em `python/calculos.py`. Cada entrada
declara o nome, a geometria, os campos pedidos ao usuário, o tipo de manejo e o rótulo
da dose. Para trocar cana e laranja por soja e café, por exemplo, basta editar esse
dicionário: menu, validações, listagem, CSV e scripts em R continuam funcionando.
Uma geometria nova exige apenas uma função em `calculos.py` e um caso em
`calcular_area_m2()`.


## Situação atual

Tudo executado e conferido: Python 3.14.4 e R 4.5.2 (com o pacote `httr2`).

- `testes/saida_demo.txt` - três sessões do menu em Python.
- `testes/saida_r.txt` - estatísticas, cenários de erro do CSV, clima atual da fazenda e
  o comportamento do `clima.R` sem internet.
- Os números do `estatisticas.R` batem com o cálculo independente feito em Python
  (tabela em `testes/casos_de_teste.md`).

## Video

https://youtu.be/OBqYgE1e4Tc


## Fonte do resumo

JORGE, L. A. de C.; INAMASU, R. Y. *Uso de veículos aéreos não tripulados (VANT) em
Agricultura de Precisão*. In: **Agricultura de precisão: resultados de um novo olhar**.
Brasília, DF: Embrapa, 2014. cap. 8, p. 109-134.
Disponível em: https://www.alice.cnptia.embrapa.br/alice/bitstream/doc/1003485/1/CAP8.pdf
