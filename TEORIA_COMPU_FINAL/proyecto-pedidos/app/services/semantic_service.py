"""Análisis semántico: reglas que la gramática no puede expresar."""
from ..models.lenguaje import CATEGORIAS


def analizar(tokens):
    """Se llama solo con tokens ya validados sintácticamente."""
    num, ubic = tokens[2], tokens[4]
    items = [t for t in tokens if t.tipo == "T_ITEM"]
    errores, avisos, atributos = [], [], []

    correlativo = int(num.lexema)
    if correlativo == 0:
        errores.append("Semántico: el correlativo debe estar entre 001 y 999.")
    atributos.append(("T_NUM", num.lexema, "int", "correlativo = int(lexema); exigir 1..999", correlativo))

    mesa = None
    if ubic.lexema[0] == "M":
        canal, mesa = "mesa", int(ubic.lexema[1:])
        if mesa == 0:
            errores.append("Semántico: el número de mesa debe estar entre 1 y 99.")
    elif ubic.lexema == "D":
        canal = "delivery"
    else:
        canal = "para llevar"
    atributos.append(("T_UBICACION", ubic.lexema, "str / int", "canal según la letra; si es M, mesa = int(dígitos) ≥ 1",
                      canal if mesa is None else f"{canal} {mesa}"))

    lista, vistos = [], set()
    for t in items:
        codigo = int(t.lexema[1:])
        if codigo == 0:
            errores.append(f"Semántico: el código de producto de «{t.lexema}» debe estar entre 01 y 99.")
        if t.lexema in vistos:
            avisos.append(f"Aviso: el ítem «{t.lexema}» está repetido; revisar posible duplicidad de platos.")
        vistos.add(t.lexema)
        lista.append({"categoria": CATEGORIAS[t.lexema[0]], "codigo": t.lexema})
        atributos.append(("T_ITEM", t.lexema, "dict", "categoría por la letra; producto = int(2 dígitos) ≥ 1",
                          f"{CATEGORIAS[t.lexema[0]]} #{codigo}"))

    objeto = {"correlativo": correlativo, "canal": canal}
    if mesa is not None:
        objeto["mesa"] = mesa
    objeto["items"] = lista
    return {"objeto": objeto, "errores": errores, "avisos": avisos, "atributos": atributos}
