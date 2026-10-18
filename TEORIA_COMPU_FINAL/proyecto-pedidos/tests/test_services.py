import os
import unittest

from app.services import automata_service, lexer_service, parser_service, semantic_service
from app.utils.helpers import lineas_utiles

RUTA = os.path.join(os.path.dirname(__file__), "..", "storage", "pedidos_prueba_33.txt")


def clasificar(cadena):
    tokens = lexer_service.tokenizar(cadena)
    sintaxis = parser_service.analizar(tokens, len(cadena))
    semantica = semantic_service.analizar(tokens) if sintaxis["valido"] else None
    acepta, _ = automata_service.validar_con_afd(cadena)
    return tokens, sintaxis, semantica, acepta


def leer_bloques():
    bloques, actual = {}, None
    with open(RUTA, encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if linea.startswith("#"):
                actual = linea
                bloques[actual] = []
            elif linea:
                bloques[actual].append(linea)
    return list(bloques.values())


class TestLexer(unittest.TestCase):
    def test_tokens_de_un_pedido(self):
        tipos = [t.tipo for t in lexer_service.tokenizar("PED-102-D-B02+S01")]
        self.assertEqual(tipos, ["T_PREFIJO", "T_GUION", "T_NUM", "T_GUION", "T_UBICACION",
                                 "T_GUION", "T_ITEM", "T_MAS", "T_ITEM"])

    def test_error_lexico_agrupado(self):
        t = lexer_service.tokenizar("PED-45-M12-C03")
        self.assertEqual((t[2].tipo, t[2].lexema), ("ERROR", "45"))


class TestParser(unittest.TestCase):
    def test_mensaje_de_cadena_incompleta(self):
        _, sintaxis, _, _ = clasificar("PED-045-M12-")
        self.assertFalse(sintaxis["valido"])
        self.assertIn("incompleta", sintaxis["error"]["mensaje"])

    def test_arbol_y_producciones(self):
        _, sintaxis, _, _ = clasificar("PED-007-L-C01+B02")
        self.assertTrue(sintaxis["valido"])
        self.assertEqual(sintaxis["producciones"].count("ListaItems → T_ITEM Resto"), 2)


class TestSemantica(unittest.TestCase):
    def test_objeto_json(self):
        _, _, sem, _ = clasificar("PED-045-M12-C03")
        self.assertEqual(sem["objeto"], {"correlativo": 45, "canal": "mesa", "mesa": 12,
                                         "items": [{"categoria": "Combo", "codigo": "C03"}]})

    def test_item_repetido_da_aviso(self):
        _, _, sem, _ = clasificar("PED-045-D-C03+C03")
        self.assertTrue(sem["avisos"])


class TestArchivoDePruebas(unittest.TestCase):
    """OE5: 33 cadenas (15 válidas, 15 inválidas, 3 con error semántico)."""

    def setUp(self):
        self.validas, self.invalidas, self.semanticas = leer_bloques()

    def test_cantidad(self):
        self.assertEqual((len(self.validas), len(self.invalidas), len(self.semanticas)), (15, 15, 3))

    def test_validas(self):
        for c in self.validas:
            _, sin, sem, afd = clasificar(c)
            self.assertTrue(sin["valido"] and afd and not sem["errores"], c)

    def test_invalidas(self):
        for c in self.invalidas:
            _, sin, _, afd = clasificar(c)
            self.assertFalse(sin["valido"] or afd, c)

    def test_semanticas(self):
        for c in self.semanticas:
            _, sin, sem, afd = clasificar(c)
            self.assertTrue(sin["valido"] and afd and sem["errores"], c)


class TestAutomatas(unittest.TestCase):
    def test_afd_de_ubicacion(self):
        afnd, afd = automata_service.construir("M[0-9]{1,2}|D|L")
        for ok in ["M1", "M12", "D", "L"]:
            self.assertTrue(automata_service.simular(afd, ok)[0], ok)
        for mal in ["M", "M123", "X", "DL", ""]:
            self.assertFalse(automata_service.simular(afd, mal)[0], mal)

    def test_afd_completo_tiene_trampa(self):
        _, afd = automata_service.construir("PED", True)
        self.assertEqual(afd.trampa, "qT")
        self.assertTrue(all((q, a) in afd.delta for q in afd.estados for a in afd.alfabeto))

    def test_lineas_utiles_ignora_comentarios(self):
        self.assertEqual(lineas_utiles("# x\n\n PED-1 \n"), ["PED-1"])


if __name__ == "__main__":
    unittest.main()
