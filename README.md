# TiendaPy

TiendaPy es una aplicación de consola para llevar el inventario y las ventas de la tienda Don Aurelio. Está hecha en Python como proyecto final del curso Python 0 a 100.

## Qué se puede hacer

- Registrar productos, buscarlos por código o categoría, cambiar su precio y stock, y eliminarlos.
- Vender varios productos en una misma compra y calcular el cambio.
- Consultar los productos con stock bajo o agotados, agrupados por proveedor.
- Ver el cierre del día con las ventas, el ticket promedio y los productos más vendidos o sin ventas.

Las compras desde $50.000 COP tienen un descuento del 5 %, y desde $100.000 COP, del 10 %. El programa también revisa que haya existencias suficientes y que el pago alcance.

## Cómo ejecutarlo

Necesitas Python 3 y la librería `tabulate`, que está en `requirements.txt`.

En Windows, abre una terminal dentro de la carpeta `tiendapy`. Si ya tienes el entorno `.venv` del proyecto, puedes iniciar con:

```powershell
.\.venv\Scripts\python.exe src/main.py
```

Si lo descargaste en otro equipo, crea tu propio entorno e instala la dependencia:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src/main.py
```

Al abrirlo, escribe el número de la opción que quieras usar. Para los precios, usa punto si necesitas decimales. La opción **0** guarda el inventario y cierra el programa.

## Dónde se guarda la información

El inventario se carga desde `data/inventario.txt` y se guarda al salir o al elegir la opción 8. Las ventas confirmadas se agregan a `data/ventas.txt` y descuentan las unidades vendidas del inventario.

Cada producto ocupa una línea con este formato:

```text
codigo|nombre|categoria|precio|stock|stock_minimo|proveedor
```

Las ventas se guardan así:

```text
fecha|total|codigo:cantidad;codigo:cantidad
```

## Organización del código

Los archivos están en `src`: `main.py` maneja el menú, `inventario.py` los productos, `ventas.py` los cálculos de las compras, `reportes.py` las alertas y el cierre, `persistencia.py` los archivos y `validaciones.py` la revisión de los datos ingresados.
