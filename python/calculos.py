"""Cálculos de área e de insumos da FarmTech Solutions.

Este módulo concentra as regras de negócio (geometria dos talhões e volume de
insumo). Ele não conversa com o usuário: recebe números, devolve números.
Assim as fórmulas podem ser testadas isoladamente e o menu fica simples.

Para trocar de cultura basta editar o dicionário CULTURAS: nenhuma outra parte
do sistema precisa ser alterada.
"""

METROS_QUADRADOS_POR_HECTARE = 10_000
MILILITROS_POR_LITRO = 1_000


# ---------------------------------------------------------------- geometria
def area_retangulo(comprimento_m, largura_m):
    """Área de um talhão retangular, em m²."""
    return comprimento_m * largura_m


def area_trapezio(base_maior_m, base_menor_m, altura_m):
    """Área de um talhão trapezoidal, em m²."""
    return ((base_maior_m + base_menor_m) * altura_m) / 2


def para_hectare(area_m2):
    """Converte m² em hectares."""
    return area_m2 / METROS_QUADRADOS_POR_HECTARE


# ------------------------------------------------------------------ insumos
def insumo_por_area(area_ha, dose_l_por_ha):
    """Volume total de insumo (L) para uma dose informada em L/ha."""
    return area_ha * dose_l_por_ha


def comprimento_total_ruas(quantidade_ruas, comprimento_medio_rua_m):
    """Metros lineares de rua a serem percorridos pelo pulverizador."""
    return quantidade_ruas * comprimento_medio_rua_m


def insumo_por_rua(comprimento_total_m, dose_ml_por_metro):
    """Volume total de insumo (L) para uma dose informada em mL/metro de rua."""
    return (comprimento_total_m * dose_ml_por_metro) / MILILITROS_POR_LITRO


# ----------------------------------------------------------------- culturas
# campos: (chave, rótulo mostrado ao usuário, tipo)
CULTURAS = {
    "1": {
        "chave": "cana-de-acucar",
        "nome": "Cana-de-açúcar",
        "geometria": "retangulo",
        "campos_area": (
            ("comprimento_m", "Comprimento do talhão (m)", "float"),
            ("largura_m", "Largura do talhão (m)", "float"),
        ),
        "manejo": "area",
        "campos_manejo": (),
        "rotulo_dose": "Dose do produto (L/ha)",
        "unidade_dose": "L/ha",
    },
    "2": {
        "chave": "laranja",
        "nome": "Laranja",
        "geometria": "trapezio",
        "campos_area": (
            ("base_maior_m", "Base maior do talhão (m)", "float"),
            ("base_menor_m", "Base menor do talhão (m)", "float"),
            ("altura_m", "Altura entre as bases (m)", "float"),
        ),
        "manejo": "rua",
        "campos_manejo": (
            ("quantidade_ruas", "Quantidade de ruas", "int"),
            ("comprimento_medio_rua_m", "Comprimento médio de cada rua (m)", "float"),
        ),
        "rotulo_dose": "Dose do produto (mL por metro de rua)",
        "unidade_dose": "mL/m",
    },
}


def cultura_por_chave(chave):
    """Localiza a definição da cultura pela chave gravada no registro."""
    for cultura in CULTURAS.values():
        if cultura["chave"] == chave:
            return cultura
    raise KeyError(f"Cultura desconhecida: {chave}")


def campos_da_cultura(cultura):
    """Todos os campos numéricos pedidos ao usuário para essa cultura."""
    return tuple(cultura["campos_area"]) + tuple(cultura["campos_manejo"])


# --------------------------------------------------------------- fachada
def calcular_area_m2(cultura, dimensoes):
    """Área em m² de acordo com a geometria da cultura."""
    geometria = cultura["geometria"]
    if geometria == "retangulo":
        return area_retangulo(dimensoes["comprimento_m"], dimensoes["largura_m"])
    if geometria == "trapezio":
        return area_trapezio(
            dimensoes["base_maior_m"],
            dimensoes["base_menor_m"],
            dimensoes["altura_m"],
        )
    raise ValueError(f"Geometria não suportada: {geometria}")


def calcular_insumo_l(cultura, dimensoes, area_ha, dose):
    """Volume total de insumo (L) de acordo com o manejo da cultura."""
    manejo = cultura["manejo"]
    if manejo == "area":
        return insumo_por_area(area_ha, dose)
    if manejo == "rua":
        metros = comprimento_total_ruas(
            dimensoes["quantidade_ruas"],
            dimensoes["comprimento_medio_rua_m"],
        )
        return insumo_por_rua(metros, dose)
    raise ValueError(f"Manejo não suportado: {manejo}")


def montar_registro(cultura, dimensoes, produto, dose, id_registro):
    """Calcula tudo e devolve o registro pronto para entrar nos vetores."""
    area_m2 = calcular_area_m2(cultura, dimensoes)
    area_ha = para_hectare(area_m2)
    total_l = calcular_insumo_l(cultura, dimensoes, area_ha, dose)
    return {
        "id": id_registro,
        "cultura": cultura["chave"],
        "area_m2": area_m2,
        "area_ha": area_ha,
        "produto": produto,
        "dose": dose,
        "total_insumo_l": total_l,
        "dimensoes": dict(dimensoes),
        "manejo": cultura["manejo"],
        "unidade_dose": cultura["unidade_dose"],
    }
