"""Genera el código DOT (Graphviz) de los autómatas; el navegador lo dibuja con viz.js."""
from ..utils.helpers import formatear_simbolos


def _esc(t):
    return t.replace("\\", "\\\\").replace('"', '\\"')


def _cabecera(nombre, estados, inicial, finales, trampa=None):
    L = [f"digraph {nombre} {{", "  rankdir=LR;",
         '  node [shape=circle, fontname="Helvetica", fontsize=12];',
         '  edge [fontname="Helvetica", fontsize=11];',
         '  __ini [shape=point, label="", width=0.12];']
    for e in estados:
        forma = "doublecircle" if e in finales else "circle"
        estilo = ", style=dashed" if e == trampa else ""
        L.append(f'  "{e}" [shape={forma}{estilo}];')
    L.append(f'  __ini -> "{inicial}";')
    return L


def afnd_a_dot(afnd):
    L = _cabecera("AFND", afnd.estados, afnd.inicial, afnd.finales)
    grupos = {}
    for o, simbolos, d in afnd.transiciones:
        g = grupos.setdefault((o, d), {"eps": False, "sim": set()})
        if simbolos is None:
            g["eps"] = True
        else:
            g["sim"] |= set(simbolos)
    for (o, d), g in grupos.items():
        partes = (["ε"] if g["eps"] else []) + ([formatear_simbolos(g["sim"])] if g["sim"] else [])
        L.append(f'  "{o}" -> "{d}" [label="{_esc(", ".join(partes))}"];')
    return "\n".join(L + ["}"])


def afd_a_dot(afd):
    L = _cabecera("AFD", afd.estados, afd.inicial, afd.finales, afd.trampa)
    grupos = {}
    for (q, a), d in afd.delta.items():
        grupos.setdefault((q, d), set()).add(a)
    for (q, d), simbolos in grupos.items():
        L.append(f'  "{q}" -> "{d}" [label="{_esc(formatear_simbolos(simbolos))}"];')
    return "\n".join(L + ["}"])
