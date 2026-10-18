# Analizador léxico y sintáctico de pedidos

Proyecto final de Teoría de Computación (USIL, 2026-II).
Valida pedidos de restaurante (mesa, para llevar y delivery) antes de enviarlos a cocina.

Formato de un pedido: `PED-NNN-UBICACIÓN-ÍTEM(+ÍTEM)*`
Ejemplos válidos: `PED-045-M12-C03` · `PED-102-D-B02+S01` · `PED-007-L-C01+B02+S03`

## Ejecutar en tu PC

```bash
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python run.py                  # abre http://127.0.0.1:5000
```

Pruebas: `python -m unittest discover -s tests -t .`

## Qué pide cada etapa y dónde está

| Pedido del docente | Dónde está |
|---|---|
| GUI + Flask con enunciado | `app/views/templates/index.html`, `app/controllers/analizador_controller.py` |
| Subir archivo y escribir el lenguaje, con ejemplo | formulario de la página principal (ejemplo en `storage/`) |
| Tokens y lexemas | `app/services/lexer_service.py` |
| Expresión regular por lexema | `app/models/lenguaje.py` (lista `TOKENS`) |
| AFND de cada ER (gráfico por código) | `app/services/regex_service.py` (Thompson) y `dot_service.py` |
| AFD equivalente | `app/services/automata_service.py` (subconjuntos) |
| Quíntupla, tabla y transiciones | página `/automatas` |
| Gramática, derivación y semántica | `parser_service.py`, `semantic_service.py` |
| Pruebas con más de 30 cadenas (OE5) | `storage/pedidos_prueba_33.txt` y `tests/` |

Los gráficos salen de código DOT generado en Python y se dibujan en el navegador con viz.js.

## Subir a GitHub

```bash
git init
git add .
git commit -m "Proyecto TC: analizador de pedidos"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/proyecto-pedidos.git
git push -u origin main
```

## Publicar (hosting gratuito)

**Vercel** (como los ejemplos del docente): Add New → Project → importa el repositorio → Deploy. Ya incluye `vercel.json` y `api/index.py`.

**Render** (alternativa): New → Web Service → tu repositorio. Build: `pip install -r requirements.txt`. Start: `gunicorn run:app`.

## Nota sobre la gramática

En el Avance 1 la regla era `ListaItems → ITEM | ITEM MAS ListaItems`. Aquí se factoriza por la izquierda
(`ListaItems → T_ITEM Resto`, `Resto → T_MAS ListaItems | ε`) para que sea LL(1) y se pueda analizar con un solo token de preanálisis.
El lenguaje es el mismo. Además, el lenguaje de pedidos es regular: por eso existe un AFD del pedido completo.
