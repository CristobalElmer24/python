from .helpers import lineas_utiles

MAX_LINEAS = 200


def leer_entrada(request):
    """Devuelve (texto, error). El archivo subido tiene prioridad sobre el cuadro de texto."""
    archivo = request.files.get("archivo")
    if archivo and archivo.filename:
        if not archivo.filename.lower().endswith(".txt"):
            return request.form.get("texto", ""), "El archivo debe tener extensión .txt"
        datos = archivo.read()
        try:
            texto = datos.decode("utf-8-sig")
        except UnicodeDecodeError:
            texto = datos.decode("latin-1")
    else:
        texto = request.form.get("texto", "")

    lineas = lineas_utiles(texto)
    if not lineas:
        return texto, "Escribe o sube al menos un pedido."
    if len(lineas) > MAX_LINEAS:
        return texto, f"Máximo {MAX_LINEAS} pedidos por análisis."
    return texto, None
