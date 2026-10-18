"""AFND -> AFD (construcción de subconjuntos), simulación, tablas y quíntupla."""
from collections import defaultdict
from functools import lru_cache

from ..models.automata import AFD
from ..models.lenguaje import ER_PEDIDO
from ..utils.helpers import formatear_simbolos
from . import regex_service


def _num(estado):
    return int("".join(c for c in estado if c.isdigit()))


def _cerradura(eps, conjunto):
    res, pila = set(conjunto), list(conjunto)
    while pila:
        for d in eps.get(pila.pop(), ()):
            if d not in res:
                res.add(d)
                pila.append(d)
    return frozenset(res)


def subconjuntos(afnd, completo=False):
    eps, sim = defaultdict(list), defaultdict(list)
    for o, l, d in afnd.transiciones:
        (eps[o].append(d) if l is None else sim[o].append((l, d)))

    inicio = _cerradura(eps, {afnd.inicial})
    nombres, cola, delta = {inicio: "q0"}, [inicio], {}
    while cola:
        S = cola.pop(0)
        for a in afnd.alfabeto:
            mover = {d for s in S for l, d in sim[s] if a in l}
            if not mover:
                continue
            T = _cerradura(eps, mover)
            if T not in nombres:
                nombres[T] = f"q{len(nombres)}"
                cola.append(T)
            delta[(nombres[S], a)] = nombres[T]

    estados = list(nombres.values())
    finales = frozenset(n for S, n in nombres.items() if afnd.finales & S)
    composicion = {n: sorted(S, key=_num) for S, n in nombres.items()}

    trampa = None
    if completo and any((q, a) not in delta for q in estados for a in afnd.alfabeto):
        trampa = "qT"
        estados.append(trampa)
        for q in estados:
            for a in afnd.alfabeto:
                delta.setdefault((q, a), trampa)
    return AFD(estados, list(afnd.alfabeto), delta, "q0", finales, composicion, trampa)


@lru_cache(maxsize=64)
def construir(er, completo=False):
    afnd = regex_service.er_a_afnd(er)
    return afnd, subconjuntos(afnd, completo)


def simular(afd, cadena):
    """Devuelve (aceptada, camino de estados)."""
    q, camino = afd.inicial, [afd.inicial]
    for c in cadena:
        q = afd.delta.get((q, c))
        if q is None:
            return False, camino + ["∅"]
        camino.append(q)
    return q in afd.finales, camino


def validar_con_afd(cadena):
    _, afd = construir(ER_PEDIDO)
    return simular(afd, cadena)


# ------------------------------------------------- datos para las tablas HTML
def tabla(afd):
    filas = []
    for q in afd.estados:
        filas.append({"estado": q, "inicial": q == afd.inicial, "final": q in afd.finales,
                      "celdas": [afd.delta.get((q, a), "∅") for a in afd.alfabeto]})
    return {"encabezado": afd.alfabeto, "filas": filas}


def quintupla(afd):
    return {
        "Q": "{" + ", ".join(afd.estados) + "}",
        "Sigma": "{" + ", ".join(afd.alfabeto) + "}",
        "delta": "definida por la tabla de transiciones",
        "q0": afd.inicial,
        "F": "{" + ", ".join(sorted(afd.finales, key=_num)) + "}",
    }


def transiciones(afd):
    grupos = defaultdict(set)
    for (q, a), d in afd.delta.items():
        grupos[(q, d)].add(a)
    salida = []
    for (q, d), simbolos in sorted(grupos.items(), key=lambda kv: (_num(kv[0][0]) if kv[0][0] != "qT" else 999, kv[0][1])):
        s = formatear_simbolos(simbolos)
        salida.append(f"δ({q}, {s if len(simbolos) == 1 else '{' + s + '}'}) = {d}")
    return salida
