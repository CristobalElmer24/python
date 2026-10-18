import re

from ..models.lenguaje import TOKENS
from ..models.token import Token

_PATRONES = [(nombre, re.compile(er)) for nombre, er, _ in TOKENS]


def _coincidencia(linea, pos):
    for nombre, patron in _PATRONES:
        m = patron.match(linea, pos)
        if m and m.end() > pos:
            return nombre, m
    return None


def tokenizar(linea):
    """Análisis léxico: devuelve la lista de tokens. Los caracteres que no
    pertenecen a ningún token se agrupan en un token ERROR."""
    tokens, pos = [], 0
    while pos < len(linea):
        hallado = _coincidencia(linea, pos)
        if hallado:
            nombre, m = hallado
            tokens.append(Token(nombre, m.group(), pos))
            pos = m.end()
        else:
            inicio = pos
            pos += 1
            while pos < len(linea) and _coincidencia(linea, pos) is None:
                pos += 1
            tokens.append(Token("ERROR", linea[inicio:pos], inicio))
    return tokens


def errores_lexicos(tokens):
    return [
        f"Error léxico en la posición {t.posicion}: «{t.lexema}» no coincide con ningún token."
        for t in tokens if t.tipo == "ERROR"
    ]
