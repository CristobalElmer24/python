"""Expresión regular -> AST -> AFND (construcción de Thompson).

Sintaxis soportada: literales, \\x (escape), [a-z] (clases), ( ), |, *, +, ?, {n} y {n,m}.
"""
from collections import defaultdict

from ..models.automata import AFND


class ErrorRegex(Exception):
    pass


# ---------------------------------------------------------------- parser de ER
class _ParserER:
    def __init__(self, texto):
        self.s, self.i = texto, 0

    def peek(self):
        return self.s[self.i] if self.i < len(self.s) else None

    def parse(self):
        nodo = self.expr()
        if self.i != len(self.s):
            raise ErrorRegex(f"Carácter inesperado «{self.peek()}» en la posición {self.i}")
        return nodo

    def expr(self):
        partes = [self.termino()]
        while self.peek() == "|":
            self.i += 1
            partes.append(self.termino())
        return partes[0] if len(partes) == 1 else ("alt", partes)

    def termino(self):
        partes = []
        while self.peek() not in (None, "|", ")"):
            partes.append(self.factor())
        if not partes:
            return ("eps",)
        return partes[0] if len(partes) == 1 else ("cat", partes)

    def factor(self):
        nodo = self.atomo()
        while True:
            c = self.peek()
            if c == "*":
                self.i += 1; nodo = ("star", nodo)
            elif c == "+":
                self.i += 1; nodo = ("plus", nodo)
            elif c == "?":
                self.i += 1; nodo = ("opt", nodo)
            elif c == "{":
                nodo = self.repeticion(nodo)
            else:
                return nodo

    def repeticion(self, nodo):
        fin = self.s.find("}", self.i)
        if fin == -1:
            raise ErrorRegex("Falta '}' en un cuantificador")
        cuerpo = self.s[self.i + 1:fin]
        self.i = fin + 1
        try:
            if "," in cuerpo:
                a, b = cuerpo.split(",")
                return ("rep", nodo, int(a), int(b))
            return ("rep", nodo, int(cuerpo), int(cuerpo))
        except ValueError:
            raise ErrorRegex(f"Cuantificador inválido {{{cuerpo}}}")

    def atomo(self):
        c = self.peek()
        if c == "(":
            self.i += 1
            nodo = self.expr()
            if self.peek() != ")":
                raise ErrorRegex("Falta ')'")
            self.i += 1
            return nodo
        if c == "[":
            return self.clase()
        if c == "\\":
            self.i += 1
            lit = self.peek()
            if lit is None:
                raise ErrorRegex("Escape '\\' sin carácter")
            self.i += 1
            return ("chars", frozenset(lit))
        if c is None or c in "*+?{|)":
            raise ErrorRegex(f"Se esperaba un símbolo en la posición {self.i}")
        self.i += 1
        return ("chars", frozenset(c))

    def clase(self):
        self.i += 1
        chars = set()
        while self.peek() not in (None, "]"):
            a = self.peek()
            self.i += 1
            if self.peek() == "-" and self.i + 1 < len(self.s) and self.s[self.i + 1] != "]":
                b = self.s[self.i + 1]
                self.i += 2
                chars.update(chr(x) for x in range(ord(a), ord(b) + 1))
            else:
                chars.add(a)
        if self.peek() != "]":
            raise ErrorRegex("Falta ']'")
        self.i += 1
        return ("chars", frozenset(chars))


def parsear(er):
    return _expandir(_ParserER(er).parse())


def _expandir(n):
    """Reemplaza x{n,m} por x...x(x?)...(x?) para quedarse solo con operadores básicos."""
    t = n[0]
    if t in ("chars", "eps"):
        return n
    if t in ("cat", "alt"):
        return (t, [_expandir(x) for x in n[1]])
    if t in ("star", "plus", "opt"):
        return (t, _expandir(n[1]))
    _, x, a, b = n
    x = _expandir(x)
    partes = [x] * a + [("opt", x)] * (b - a)
    if not partes:
        return ("eps",)
    return partes[0] if len(partes) == 1 else ("cat", partes)


# ------------------------------------------------------------------- Thompson
class _Thompson:
    def __init__(self):
        self.n, self.trans = 0, []

    def nuevo(self):
        self.n += 1
        return self.n - 1

    def arista(self, o, simbolos, d):
        self.trans.append((o, simbolos, d))

    def construir(self, nodo):
        t = nodo[0]
        if t in ("chars", "eps"):
            i, f = self.nuevo(), self.nuevo()
            self.arista(i, nodo[1] if t == "chars" else None, f)
            return i, f
        if t == "cat":
            i, f = self.construir(nodo[1][0])
            for sub in nodo[1][1:]:
                si, sf = self.construir(sub)
                self.arista(f, None, si)
                f = sf
            return i, f
        if t == "alt":
            i, f = self.nuevo(), self.nuevo()
            for sub in nodo[1]:
                si, sf = self.construir(sub)
                self.arista(i, None, si)
                self.arista(sf, None, f)
            return i, f
        si, sf = self.construir(nodo[1])
        i, f = self.nuevo(), self.nuevo()
        self.arista(i, None, si)
        self.arista(sf, None, f)
        if t in ("star", "plus"):
            self.arista(sf, None, si)
        if t in ("star", "opt"):
            self.arista(i, None, f)
        return i, f


def er_a_afnd(er):
    th = _Thompson()
    ini, fin = th.construir(parsear(er))

    ady = defaultdict(list)
    for o, _, d in th.trans:
        ady[o].append(d)
    orden, vistos = [ini], {ini}
    for s in orden:                      # BFS: numera los estados en orden de alcance
        for d in ady[s]:
            if d not in vistos:
                vistos.add(d)
                orden.append(d)
    nombre = {s: f"n{k}" for k, s in enumerate(orden)}

    trans = [(nombre[o], l, nombre[d]) for o, l, d in th.trans if o in nombre]
    alfabeto = sorted(set().union(*[l for _, l, _ in trans if l]))
    return AFND(estados=list(nombre.values()), alfabeto=alfabeto, transiciones=trans,
                inicial=nombre[ini], finales=frozenset({nombre[fin]}))
