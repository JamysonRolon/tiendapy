# Aca guardamos los datos para que sigan cuando abramos el programa otra vez.
from datetime import date
from pathlib import Path
import os

from inventario import validar_producto
from validaciones import numero_positivo, texto_valido


# __file__ es este archivo. Subimos de src a tiendapy y buscamos la carpeta data.
# Así las rutas no dependen de la carpeta desde la que se abra la terminal.
DATA = Path(__file__).resolve().parent.parent / "data"


def cargar_inventario(ruta=None):
    # ruta permite usar otro archivo en las pruebas; normalmente se usa DATA.
    ruta = Path(ruta) if ruta is not None else DATA / "inventario.txt"
    inventario = {}
    try:
        # with cierra el archivo al salir del bloque, incluso si aparece un error.
        # rb lee bytes para detectar una línea mal codificada y seguir con las demás.
        with open(ruta, "rb") as archivo:
            for numero, linea in enumerate(archivo, 1):
                try:
                    # decode convierte bytes en texto y split separa los siete campos.
                    campos = linea.decode("utf-8-sig").strip().split("|")
                    if len(campos) != 7:
                        raise ValueError("Se esperaban 7 campos.")
                    # zip empareja cada nombre de atributo con su valor en la línea.
                    # dict crea el producto y validar_producto convierte sus números.
                    producto = validar_producto(dict(zip(
                        ["codigo", "nombre", "categoria", "precio", "stock",
                         "stock_minimo", "proveedor"], campos)), desde_archivo=True)
                    if producto["codigo"] in inventario:
                        raise ValueError("Código repetido.")
                    inventario[producto["codigo"]] = producto
                # Este except afecta solo a esta línea; el for sigue con la siguiente.
                except (ValueError, UnicodeError) as error:
                    print(f"Advertencia: inventario, línea {numero} omitida. {error}")
    except FileNotFoundError:
        print("No existe inventario.txt. Se iniciará con el inventario vacío.")
    return inventario


def guardar_inventario(inventario, ruta=None):
    # Escribe el inventario completo; crea la carpeta si todavía no existe.
    ruta = Path(ruta) if ruta is not None else DATA / "inventario.txt"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    # Primero se escribe inventario.tmp para no tocar el original a medio guardar.
    temporal = ruta.with_suffix(".tmp")
    try:
        with open(temporal, "w", encoding="utf-8") as archivo:
            for p in inventario.values():
                # Cada producto ocupa una línea, con los campos separados por |.
                archivo.write(f'{p["codigo"]}|{p["nombre"]}|{p["categoria"]}|'
                              f'{p["precio"]}|{p["stock"]}|{p["stock_minimo"]}|'
                              f'{p["proveedor"]}\n')
        # Reemplaza el archivo anterior solo cuando terminó de escribir el temporal.
        os.replace(temporal, ruta)
    finally:
        # finally se ejecuta con o sin error y elimina un temporal que haya quedado.
        if temporal.exists():
            temporal.unlink()


def cargar_ventas(ruta=None):
    # Reconstruye la lista de ventas desde fecha|total|codigo:cantidad;codigo:cantidad.
    ruta = Path(ruta) if ruta is not None else DATA / "ventas.txt"
    ventas = []
    try:
        with open(ruta, "rb") as archivo:
            for numero, linea in enumerate(archivo, 1):
                try:
                    fecha, total, detalle = linea.decode("utf-8-sig").strip().split("|")
                    # Además del formato, comprueba que la fecha exista en el calendario.
                    if date.fromisoformat(fecha).isoformat() != fecha:
                        raise ValueError("Fecha inválida.")
                    total = numero_positivo(total)
                    productos = {}
                    # Primero separa productos con ; y luego código y cantidad con :.
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
    # La venta se agrega al final, asi no borramos las que ya estaban.
    ruta = Path(ruta) if ruta is not None else DATA / "ventas.txt"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    # join une todos los pares código:cantidad con un punto y coma entre ellos.
    detalle = ";".join(codigo + ":" + str(cantidad)
                       for codigo, cantidad in venta["productos"].items())
    # Si falla la escritura, quitar cualquier fragmento de esta venta.
    # a+b permite leer y agregar bytes al final; también crea el archivo si falta.
    with open(ruta, "a+b") as archivo:
        archivo.seek(0, 2)
        # tell guarda la posición de inicio para deshacer una escritura incompleta.
        inicio = archivo.tell()
        separador = ""
        if inicio:
            # seek(-1, 2) se ubica en el último byte, contando desde el final.
            archivo.seek(-1, 2)
            if archivo.read(1) != b"\n":
                separador = "\n"
        try:
            linea = f'{separador}{venta["fecha"]}|{venta["total"]}|{detalle}\n'
            archivo.write(linea.encode("utf-8"))
            archivo.flush()  # Envía al archivo los datos pendientes de escritura.
        except OSError:
            archivo.truncate(inicio)  # Recupera el tamaño que tenía antes de esta venta.
            raise


def guardar_compra(anterior, nuevo, venta, carpeta=None):
    # Guarda las existencias nuevas y luego agrega la venta al historial.
    # Si falla el historial, intenta restaurar las existencias anteriores.
    carpeta = Path(carpeta) if carpeta is not None else DATA
    guardar_inventario(nuevo, carpeta / "inventario.txt")
    try:
        registrar_venta(venta, carpeta / "ventas.txt")
    except OSError:
        # Recuperar las existencias si no se pudo guardar el comprobante.
        guardar_inventario(anterior, carpeta / "inventario.txt")
        raise
