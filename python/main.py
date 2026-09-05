"""FarmTech Solutions - controle de plantio e de insumos.

Fazenda localizada no interior de São Paulo, com duas culturas:
  - Cana-de-açúcar: talhão retangular, dose aplicada em L/ha;
  - Laranja: talhão trapezoidal, dose aplicada em mL por metro de rua.

Os dados ficam em VETORES PARALELOS (listas de mesmo tamanho): o registro de
índice 2 ocupa a posição 2 em todos os vetores. Para nunca dessincronizar,
toda inclusão, alteração e exclusão passa pelas funções adicionar(),
substituir() e remover(), que percorrem o dicionário VETORES.

Execução:  python3 python/main.py
"""

import csv
from pathlib import Path

import calculos
import validacoes as val

# --------------------------------------------------------------- vetores
ids = []
culturas = []
areas_m2 = []
areas_ha = []
produtos = []
doses = []
totais_insumo_l = []
# vetores auxiliares (mesmo índice) - guardam o que foi digitado para permitir
# recalcular a área e o insumo em qualquer atualização
dimensoes = []
manejos = []
unidades_dose = []

VETORES = {
    "id": ids,
    "cultura": culturas,
    "area_m2": areas_m2,
    "area_ha": areas_ha,
    "produto": produtos,
    "dose": doses,
    "total_insumo_l": totais_insumo_l,
    "dimensoes": dimensoes,
    "manejo": manejos,
    "unidade_dose": unidades_dose,
}

RAIZ = Path(__file__).resolve().parent.parent
ARQUIVO_CSV = RAIZ / "dados" / "plantios.csv"
COLUNAS_CSV = ("id", "cultura", "area_m2", "area_ha", "produto", "dose", "total_insumo_l")


# ------------------------------------------------- operações nos vetores
def total_registros():
    """Quantidade de registros - todos os vetores têm o mesmo tamanho."""
    tamanhos = {len(vetor) for vetor in VETORES.values()}
    if len(tamanhos) != 1:
        raise RuntimeError("Vetores dessincronizados: " + str(tamanhos))
    return tamanhos.pop()


def proximo_id():
    """IDs sequenciais que não se repetem, mesmo após exclusões."""
    return max(ids, default=0) + 1


def adicionar(registro):
    for nome, vetor in VETORES.items():
        vetor.append(registro[nome])


def substituir(posicao, registro):
    for nome, vetor in VETORES.items():
        vetor[posicao] = registro[nome]


def remover(posicao):
    for vetor in VETORES.values():
        vetor.pop(posicao)


def obter(posicao):
    return {nome: vetor[posicao] for nome, vetor in VETORES.items()}


def vetores_vazios():
    """Avisa e devolve True quando não há nada cadastrado."""
    if total_registros() == 0:
        print("\n>> Nenhum plantio cadastrado ainda. Use a opção 1 do menu.")
        return True
    return False


# ------------------------------------------------------------ apresentação
def descrever_dimensoes(registro):
    """Texto com as medidas digitadas. Registros vindos do CSV não as têm."""
    cultura = calculos.cultura_por_chave(registro["cultura"])
    if not registro["dimensoes"]:
        return "dimensões não gravadas no CSV - informe-as ao atualizar o registro"
    partes = []
    for chave, rotulo, tipo in calculos.campos_da_cultura(cultura):
        if chave not in registro["dimensoes"]:
            continue
        valor = registro["dimensoes"][chave]
        texto = str(valor) if tipo == "int" else val.numero(valor)
        partes.append(f"{rotulo.split(' (')[0]}: {texto}")
    return " | ".join(partes)


def mostrar_registro(posicao):
    registro = obter(posicao)
    cultura = calculos.cultura_por_chave(registro["cultura"])
    print(f"\n  Índice {posicao} | ID {registro['id']} | {cultura['nome']}")
    print(f"    {descrever_dimensoes(registro)}")
    print(f"    Área: {val.numero(registro['area_m2'])} m²  "
          f"({val.numero(registro['area_ha'])} ha)")
    print(f"    Produto: {registro['produto']} | "
          f"Dose: {val.numero(registro['dose'])} {registro['unidade_dose']}")
    print(f"    Insumo total: {val.numero(registro['total_insumo_l'])} L")


def listar_registros():
    """Opção 2 do menu: tabela com os dados e os resultados calculados."""
    if vetores_vazios():
        return
    print("\n" + "=" * 100)
    print(f"{'Idx':>3} {'ID':>3} {'Cultura':<16} {'Área (m²)':>13} {'Área (ha)':>10} "
          f"{'Produto':<22} {'Dose':>12} {'Insumo (L)':>12}")
    print("-" * 100)
    for posicao in range(total_registros()):
        registro = obter(posicao)
        cultura = calculos.cultura_por_chave(registro["cultura"])
        dose = f"{val.numero(registro['dose'])} {registro['unidade_dose']}"
        print(f"{posicao:>3} {registro['id']:>3} {cultura['nome']:<16} "
              f"{val.numero(registro['area_m2']):>13} {val.numero(registro['area_ha']):>10} "
              f"{registro['produto'][:22]:<22} {dose:>12} "
              f"{val.numero(registro['total_insumo_l']):>12}")
    print("-" * 100)
    resumo_por_cultura()


def resumo_por_cultura():
    """Totais por cultura - confere com o que o R calcula depois."""
    print("Resumo por cultura:")
    for cultura in calculos.CULTURAS.values():
        posicoes = [i for i, c in enumerate(culturas) if c == cultura["chave"]]
        if not posicoes:
            continue
        area = sum(areas_ha[i] for i in posicoes)
        insumo = sum(totais_insumo_l[i] for i in posicoes)
        print(f"  {cultura['nome']:<16} {len(posicoes):>2} registro(s) | "
              f"{val.numero(area)} ha | {val.numero(insumo)} L de insumo")
    print(f"  {'TOTAL':<16} {total_registros():>2} registro(s) | "
          f"{val.numero(sum(areas_ha))} ha | {val.numero(sum(totais_insumo_l))} L de insumo")
    print("=" * 100)


# ----------------------------------------------------------------- opções
def escolher_cultura():
    print("\nCulturas disponíveis:")
    for opcao, cultura in calculos.CULTURAS.items():
        geometria = "retângulo" if cultura["geometria"] == "retangulo" else "trapézio"
        print(f"  {opcao} - {cultura['nome']} ({geometria})")
    escolha = val.ler_opcao("Escolha a cultura: ", calculos.CULTURAS.keys())
    return calculos.CULTURAS[escolha]


def ler_dimensoes(cultura, atuais=None):
    """Pede cada dimensão da cultura. Com 'atuais', ENTER mantém o valor."""
    coletadas = {}
    for campo in calculos.campos_da_cultura(cultura):
        chave = campo[0]
        padrao = atuais.get(chave) if atuais else None
        coletadas[chave] = val.ler_campo(campo, padrao=padrao)
    return coletadas


def cadastrar():
    """Opção 1: coleta os dados, calcula e grava nos vetores."""
    print("\n--- Cadastro de plantio ---")
    cultura = escolher_cultura()
    dados = ler_dimensoes(cultura)
    produto = val.ler_texto("Produto aplicado")
    dose = val.ler_float(cultura["rotulo_dose"])
    registro = calculos.montar_registro(cultura, dados, produto, dose, proximo_id())
    adicionar(registro)
    print("\n>> Plantio cadastrado com sucesso.")
    mostrar_registro(total_registros() - 1)


def atualizar():
    """Opção 3: altera um registro e recalcula área e insumo."""
    print("\n--- Atualização de registro ---")
    if vetores_vazios():
        return
    listar_registros()
    posicao = val.ler_indice("Índice do registro que deseja atualizar", total_registros())
    if posicao is None:
        print(">> Atualização cancelada.")
        return

    atual = obter(posicao)
    mostrar_registro(posicao)
    print("\nO que deseja atualizar?")
    print("  1 - Dimensões do talhão")
    print("  2 - Produto e dose")
    print("  3 - Tudo (inclusive a cultura)")
    print("  0 - Cancelar")
    escolha = val.ler_opcao("Opção: ", ("0", "1", "2", "3"))
    if escolha == "0":
        print(">> Atualização cancelada.")
        return

    print("(ENTER mantém o valor atual)")
    if escolha == "3":
        cultura = escolher_cultura()
        anteriores = atual["dimensoes"] if cultura["chave"] == atual["cultura"] else None
        if not anteriores:
            anteriores = None
        dados = ler_dimensoes(cultura, anteriores)
        produto = val.ler_texto("Produto aplicado", padrao=atual["produto"])
        dose = val.ler_float(cultura["rotulo_dose"], padrao=atual["dose"])
    else:
        cultura = calculos.cultura_por_chave(atual["cultura"])
        if escolha == "1":
            dados = ler_dimensoes(cultura, atual["dimensoes"])
            produto, dose = atual["produto"], atual["dose"]
        else:
            dados = atual["dimensoes"]
            if not dados:
                print("Registro carregado do CSV: informe novamente as medidas do talhão.")
                dados = ler_dimensoes(cultura)
            produto = val.ler_texto("Produto aplicado", padrao=atual["produto"])
            dose = val.ler_float(cultura["rotulo_dose"], padrao=atual["dose"])

    registro = calculos.montar_registro(cultura, dados, produto, dose, atual["id"])
    substituir(posicao, registro)
    print("\n>> Registro atualizado e resultados recalculados.")
    mostrar_registro(posicao)


def excluir():
    """Opção 4: remove a mesma posição de todos os vetores."""
    print("\n--- Exclusão de registro ---")
    if vetores_vazios():
        return
    listar_registros()
    posicao = val.ler_indice("Índice do registro que deseja excluir", total_registros())
    if posicao is None:
        print(">> Exclusão cancelada.")
        return
    mostrar_registro(posicao)
    if not val.confirmar("\nConfirma a exclusão deste registro?"):
        print(">> Exclusão cancelada.")
        return
    remover(posicao)
    print(f">> Registro removido. Restam {total_registros()} registro(s).")


def exportar_csv():
    """Opção 5: gera dados/plantios.csv, lido depois pelos scripts em R."""
    print("\n--- Exportação para CSV ---")
    if vetores_vazios():
        return
    ARQUIVO_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(ARQUIVO_CSV, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(COLUNAS_CSV)
        for posicao in range(total_registros()):
            registro = obter(posicao)
            escritor.writerow([
                registro["id"],
                registro["cultura"],
                round(registro["area_m2"], 4),
                round(registro["area_ha"], 4),
                registro["produto"],
                round(registro["dose"], 4),
                round(registro["total_insumo_l"], 4),
            ])
    print(f">> {total_registros()} registro(s) exportado(s) para {ARQUIVO_CSV}")
    print("   Analise com: Rscript r/estatisticas.R")


def importar_csv():
    """Recarrega os vetores a partir do CSV exportado anteriormente.

    As dimensões não vão para o CSV (ele segue o layout combinado com o R),
    então os registros importados só podem ter produto e dose atualizados.
    """
    if not ARQUIVO_CSV.exists():
        return
    try:
        with open(ARQUIVO_CSV, newline="", encoding="utf-8") as arquivo:
            linhas = list(csv.DictReader(arquivo))
    except OSError as erro:
        print(f"!! Não foi possível ler o CSV anterior: {erro}")
        return
    for linha in linhas:
        try:
            cultura = calculos.cultura_por_chave(linha["cultura"])
            area_m2 = float(linha["area_m2"])
            adicionar({
                "id": int(linha["id"]),
                "cultura": cultura["chave"],
                "area_m2": area_m2,
                "area_ha": float(linha["area_ha"]),
                "produto": linha["produto"],
                "dose": float(linha["dose"]),
                "total_insumo_l": float(linha["total_insumo_l"]),
                "dimensoes": {},
                "manejo": cultura["manejo"],
                "unidade_dose": cultura["unidade_dose"],
            })
        except (KeyError, ValueError) as erro:
            print(f"!! Linha ignorada no CSV ({erro}).")
    if total_registros():
        print(f">> {total_registros()} registro(s) carregado(s) de {ARQUIVO_CSV.name}.")


# -------------------------------------------------------------------- menu
MENU = """
=========== FarmTech Solutions ===========
1 - Cadastrar plantio
2 - Listar dados e resultados
3 - Atualizar registro
4 - Excluir registro
5 - Exportar dados para CSV
6 - Sair
=========================================="""


def main():
    print("FarmTech Solutions - Fazenda modelo (interior de São Paulo)")
    print("Culturas atendidas: cana-de-açúcar (retângulo) e laranja (trapézio).")
    try:
        if val.confirmar("Carregar os dados já exportados em dados/plantios.csv?"):
            importar_csv()
    except val.EntradaEncerrada:
        print("\nEntrada encerrada. Até logo!")
        return

    while True:
        print(MENU)
        try:
            opcao = val.ler_opcao("Escolha uma opção: ", ("1", "2", "3", "4", "5", "6"))
            if opcao == "1":
                cadastrar()
            elif opcao == "2":
                listar_registros()
            elif opcao == "3":
                atualizar()
            elif opcao == "4":
                excluir()
            elif opcao == "5":
                exportar_csv()
            elif opcao == "6":
                if total_registros() and val.confirmar("Exportar os dados antes de sair?"):
                    exportar_csv()
                print("\nEncerrando. Bom plantio!")
                break
        except val.EntradaEncerrada:
            print("\nEntrada encerrada. Encerrando o programa.")
            break


if __name__ == "__main__":
    main()
