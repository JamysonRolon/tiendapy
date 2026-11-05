# Estas pruebas usan unittest, incluido en Python, y archivos temporales.
# No modifican los archivos de ejemplo que están en data.
import contextlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

# Permite importar los módulos de src al ejecutar las pruebas desde esta carpeta.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from inventario import (registrar_producto, buscar_codigo, buscar_categoria,
                        modificar_producto, eliminar_producto)
from ventas import agregar_al_carrito, calcular_venta, calcular_cambio, preparar_venta
from persistencia import (cargar_inventario, cargar_ventas, guardar_inventario,
                          guardar_compra, registrar_venta)
from reportes import alertas_stock, cierre_dia, mostrar_alertas
from validaciones import leer_numero
import main


def producto(codigo="LAC001", precio=5000, stock=20):
    # Crea un producto de prueba; los argumentos permiten variar cada caso.
    return {"codigo": codigo, "nombre": "Leche", "categoria": "Lacteos",
            "precio": precio, "stock": stock, "stock_minimo": 3,
            "proveedor": "Proveedor de prueba"}


class TiendaPruebas(unittest.TestCase):
    # unittest ejecuta los métodos cuyo nombre empieza por test_.
    def setUp(self):
        # Antes de cada prueba prepara un inventario nuevo, separado de las demás.
        self.inventario = {}
        registrar_producto(self.inventario, producto())

    def test_crud_y_busquedas(self):
        # assertEqual compara el resultado con lo esperado.
        # assertRaises comprueba que una regla rechace una operación incorrecta.
        self.assertEqual(buscar_codigo(self.inventario, "lac001")["stock"], 20)
        self.assertEqual(len(buscar_categoria(self.inventario, "Lácteos")), 1)
        self.assertEqual(buscar_categoria(self.inventario, "Otra"), [])
        with self.assertRaises(ValueError):
            registrar_producto(self.inventario, producto("lac001"))
        with self.assertRaises(ValueError):
            buscar_codigo(self.inventario, "NO")
        modificar_producto(self.inventario, "LAC001", 6000, 10)
        self.assertEqual(self.inventario["LAC001"]["precio"], 6000)
        eliminar_producto(self.inventario, "LAC001")
        self.assertEqual(self.inventario, {})

    def test_valores_invalidos_no_modifican_producto(self):
        # Un rechazo no debe dejar un precio o stock cambiado a medias.
        for precio, stock in [(0, 3), (-1, 3), (5, 0), (5, -1), (float("nan"), 2)]:
            with self.subTest(precio=precio, stock=stock):
                with self.assertRaises(ValueError):
                    modificar_producto(self.inventario, "LAC001", precio, stock)
                self.assertEqual(self.inventario["LAC001"]["precio"], 5000)
                self.assertEqual(self.inventario["LAC001"]["stock"], 20)
        for campo, valor in [("nombre", "a|b"), ("stock", 0), ("stock", 1.5),
                             ("precio", -1), ("categoria", "Otros")]:
            p = producto("NUEVO")
            p[campo] = valor
            with self.assertRaises(ValueError):
                registrar_producto(self.inventario, p)

    def test_descuentos_en_los_limites(self):
        # Revisa los valores justo antes de los umbrales, en ellos y por encima.
        # subTest identifica cuál de los casos falla sin ocultar los demás.
        for subtotal, descuento in [(49999, 0), (50000, 2500), (99999, 4999.95),
                                     (100000, 10000), (150000, 15000)]:
            with self.subTest(subtotal=subtotal):
                inv = {"A": producto("A", subtotal, 1)}
                resumen = calcular_venta(inv, {"A": 1})
                self.assertEqual(resumen["descuento"], descuento)
                self.assertEqual(resumen["total"], round(subtotal - descuento, 2))

    def test_carrito_repetido_no_sobrevende(self):
        # Sumar dos entradas del mismo producto también debe respetar el stock.
        carrito = {}
        agregar_al_carrito(self.inventario, carrito, "lac001", 12)
        with self.assertRaises(ValueError):
            agregar_al_carrito(self.inventario, carrito, "LAC001", 9)
        self.assertEqual(carrito, {"LAC001": 12})
        self.assertEqual(self.inventario["LAC001"]["stock"], 20)
        for cantidad in [0, -1, "texto"]:
            with self.assertRaises(ValueError):
                agregar_al_carrito(self.inventario, carrito, "LAC001", cantidad)
        with self.assertRaises(ValueError):
            calcular_venta(self.inventario, {})

    def test_pago_y_venta_de_varios_productos(self):
        # Comprueba el cambio y que preparar la venta conserve el inventario original.
        registrar_producto(self.inventario, producto("BEB001", 3000, 5))
        carrito = {"LAC001": 2, "BEB001": 3}
        with self.assertRaises(ValueError):
            preparar_venta(self.inventario, carrito, 1000)
        venta, nuevo, cambio = preparar_venta(self.inventario, carrito, 20000)
        self.assertEqual((venta["total"], cambio), (19000, 1000))
        self.assertEqual(nuevo["BEB001"]["stock"], 2)
        self.assertEqual(self.inventario["BEB001"]["stock"], 5)
        self.assertEqual(calcular_cambio(19000, 19000), 0)

    def test_persistencia_y_agotados(self):
        # TemporaryDirectory crea una carpeta que se borra al terminar el bloque.
        # Se venden todas las unidades, se recargan y se revisa la alerta AGOTADO.
        with tempfile.TemporaryDirectory() as carpeta:
            carpeta = Path(carpeta)
            venta, nuevo, _ = preparar_venta(self.inventario, {"LAC001": 20}, 100000)
            guardar_compra(self.inventario, nuevo, venta, carpeta)
            cargado = cargar_inventario(carpeta / "inventario.txt")
            historial = cargar_ventas(carpeta / "ventas.txt")
            self.assertEqual(cargado, nuevo)
            self.assertEqual(historial, [venta])
            self.assertEqual(cargado["LAC001"]["stock"], 0)
            salida = io.StringIO()
            with contextlib.redirect_stdout(salida):
                mostrar_alertas(cargado)
            self.assertIn("AGOTADO", salida.getvalue())

    def test_archivos_ausentes_y_corruptos(self):
        # Incluye líneas válidas entre líneas dañadas para comprobar que la carga siga.
        # redirect_stdout captura los avisos en memoria en lugar de mostrarlos.
        with tempfile.TemporaryDirectory() as carpeta, contextlib.redirect_stdout(io.StringIO()) as salida:
            inv = Path(carpeta) / "inventario.txt"
            ven = Path(carpeta) / "ventas.txt"
            self.assertEqual(cargar_inventario(inv), {})
            self.assertEqual(cargar_ventas(ven), [])
            inv.write_bytes(b'roto\nA|Leche|Lacteos|5|0|2|Proveedor\n'
                            b'A|Repetido|Lacteos|5|2|2|Proveedor\n\xff\n'
                            b'B|Arroz|Abarrotes|3|2|1|Proveedor\n')
            self.assertEqual(set(cargar_inventario(inv)), {"A", "B"})
            ven.write_text("roto\n2026-11-04|10.0|A:2\n2026-99-01|10|A:1\n"
                           "2026-11-04|nan|A:1\n2026-11-04|10|A:0\n", encoding="utf-8")
            self.assertEqual(len(cargar_ventas(ven)), 1)
            self.assertIn("omitida", salida.getvalue())
            # También se puede anexar si la última línea no tiene salto.
            ven.write_text("2026-11-04|10.0|A:2", encoding="utf-8")
            registrar_venta({"fecha": "2026-11-04", "total": 5.0, "productos": {"A": 1}}, ven)
            self.assertEqual(len(cargar_ventas(ven)), 2)

    def test_error_de_guardado_no_descontar(self):
        # patch simula un disco lleno sin provocar un problema real en el equipo.
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "inventario.txt"
            guardar_inventario(self.inventario, ruta)
            venta, nuevo, _ = preparar_venta(self.inventario, {"LAC001": 1}, 5000)
            with patch("persistencia.registrar_venta", side_effect=OSError("Disco lleno")):
                with self.assertRaises(OSError):
                    guardar_compra(self.inventario, nuevo, venta, carpeta)
            self.assertEqual(cargar_inventario(ruta), self.inventario)

    def test_cierre_fecha_empates_y_productos_eliminados(self):
        # Usa fechas fijas para que el resultado no dependa del día de ejecución.
        registrar_producto(self.inventario, producto("B", 2000, 3))
        registrar_producto(self.inventario, producto("C", 2000, 3))
        ventas = [{"fecha": "2026-11-04", "total": 14000,
                   "productos": {"LAC001": 2, "B": 2, "BORRADO": 1}},
                  {"fecha": "2026-11-03", "total": 10000, "productos": {"C": 5}}]
        r = cierre_dia(self.inventario, ventas, "2026-11-04")
        self.assertEqual((r["total"], r["cantidad"], r["promedio"]), (14000, 1, 14000))
        self.assertEqual(set(r["mas_vendidos"]), {"LAC001", "B"})
        self.assertEqual([p["codigo"] for p in r["sin_ventas"]], ["C"])
        self.assertEqual(r["categorias"]["Producto eliminado"], 1)
        self.assertEqual(cierre_dia(self.inventario, [], "2026-11-04")["promedio"], 0)
        self.assertEqual(len(alertas_stock(self.inventario)["Proveedor de prueba"]), 2)

    def test_captura_numeros_y_cancelacion(self):
        # patch sustituye input; side_effect entrega las respuestas en orden.
        with patch("builtins.input", side_effect=["hola", "-1", "0", "nan", "3"]), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(leer_numero("Cantidad: ", True), 3)
        for entradas in [["LAC001", "2", "cancelar"], ["LAC001", "2", "fin", "1", "10000", "n"]]:
            with patch("builtins.input", side_effect=entradas), contextlib.redirect_stdout(io.StringIO()):
                historial = []
                main.vender(self.inventario, historial)
                self.assertEqual(historial, [])
                self.assertEqual(self.inventario["LAC001"]["stock"], 20)

    def test_menu_confirmacion_y_reinicio_real(self):
        # subprocess abre otro Python para comprobar un cierre y una reapertura reales.
        with tempfile.TemporaryDirectory() as carpeta:
            carpeta = Path(carpeta)
            guardar_inventario(self.inventario, carpeta / "inventario.txt")
            (carpeta / "ventas.txt").write_text("", encoding="utf-8")
            # Ejecutar el menú en otro proceso, sin tocar los datos de ejemplo.
            script = ("import sys; sys.path.insert(0, sys.argv[1]); "
                      "import persistencia, main; from pathlib import Path; "
                      "persistencia.DATA=Path(sys.argv[2]); main.main()")
            comando = [sys.executable, "-c", script,
                       str(Path(main.__file__).parent), str(carpeta)]
            resultado = subprocess.run(comando, input="x\n5\nLAC001\n2\nfin\n1\n10000\ns\n0\n",
                                       text=True, capture_output=True)
            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            self.assertIn("Venta guardada", resultado.stdout)
            self.assertIn("Pago insuficiente", resultado.stdout)
            reinicio = subprocess.run(comando, input="2\n3\n0\n", text=True, capture_output=True)
            self.assertEqual(reinicio.returncode, 0, reinicio.stderr)
            self.assertEqual(cargar_inventario(carpeta / "inventario.txt")["LAC001"]["stock"], 18)
            self.assertEqual(len(cargar_ventas(carpeta / "ventas.txt")), 1)


# Permite ejecutar también este archivo directamente para iniciar las pruebas.
if __name__ == "__main__":
    unittest.main()
