import json

from flask import current_app, render_template, request

from ..models.lenguaje import (ER_POR_TOKEN, GRAMATICA, NO_TERMINALES, TERMINALES, TOKENS)
from ..services import automata_service, lexer_service, parser_service, semantic_service
from ..utils.helpers import lineas_utiles
from ..utils.validators import leer_entrada


def procesar(n, cadena):
    tokens = lexer_service.tokenizar(cadena)
    sintaxis = parser_service.analizar(tokens, len(cadena))
    semantica = semantic_service.analizar(tokens) if sintaxis["valido"] else None
    acepta, camino = automata_service.validar_con_afd(cadena)

    errores = lexer_service.errores_lexicos(tokens)
    if not sintaxis["valido"]:
        e = sintaxis["error"]
        errores.append(f"Error sintáctico en la posición {e['posicion']}: {e['mensaje']}")
    if semantica:
        errores += semantica["errores"]

    return {"n": n, "cadena": cadena, "tokens": tokens, "sintaxis": sintaxis,
            "semantica": semantica, "afd_acepta": acepta, "afd_camino": camino,
            "errores": errores, "valido": not errores}


def a_json(resultados):
    return [{"linea": r["n"], "cadena": r["cadena"], "valido": r["valido"],
             "pedido": r["semantica"]["objeto"] if r["valido"] else None,
             "errores": r["errores"]} for r in resultados]


def index():
    texto, error, resultados, salida = current_app.config["EJEMPLO"], None, None, None
    if request.method == "POST":
        texto, error = leer_entrada(request)
        if not error:
            resultados = [procesar(i, l) for i, l in enumerate(lineas_utiles(texto), start=1)]
            salida = json.dumps(a_json(resultados), ensure_ascii=False, indent=2)
    return render_template(
        "index.html", enunciado=current_app.config["ENUNCIADO"], ejemplo=current_app.config["EJEMPLO"],
        texto=texto, error=error, resultados=resultados, salida=salida, tokens=TOKENS,
        er_por_token=ER_POR_TOKEN, gramatica=GRAMATICA, no_terminales=NO_TERMINALES,
        terminales=TERMINALES)
