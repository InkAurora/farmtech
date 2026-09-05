"""Leitura e validação das entradas digitadas pelo usuário.

Todas as funções ficam pedindo o dado até receber algo válido. Entrada não
numérica é tratada com try/except e nunca derruba o programa. Se o usuário
encerrar a entrada (Ctrl+D) ou interromper (Ctrl+C), levantamos
EntradaEncerrada para o menu fechar com educação.
"""

import math


class EntradaEncerrada(Exception):
    """Usuário fechou a entrada padrão (Ctrl+D / Ctrl+C)."""


def _perguntar(rotulo):
    """input() com tratamento de fim de entrada."""
    try:
        return input(rotulo).strip()
    except (EOFError, KeyboardInterrupt):
        raise EntradaEncerrada from None


def _para_numero(texto):
    """Aceita vírgula ou ponto como separador decimal."""
    return float(texto.replace(",", "."))


def ler_texto(rotulo, padrao=None):
    """Texto não vazio. Com padrão definido, ENTER mantém o valor atual."""
    sufixo = f" [{padrao}]" if padrao is not None else ""
    while True:
        valor = _perguntar(f"{rotulo}{sufixo}: ")
        if valor:
            return valor
        if padrao is not None:
            return padrao
        print("  !! Digite algum texto.")


def ler_float(rotulo, padrao=None, minimo=0.0, incluir_minimo=False):
    """Número real maior que zero (por padrão). ENTER mantém o valor atual."""
    sufixo = f" [{padrao}]" if padrao is not None else ""
    while True:
        bruto = _perguntar(f"{rotulo}{sufixo}: ")
        if not bruto and padrao is not None:
            return padrao
        try:
            valor = _para_numero(bruto)
        except ValueError:
            print("  !! Valor inválido. Use apenas números (ex.: 250 ou 250,5).")
            continue
        if not math.isfinite(valor):
            print("  !! Valor inválido.")
            continue
        if incluir_minimo and valor < minimo:
            print(f"  !! O valor precisa ser maior ou igual a {minimo:.2f}.")
            continue
        if not incluir_minimo and valor <= minimo:
            print(f"  !! O valor precisa ser maior que {minimo:.2f}.")
            continue
        return valor


def ler_inteiro(rotulo, padrao=None, minimo=1):
    """Número inteiro (quantidade de ruas, por exemplo)."""
    sufixo = f" [{padrao}]" if padrao is not None else ""
    while True:
        bruto = _perguntar(f"{rotulo}{sufixo}: ")
        if not bruto and padrao is not None:
            return padrao
        try:
            valor = int(bruto)
        except ValueError:
            print("  !! Digite um número inteiro (sem casas decimais).")
            continue
        if valor < minimo:
            print(f"  !! O valor precisa ser maior ou igual a {minimo}.")
            continue
        return valor


def ler_campo(campo, padrao=None):
    """Lê um campo declarado em calculos.CULTURAS: (chave, rótulo, tipo)."""
    _, rotulo, tipo = campo
    if tipo == "int":
        return ler_inteiro(rotulo, padrao=padrao, minimo=1)
    return ler_float(rotulo, padrao=padrao)


def ler_opcao(rotulo, opcoes_validas):
    """Opção de menu. Só devolve quando estiver na lista de opções."""
    validas = [str(o) for o in opcoes_validas]
    while True:
        valor = _perguntar(rotulo)
        if valor in validas:
            return valor
        print(f"  !! Opção inválida. Escolha uma entre: {', '.join(validas)}.")


def ler_indice(rotulo, tamanho):
    """Índice existente nos vetores (0 até tamanho-1). '' cancela a operação."""
    if tamanho == 0:
        return None
    while True:
        bruto = _perguntar(f"{rotulo} (ENTER cancela): ")
        if not bruto:
            return None
        try:
            indice = int(bruto)
        except ValueError:
            print("  !! Digite um número inteiro.")
            continue
        if 0 <= indice < tamanho:
            return indice
        print(f"  !! Índice inexistente. Use um valor entre 0 e {tamanho - 1}.")


def confirmar(rotulo):
    """Confirmação s/n. Qualquer outra coisa é rejeitada."""
    while True:
        valor = _perguntar(f"{rotulo} (s/n): ").lower()
        if valor in ("s", "sim"):
            return True
        if valor in ("n", "nao", "não"):
            return False
        print("  !! Responda com 's' ou 'n'.")


def numero(valor, casas=2):
    """Formata número no padrão brasileiro com 2 casas decimais."""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "@").replace(".", ",").replace("@", ".")
