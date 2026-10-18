import io
import unittest

from app import create_app


class TestRutas(unittest.TestCase):
    def setUp(self):
        self.cliente = create_app().test_client()

    def test_inicio(self):
        r = self.cliente.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("Analizar y compilar", r.get_data(as_text=True))

    def test_analizar_texto(self):
        r = self.cliente.post("/", data={"texto": "PED-045-M12-C03\nPED-45-M12-C03"})
        html = r.get_data(as_text=True)
        self.assertIn("A cocina", html)
        self.assertIn("Rechazado", html)

    def test_analizar_archivo(self):
        datos = {"archivo": (io.BytesIO(b"PED-102-D-B02+S01"), "pedidos.txt"), "texto": ""}
        r = self.cliente.post("/", data=datos, content_type="multipart/form-data")
        self.assertIn("A cocina", r.get_data(as_text=True))

    def test_archivo_no_txt(self):
        datos = {"archivo": (io.BytesIO(b"x"), "pedidos.csv")}
        r = self.cliente.post("/", data=datos, content_type="multipart/form-data")
        self.assertIn("extensión .txt", r.get_data(as_text=True))

    def test_automatas(self):
        for url in ("/automatas", "/automatas?completo=1"):
            r = self.cliente.get(url)
            self.assertEqual(r.status_code, 200)
            self.assertIn("digraph AFD", r.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
