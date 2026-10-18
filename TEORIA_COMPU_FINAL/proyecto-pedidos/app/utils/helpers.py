def lineas_utiles(texto):
    """Líneas no vacías; las que empiezan con # se ignoran (comentarios)."""
    return [l.strip() for l in texto.splitlines() if l.strip() and not l.strip().startswith("#")]


def formatear_simbolos(simbolos):
    """{'0','1',...,'9'} -> '0-9'; {'C','B','S'} -> 'B,C,S'."""
    orden = sorted(simbolos)
    partes, i = [], 0
    while i < len(orden):
        j = i
        while j + 1 < len(orden) and ord(orden[j + 1]) == ord(orden[j]) + 1:
            j += 1
        if j - i >= 2:
            partes.append(f"{orden[i]}-{orden[j]}")
        else:
            partes.extend(orden[i:j + 1])
        i = j + 1
    return ",".join(partes)
