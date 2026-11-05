from datetime import date

from inventario import buscar_codigo
from validaciones import numero_positivo


def agregar_al_carrito(inventario, carrito, codigo, cantidad):
    producto = buscar_codigo(inventario, codigo)
    cantidad = numero_positivo(cantidad, True)
    codigo = producto["codigo"]
    cantidad_total = carrito.get(codigo, 0) + cantidad
    if cantidad_total > producto["stock"]:
        raise ValueError("No alcanza el stock. Disponibles: " + str(producto["stock"]))
    carrito[codigo] = cantidad_total


def calcular_venta(inventario, carrito):
    if not carrito:
        raise ValueError("El carrito está vacío.")
    subtotal = 0.0
    for codigo, cantidad in carrito.items():
        producto = buscar_codigo(inventario, codigo)
        numero_positivo(cantidad, True)
        if cantidad > producto["stock"]:
            raise ValueError("No alcanza el stock de " + producto["nombre"])
        subtotal += round(producto["precio"] * cantidad, 2)
    subtotal = round(numero_positivo(subtotal), 2)
    porcentaje = 0
    if subtotal >= 100000:
        porcentaje = 10
    elif subtotal >= 50000:
        porcentaje = 5
    descuento = round(subtotal * porcentaje / 100, 2)
    total = round(subtotal - descuento, 2)
    return {"subtotal": subtotal, "porcentaje": porcentaje,
            "descuento": descuento, "total": total}


def calcular_cambio(total, pago):
    pago = round(numero_positivo(pago), 2)
    if pago < total:
        raise ValueError("Pago insuficiente. Debes recibir al menos $" + format(total, ".2f"))
    return round(pago - total, 2)


def preparar_venta(inventario, carrito, pago):
    resumen = calcular_venta(inventario, carrito)
    cambio = calcular_cambio(resumen["total"], pago)
    venta = {"fecha": date.today().isoformat(), "total": resumen["total"],
             "productos": carrito.copy()}
    nuevo_inventario = {}
    for codigo, producto in inventario.items():
        nuevo_inventario[codigo] = producto.copy()
        nuevo_inventario[codigo]["stock"] -= carrito.get(codigo, 0)
    return venta, nuevo_inventario, cambio
