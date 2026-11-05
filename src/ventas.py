# Este módulo calcula ventas. Guardarlas en archivos corresponde a persistencia.
from datetime import date

from inventario import buscar_codigo
from validaciones import numero_positivo


def agregar_al_carrito(inventario, carrito, codigo, cantidad):
    # El carrito relaciona códigos con cantidades, sin descontar stock todavía.
    producto = buscar_codigo(inventario, codigo)
    cantidad = numero_positivo(cantidad, True)
    codigo = producto["codigo"]
    # get devuelve 0 si el código aún no estaba. Si ya estaba, suma las unidades.
    cantidad_total = carrito.get(codigo, 0) + cantidad
    if cantidad_total > producto["stock"]:
        raise ValueError("No alcanza el stock. Disponibles: " + str(producto["stock"]))
    carrito[codigo] = cantidad_total


def calcular_venta(inventario, carrito):
    # Comprueba el carrito y devuelve subtotal, descuento y total en un diccionario.
    if not carrito:
        raise ValueError("El carrito está vacío.")
    subtotal = 0.0
    # items permite recorrer a la vez el código y su cantidad.
    for codigo, cantidad in carrito.items():
        producto = buscar_codigo(inventario, codigo)
        numero_positivo(cantidad, True)
        if cantidad > producto["stock"]:
            raise ValueError("No alcanza el stock de " + producto["nombre"])
        subtotal += round(producto["precio"] * cantidad, 2)
    subtotal = round(numero_positivo(subtotal), 2)
    # Se revisa primero el descuento mayor y se aplica solo uno de los dos.
    porcentaje = 0
    if subtotal >= 100000:
        porcentaje = 10
    elif subtotal >= 50000:
        porcentaje = 5
    # round(..., 2) conserva dos decimales en los importes calculados.
    descuento = round(subtotal * porcentaje / 100, 2)
    total = round(subtotal - descuento, 2)
    return {"subtotal": subtotal, "porcentaje": porcentaje,
            "descuento": descuento, "total": total}


def calcular_cambio(total, pago):
    # Rechaza un pago insuficiente; si alcanza, devuelve lo que hay que entregar.
    pago = round(numero_positivo(pago), 2)
    if pago < total:
        raise ValueError("Pago insuficiente. Debes recibir al menos $" + format(total, ".2f"))
    return round(pago - total, 2)


def preparar_venta(inventario, carrito, pago):
    # Prepara los datos de la venta y un inventario nuevo, sin cambiar el original.
    resumen = calcular_venta(inventario, carrito)
    cambio = calcular_cambio(resumen["total"], pago)
    # isoformat escribe la fecha como AAAA-MM-DD; copy separa la venta del carrito.
    venta = {"fecha": date.today().isoformat(), "total": resumen["total"],
             "productos": carrito.copy()}
    nuevo_inventario = {}
    # Se copia también cada producto: copiar solo el diccionario exterior no basta.
    for codigo, producto in inventario.items():
        nuevo_inventario[codigo] = producto.copy()
        nuevo_inventario[codigo]["stock"] -= carrito.get(codigo, 0)
    # Python permite devolver varios valores y recibirlos en tres variables.
    return venta, nuevo_inventario, cambio
