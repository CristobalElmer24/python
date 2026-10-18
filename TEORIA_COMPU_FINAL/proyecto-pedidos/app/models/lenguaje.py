"""Definición formal del lenguaje de pedidos (Avance 1)."""

ALFABETO = list("PEDMLCBS+-0123456789")

# (token, expresión regular, descripción) — el orden es la prioridad del lexer
TOKENS = [
    ("T_PREFIJO", "PED", "Constante que abre todo pedido"),
    ("T_GUION", "-", "Separador de campos"),
    ("T_MAS", r"\+", "Concatenador de varios ítems"),
    ("T_NUM", "[0-9]{3}", "Correlativo de 3 dígitos"),
    ("T_UBICACION", "M[0-9]{1,2}|D|L", "Mesa (M + 1 o 2 dígitos), delivery o para llevar"),
    ("T_ITEM", "(C|B|S)[0-9]{2}", "Categoría (combo, bebida, snack) + código de producto"),
]
ER_POR_TOKEN = {nombre: er for nombre, er, _ in TOKENS}

# ER del pedido completo (el lenguaje es regular)
ER_PEDIDO = r"PED-[0-9]{3}-(M[0-9]{1,2}|D|L)-(C|B|S)[0-9]{2}(\+(C|B|S)[0-9]{2})*"

# Gramática libre de contexto, factorizada por la izquierda para que sea LL(1)
GRAMATICA = [
    "Pedido     → T_PREFIJO T_GUION T_NUM T_GUION Ubicacion T_GUION ListaItems",
    "Ubicacion  → T_UBICACION",
    "ListaItems → T_ITEM Resto",
    "Resto      → T_MAS ListaItems | ε",
]
NO_TERMINALES = ["Pedido", "Ubicacion", "ListaItems", "Resto"]
TERMINALES = [t for t, _, _ in TOKENS]

LEGIBLE = {
    "T_PREFIJO": "el prefijo PED",
    "T_GUION": "un guion '-'",
    "T_NUM": "un correlativo de 3 dígitos",
    "T_UBICACION": "una ubicación (M1–M99, D o L)",
    "T_ITEM": "un ítem (C, B o S + 2 dígitos)",
    "T_MAS": "'+'",
}
CATEGORIAS = {"C": "Combo", "B": "Bebida", "S": "Postre/Snack"}
