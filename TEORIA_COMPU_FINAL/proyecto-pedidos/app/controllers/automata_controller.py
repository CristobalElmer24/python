from flask import render_template, request

from ..models.lenguaje import ER_PEDIDO, TOKENS
from ..services import automata_service as au
from ..services import dot_service


def ficha(nombre, er, descripcion, completo):
    afnd, afd = au.construir(er, completo)
    return {"nombre": nombre, "er": er, "descripcion": descripcion,
            "afnd": afnd, "afnd_dot": dot_service.afnd_a_dot(afnd),
            "afd": afd, "afd_dot": dot_service.afd_a_dot(afd),
            "tabla": au.tabla(afd), "quintupla": au.quintupla(afd),
            "transiciones": au.transiciones(afd)}


def automatas():
    completo = request.args.get("completo") == "1"
    fichas = [ficha(n, er, d, completo) for n, er, d in TOKENS]
    fichas.append(ficha("PEDIDO COMPLETO", ER_PEDIDO, "Todo el lenguaje de pedidos en una sola expresión regular", completo))
    return render_template("automatas.html", fichas=fichas, completo=completo)
