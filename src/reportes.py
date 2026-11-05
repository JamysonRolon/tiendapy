# Los reportes consultan la información: no cambian stock ni registran ventas.
from datetime import date
from tabulate import tabulate


def alertas_stock(inventario):
    # Devuelve un diccionario de proveedor -> lista de productos que hacen falta.
    proveedores = {}
    for producto in inventario.values():
        # El mínimo también cuenta: con stock igual al mínimo ya hay alerta.
        if producto["stock"] <= producto["stock_minimo"]:
            proveedor = producto["proveedor"]
            if proveedor not in proveedores:
                proveedores[proveedor] = []
            proveedores[proveedor].append(producto)
    return proveedores


def mostrar_alertas(inventario):
    # Presenta una tabla por proveedor y distingue los productos agotados.
    grupos = alertas_stock(inventario)
    if not grupos:
        print("No hay productos con stock bajo.")
    for proveedor, productos in grupos.items():
        print("\nProveedor:", proveedor)
        filas = []
        for p in productos:
            estado = "AGOTADO" if p["stock"] == 0 else "Stock bajo"
            filas.append([p["codigo"], p["nombre"], p["stock"], p["stock_minimo"], estado])
        print(tabulate(filas, headers=["Código", "Producto", "Stock", "Mínimo", "Estado"]))


def cierre_dia(inventario, ventas, fecha=None):
    # Calcula el reporte de la fecha solicitada; si no hay fecha, usa hoy.
    fecha = fecha or date.today().isoformat()
    # La lista conserva únicamente las ventas cuya fecha coincide con la elegida.
    del_dia = [venta for venta in ventas if venta["fecha"] == fecha]
    total = round(sum(venta["total"] for venta in del_dia), 2)
    # Estos diccionarios acumulan cantidades por código y por categoría.
    unidades = {}
    categorias = {}
    for venta in del_dia:
        for codigo, cantidad in venta["productos"].items():
            unidades[codigo] = unidades.get(codigo, 0) + cantidad
            # El historial conserva el código aunque el producto se haya eliminado.
            categoria = inventario[codigo]["categoria"] if codigo in inventario else "Producto eliminado"
            categorias[categoria] = categorias.get(categoria, 0) + cantidad
    # Primero encuentra la mayor cantidad y después todos los códigos empatados.
    mas_vendidos = []
    if unidades:
        mayor = max(unidades.values())
        mas_vendidos = [codigo for codigo in unidades if unidades[codigo] == mayor]
    # Un producto sin ventas no aparece entre los códigos contados en esa fecha.
    sin_ventas = [p for codigo, p in inventario.items() if codigo not in unidades]
    # Evita dividir entre cero cuando no hubo transacciones.
    promedio = round(total / len(del_dia), 2) if del_dia else 0.0
    return {"fecha": fecha, "total": total, "cantidad": len(del_dia),
            "promedio": promedio, "mas_vendidos": mas_vendidos,
            "unidades": unidades, "sin_ventas": sin_ventas, "categorias": categorias}


def mostrar_cierre(inventario, ventas, fecha=None):
    # Usa los cálculos anteriores para mostrar el cierre con mensajes y tablas.
    reporte = cierre_dia(inventario, ventas, fecha)
    print("\nCierre del día", reporte["fecha"])
    print(f'Total vendido: ${reporte["total"]:.2f} COP')
    print("Número de ventas:", reporte["cantidad"])
    print(f'Ticket promedio: ${reporte["promedio"]:.2f} COP')
    print("Producto(s) más vendido(s), por unidades:")
    if not reporte["mas_vendidos"]:
        print("Todavía no hay ventas en esta fecha.")
    # Si el producto ya no está, muestra su código y conserva sus unidades vendidas.
    for codigo in reporte["mas_vendidos"]:
        nombre = inventario[codigo]["nombre"] if codigo in inventario else "Producto eliminado"
        print(codigo, nombre, "-", reporte["unidades"][codigo], "unidades")
    print("Productos sin ventas en esta fecha:")
    if not reporte["sin_ventas"]:
        print("Ninguno.")
    for producto in reporte["sin_ventas"]:
        print(producto["codigo"], producto["nombre"])
    print("Categorías con movimiento (unidades):")
    if reporte["categorias"]:
        print(tabulate(list(reporte["categorias"].items()), headers=["Categoría", "Unidades"]))
    else:
        print("Ninguna.")
