"""Análisis sintáctico descendente recursivo (gramática LL(1))."""
from dataclasses import dataclass, field

from ..models.lenguaje import LEGIBLE


class ErrorSintactico(Exception):
    def __init__(self, mensaje, posicion):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.posicion = posicion


@dataclass
class Nodo:
    nombre: str
    lexema: str = None
    hijos: list = field(default_factory=list)


def arbol_a_texto(nodo, prefijo="", ultimo=True, raiz=True):
    etiqueta = nodo.nombre if nodo.lexema is None else f'{nodo.nombre}  "{nodo.lexema}"'
    if raiz:
        lineas = [etiqueta]
        hijo_prefijo = ""
    else:
        lineas = [prefijo + ("└── " if ultimo else "├── ") + etiqueta]
        hijo_prefijo = prefijo + ("    " if ultimo else "│   ")
    for i, h in enumerate(nodo.hijos):
        lineas += arbol_a_texto(h, hijo_prefijo, i == len(nodo.hijos) - 1, False).split("\n")
    return "\n".join(lineas)


class _Parser:
    def __init__(self, tokens, longitud):
        self.tokens, self.i, self.longitud = tokens, 0, longitud
        self.producciones = []

    def actual(self):
        return self.tokens[self.i] if self.i < len(self.tokens) else None

    def error(self, esperado):
        tok = self.actual()
        if tok is None:
            return ErrorSintactico(f"Cadena incompleta: se esperaba {esperado}.", self.longitud)
        if tok.tipo == "ERROR":
            return ErrorSintactico(
                f"Se esperaba {esperado}, pero «{tok.lexema}» no es válido en esta posición.", tok.posicion)
        return ErrorSintactico(
            f"Se esperaba {esperado}, pero se encontró «{tok.lexema}» ({tok.tipo}).", tok.posicion)

    def consumir(self, tipo):
        tok = self.actual()
        if tok is None or tok.tipo != tipo:
            raise self.error(LEGIBLE[tipo])
        self.i += 1
        return Nodo(tipo, tok.lexema)

    def regla(self, texto):
        self.producciones.append(texto)

    # Pedido → T_PREFIJO T_GUION T_NUM T_GUION Ubicacion T_GUION ListaItems
    def pedido(self):
        self.regla("Pedido → T_PREFIJO T_GUION T_NUM T_GUION Ubicacion T_GUION ListaItems")
        n = Nodo("Pedido")
        n.hijos = [self.consumir("T_PREFIJO"), self.consumir("T_GUION"), self.consumir("T_NUM"),
                   self.consumir("T_GUION"), self.ubicacion(), self.consumir("T_GUION"),
                   self.lista_items()]
        if self.actual() is not None:
            raise self.error("'+' (otro ítem) o el fin de la cadena")
        return n

    def ubicacion(self):
        self.regla("Ubicacion → T_UBICACION")
        return Nodo("Ubicacion", hijos=[self.consumir("T_UBICACION")])

    def lista_items(self):
        self.regla("ListaItems → T_ITEM Resto")
        n = Nodo("ListaItems")
        n.hijos = [self.consumir("T_ITEM"), self.resto()]
        return n

    def resto(self):
        n = Nodo("Resto")
        tok = self.actual()
        if tok is not None and tok.tipo == "T_MAS":
            self.regla("Resto → T_MAS ListaItems")
            n.hijos = [self.consumir("T_MAS"), self.lista_items()]
        else:
            self.regla("Resto → ε")
            n.hijos = [Nodo("ε")]
        return n


def analizar(tokens, longitud):
    p = _Parser(tokens, longitud)
    try:
        arbol = p.pedido()
    except ErrorSintactico as e:
        return {"valido": False, "error": {"mensaje": e.mensaje, "posicion": e.posicion},
                "producciones": [], "arbol": None}
    return {"valido": True, "error": None, "producciones": p.producciones,
            "arbol": arbol_a_texto(arbol)}
