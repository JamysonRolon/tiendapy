from tabulate import tabulate

from validaciones import texto_valido, numero_positivo, categoria_valida, normalizar


def validar_producto(producto, desde_archivo=False):
    return {
        "codigo": texto_valido(producto["codigo"]).upper(),
        "nombre": texto_valido(producto["nombre"]),
        "categoria": categoria_valida(producto["categoria"]),
        "precio": numero_positivo(producto["precio"]),
        # Un producto agotado sí debe poder cargarse al abrir el programa.
        "stock": numero_positivo(producto["stock"], True, desde_archivo),
        "stock_minimo": numero_positivo(producto["stock_minimo"], True, True),
        "proveedor": texto_valido(producto["proveedor"]),
    }


def registrar_producto(inventario, producto):
    nuevo = validar_producto(producto)
    if nuevo["codigo"] in inventario:
        raise ValueError("Ya existe un producto con ese código.")
    inventario[nuevo["codigo"]] = nuevo


def buscar_codigo(inventario, codigo):
    codigo = codigo.strip().upper()
    if codigo not in inventario:
        raise ValueError("No se encontró un producto con ese código.")
    return inventario[codigo]


def buscar_categoria(inventario, categoria):
    return [p for p in inventario.values()
            if normalizar(p["categoria"]) == normalizar(categoria)]


def modificar_producto(inventario, codigo, precio, stock):
    producto = buscar_codigo(inventario, codigo)
    # Revisar ambos antes de cambiar algo evita una modificación a medias.
    precio = numero_positivo(precio)
    stock = numero_positivo(stock, True)
    producto["precio"] = precio
    producto["stock"] = stock


def eliminar_producto(inventario, codigo):
    producto = buscar_codigo(inventario, codigo)
    del inventario[producto["codigo"]]


def mostrar_productos(productos):
    if not productos:
        print("No hay productos para mostrar.")
        return
    filas = []
    for p in productos:
        filas.append([p["codigo"], p["nombre"], p["categoria"], p["precio"],
                      p["stock"], p["stock_minimo"], p["proveedor"]])
    print(tabulate(filas, headers=["Código", "Nombre", "Categoría", "Precio COP",
                                   "Stock", "Mínimo", "Proveedor"], floatfmt=".2f"))
