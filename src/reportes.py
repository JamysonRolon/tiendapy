from datetime import date
from tabulate import tabulate


def alertas_stock(inventario):
    proveedores = {}
    for producto in inventario.values():
        if producto["stock"] <= producto["stock_minimo"]:
            proveedor = producto["proveedor"]
            if proveedor not in proveedores:
                proveedores[proveedor] = []
            proveedores[proveedor].append(producto)
    return proveedores


def mostrar_alertas(inventario):
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
    fecha = fecha or date.today().isoformat()
    del_dia = [venta for venta in ventas if venta["fecha"] == fecha]
    total = round(sum(venta["total"] for venta in del_dia), 2)
    unidades = {}
    categorias = {}
    for venta in del_dia:
        for codigo, cantidad in venta["productos"].items():
            unidades[codigo] = unidades.get(codigo, 0) + cantidad
            categoria = inventario[codigo]["categoria"] if codigo in inventario else "Producto eliminado"
            categorias[categoria] = categorias.get(categoria, 0) + cantidad
    mas_vendidos = []
    if unidades:
        mayor = max(unidades.values())
        mas_vendidos = [codigo for codigo in unidades if unidades[codigo] == mayor]
    sin_ventas = [p for codigo, p in inventario.items() if codigo not in unidades]
    promedio = round(total / len(del_dia), 2) if del_dia else 0.0
    return {"fecha": fecha, "total": total, "cantidad": len(del_dia),
            "promedio": promedio, "mas_vendidos": mas_vendidos,
            "unidades": unidades, "sin_ventas": sin_ventas, "categorias": categorias}


def mostrar_cierre(inventario, ventas, fecha=None):
    reporte = cierre_dia(inventario, ventas, fecha)
    print("\nCierre del día", reporte["fecha"])
    print(f'Total vendido: ${reporte["total"]:.2f} COP')
    print("Número de ventas:", reporte["cantidad"])
    print(f'Ticket promedio: ${reporte["promedio"]:.2f} COP')
    print("Producto(s) más vendido(s), por unidades:")
    if not reporte["mas_vendidos"]:
        print("Todavía no hay ventas en esta fecha.")
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
