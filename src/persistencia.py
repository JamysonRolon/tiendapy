from datetime import date
from pathlib import Path
import os

from inventario import validar_producto
from validaciones import numero_positivo, texto_valido


DATA = Path(__file__).resolve().parent.parent / "data"


def cargar_inventario(ruta=None):
    ruta = Path(ruta) if ruta is not None else DATA / "inventario.txt"
    inventario = {}
    try:
        with open(ruta, "rb") as archivo:
            for numero, linea in enumerate(archivo, 1):
                try:
                    campos = linea.decode("utf-8-sig").strip().split("|")
                    if len(campos) != 7:
                        raise ValueError("Se esperaban 7 campos.")
                    producto = validar_producto(dict(zip(
                        ["codigo", "nombre", "categoria", "precio", "stock",
                         "stock_minimo", "proveedor"], campos)), desde_archivo=True)
                    if producto["codigo"] in inventario:
                        raise ValueError("Código repetido.")
                    inventario[producto["codigo"]] = producto
                except (ValueError, UnicodeError) as error:
                    print(f"Advertencia: inventario, línea {numero} omitida. {error}")
    except FileNotFoundError:
        print("No existe inventario.txt. Se iniciará con el inventario vacío.")
    return inventario


def guardar_inventario(inventario, ruta=None):
    ruta = Path(ruta) if ruta is not None else DATA / "inventario.txt"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    temporal = ruta.with_suffix(".tmp")
    try:
        with open(temporal, "w", encoding="utf-8") as archivo:
            for p in inventario.values():
                archivo.write(f'{p["codigo"]}|{p["nombre"]}|{p["categoria"]}|'
                              f'{p["precio"]}|{p["stock"]}|{p["stock_minimo"]}|'
                              f'{p["proveedor"]}\n')
        os.replace(temporal, ruta)
    finally:
        if temporal.exists():
            temporal.unlink()


def cargar_ventas(ruta=None):
    ruta = Path(ruta) if ruta is not None else DATA / "ventas.txt"
    ventas = []
    try:
        with open(ruta, "rb") as archivo:
            for numero, linea in enumerate(archivo, 1):
                try:
                    fecha, total, detalle = linea.decode("utf-8-sig").strip().split("|")
                    if date.fromisoformat(fecha).isoformat() != fecha:
                        raise ValueError("Fecha inválida.")
                    total = numero_positivo(total)
                    productos = {}
                    for item in detalle.split(";"):
                        codigo, cantidad = item.split(":")
                        codigo = texto_valido(codigo).upper()
                        if codigo in productos:
                            raise ValueError("Producto repetido en la venta.")
                        productos[codigo] = numero_positivo(cantidad, True)
                    ventas.append({"fecha": fecha, "total": total, "productos": productos})
                except (ValueError, UnicodeError) as error:
                    print(f"Advertencia: ventas, línea {numero} omitida. {error}")
    except FileNotFoundError:
        print("No existe ventas.txt. Todavía no hay ventas registradas.")
    return ventas


def registrar_venta(venta, ruta=None):
    ruta = Path(ruta) if ruta is not None else DATA / "ventas.txt"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    detalle = ";".join(codigo + ":" + str(cantidad)
                       for codigo, cantidad in venta["productos"].items())
    # Si falla la escritura, quitar cualquier fragmento de esta venta.
    with open(ruta, "a+b") as archivo:
        archivo.seek(0, 2)
        inicio = archivo.tell()
        separador = ""
        if inicio:
            archivo.seek(-1, 2)
            if archivo.read(1) != b"\n":
                separador = "\n"
        try:
            linea = f'{separador}{venta["fecha"]}|{venta["total"]}|{detalle}\n'
            archivo.write(linea.encode("utf-8"))
            archivo.flush()
        except OSError:
            archivo.truncate(inicio)
            raise


def guardar_compra(anterior, nuevo, venta, carpeta=None):
    carpeta = Path(carpeta) if carpeta is not None else DATA
    guardar_inventario(nuevo, carpeta / "inventario.txt")
    try:
        registrar_venta(venta, carpeta / "ventas.txt")
    except OSError:
        # Recuperar las existencias si no se pudo guardar el comprobante.
        guardar_inventario(anterior, carpeta / "inventario.txt")
        raise
