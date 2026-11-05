from datetime import date
from tabulate import tabulate

from inventario import (registrar_producto, buscar_codigo, buscar_categoria,
                        modificar_producto, eliminar_producto, mostrar_productos)
from ventas import agregar_al_carrito, calcular_venta, calcular_cambio, preparar_venta
from persistencia import cargar_inventario, cargar_ventas, guardar_inventario, guardar_compra
from reportes import mostrar_alertas, mostrar_cierre
from validaciones import leer_texto, leer_numero, confirmar, categoria_valida


def registrar(inventario):
    codigo = leer_texto("Código: ").upper()
    if codigo in inventario:
        raise ValueError("Ya existe un producto con ese código.")
    nombre = leer_texto("Nombre: ")
    while True:
        try:
            categoria = categoria_valida(leer_texto("Categoría (Lacteos, Bebidas, Aseo, Abarrotes, Snacks): "))
            break
        except ValueError as error:
            print(error)
    precio = leer_numero("Precio en COP (usa punto para los decimales): ")
    if round(precio, 2) == 0:
        raise ValueError("El precio debe ser al menos 0.01 COP.")
    producto = {"codigo": codigo, "nombre": nombre, "categoria": categoria,
                "precio": round(precio, 2), "stock": leer_numero("Stock: ", True),
                "stock_minimo": leer_numero("Stock mínimo: ", True, True),
                "proveedor": leer_texto("Proveedor: ")}
    registrar_producto(inventario, producto)
    print("Producto registrado.")


def consultar(inventario):
    opcion = input("1. Por código  2. Por categoría  3. Todos: ").strip()
    if opcion == "1":
        mostrar_productos([buscar_codigo(inventario, leer_texto("Código: "))])
    elif opcion == "2":
        mostrar_productos(buscar_categoria(inventario, leer_texto("Categoría: ")))
    elif opcion == "3":
        mostrar_productos(list(inventario.values()))
    else:
        print("Opción inválida.")


def vender(inventario, historial):
    carrito = {}
    while True:
        codigo = input("Código del producto (fin para cobrar, cancelar para volver): ").strip().upper()
        if codigo == "CANCELAR":
            print("Venta cancelada. No se cambió el stock.")
            return
        if codigo == "FIN":
            try:
                resumen = calcular_venta(inventario, carrito)
                break
            except ValueError as error:
                print(error)
                continue
        try:
            buscar_codigo(inventario, codigo)
            cantidad = leer_numero("Cantidad: ", True)
            agregar_al_carrito(inventario, carrito, codigo, cantidad)
            print("Producto agregado.")
        except ValueError as error:
            print(error)
    filas = []
    for codigo, cantidad in carrito.items():
        p = inventario[codigo]
        filas.append([p["nombre"], cantidad, p["precio"], round(p["precio"] * cantidad, 2)])
    print(tabulate(filas, headers=["Producto", "Cantidad", "Precio", "Valor COP"], floatfmt=".2f"))
    print(f'Subtotal: ${resumen["subtotal"]:.2f}')
    print(f'Descuento ({resumen["porcentaje"]}%): ${resumen["descuento"]:.2f}')
    print(f'Total: ${resumen["total"]:.2f}')
    while True:
        pago = leer_numero("Pago recibido en COP: ")
        try:
            cambio = calcular_cambio(resumen["total"], pago)
            break
        except ValueError as error:
            print(error)
    print(f"Cambio: ${cambio:.2f}")
    if not confirmar("¿Confirmar venta?"):
        print("Venta cancelada. No se cambió el stock.")
        return
    venta, nuevo, cambio = preparar_venta(inventario, carrito, pago)
    guardar_compra(inventario, nuevo, venta)
    inventario.clear()
    inventario.update(nuevo)
    historial.append(venta)
    print(f"Venta guardada. Entrega ${cambio:.2f} de cambio.")


def main():
    print("TIENDAPY - Tienda Don Aurelio")
    try:
        inventario = cargar_inventario()
        historial = cargar_ventas()
    except OSError as error:
        print("No se pudieron leer los archivos. Revisa los permisos:", error)
        return
    while True:
        print("\n1. Registrar producto\n2. Consultar inventario\n3. Modificar precio y stock"
              "\n4. Eliminar producto\n5. Registrar venta\n6. Alertas de stock"
              "\n7. Cierre del día\n8. Guardar inventario\n0. Guardar y salir")
        try:
            opcion = input("Elige una opción: ").strip()
            if opcion == "1":
                registrar(inventario)
            elif opcion == "2":
                consultar(inventario)
            elif opcion == "3":
                codigo = leer_texto("Código: ")
                mostrar_productos([buscar_codigo(inventario, codigo)])
                precio = round(leer_numero("Nuevo precio: "), 2)
                stock = leer_numero("Nuevo stock: ", True)
                modificar_producto(inventario, codigo, precio, stock)
                print("Producto modificado.")
            elif opcion == "4":
                codigo = leer_texto("Código: ")
                mostrar_productos([buscar_codigo(inventario, codigo)])
                if confirmar("¿Eliminar este producto?"):
                    eliminar_producto(inventario, codigo)
                    print("Producto eliminado.")
            elif opcion == "5":
                vender(inventario, historial)
            elif opcion == "6":
                mostrar_alertas(inventario)
            elif opcion == "7":
                fecha = input("Fecha AAAA-MM-DD (Enter para hoy): ").strip()
                if fecha:
                    if date.fromisoformat(fecha).isoformat() != fecha:
                        raise ValueError("Usa el formato AAAA-MM-DD.")
                mostrar_cierre(inventario, historial, fecha or None)
            elif opcion == "8":
                guardar_inventario(inventario)
                print("Inventario guardado.")
            elif opcion == "0":
                guardar_inventario(inventario)
                print("Inventario guardado. Hasta luego.")
                break
            else:
                print("Opción inválida. Elige un número del menú.")
        except ValueError as error:
            print("No se pudo completar la operación:", error)
        except OSError as error:
            print("No se pudo guardar. Revisa el espacio y los permisos:", error)
        except (EOFError, KeyboardInterrupt):
            print("\nEntrada interrumpida. Guardando inventario...")
            try:
                guardar_inventario(inventario)
            except OSError as error:
                print("No se pudo guardar:", error)
            break


if __name__ == "__main__":
    main()
