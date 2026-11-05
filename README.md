# TiendaPy

Aplicación de consola para llevar el inventario y las ventas de la tienda Don Aurelio. Permite registrar productos, armar un carrito, cobrar y revisar qué mercancía hace falta. Los datos quedan en archivos de texto para poder cerrar el programa y seguir después.

El programa usa funciones, listas y diccionarios. No necesita clases, base de datos ni una interfaz gráfica. La única librería externa es tabulate, que permite mostrar tablas legibles en la consola y está recomendada en el enunciado.

## Cómo ejecutarlo

Necesitas Python 3.10 o superior. Abre una terminal dentro de la carpeta tiendapy.

En Windows, crea el entorno virtual:

```powershell
py -m venv .venv
```

Instala la dependencia y abre el programa:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src\main.py
```

No hace falta activar el entorno ni cambiar la política de ejecución de PowerShell. Si tu instalación usa el comando python en lugar de py, puedes usar python para crear el entorno.

En este equipo ya quedó creado el entorno, con la dependencia instalada. Puedes abrir la aplicación con iniciar.bat o ejecutar el último comando desde la carpeta del proyecto. Si mueves el proyecto a otro equipo, crea nuevamente el entorno: los entornos virtuales no son portables.

En Linux o macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python src/main.py
```

## Opciones del menú

| Opción | Qué permite hacer |
| --- | --- |
| 1 | Registrar código, nombre, categoría, precio, stock, mínimo y proveedor. |
| 2 | Consultar por código, por categoría o mostrar todos los productos. |
| 3 | Cambiar el precio y el stock de un producto existente. |
| 4 | Eliminar un producto después de confirmar. |
| 5 | Agregar varios productos a una venta, recibir el pago y calcular el cambio. |
| 6 | Ver productos con stock bajo o agotado, agrupados por proveedor. |
| 7 | Consultar el cierre de hoy o de otra fecha. |
| 8 | Guardar el inventario sin salir. |
| 0 | Guardar el inventario y cerrar. |

Los cambios de inventario se guardan con las opciones 8 y 0. Una venta confirmada guarda inmediatamente el inventario y su registro en el historial. Escribe fin para cobrar el carrito o cancelar para volver al menú sin descontar existencias. Un pago insuficiente permite volver a intentar.

## Ejemplo para probar una venta

Los archivos incluidos contienen cinco productos y una venta de ejemplo del 4 de noviembre de 2026. Esa venta es independiente del inventario inicial: el stock del archivo representa las existencias disponibles al comenzar la demostración.

1. Elige la opción 5.
2. Agrega LAC001 con cantidad 2.
3. Agrega BEB003 con cantidad 1.
4. Escribe fin.
5. El subtotal y el total deben ser 14200 COP, sin descuento.
6. Ingresa primero 10000 para comprobar el rechazo y después 20000.
7. El cambio debe ser 5800 COP. Confirma con s.
8. Consulta el inventario: quedan 33 unidades de leche y 7 de gaseosa.
9. Sal con 0 y vuelve a abrir. Las existencias y la venta deben seguir guardadas.

El ejemplo modifica los datos. Guarda una copia de la carpeta data antes de hacer la demostración si quieres conservar el punto de partida.

## Reglas y decisiones

Los códigos se convierten a mayúsculas y no pueden repetirse. Las búsquedas por categoría aceptan mayúsculas y tildes. Se admiten Lacteos, Bebidas, Aseo, Abarrotes y Snacks.

Los precios y las cantidades deben ser positivos. Al registrar o modificar, el stock debe ser mayor que cero. El mínimo puede ser cero. Una venta sí puede dejar el stock en cero y un archivo puede contener productos agotados. Esta distinción resuelve la diferencia entre CR-02, que rechaza el ingreso manual de stock cero, y la regla que exige mostrar agotados.

Si agregas dos veces un mismo código al carrito, las cantidades se suman. La validación revisa esa suma contra las unidades disponibles. Cancelar o intentar vender más de lo disponible conserva el inventario.

| Subtotal | Descuento |
| --- | --- |
| Menor de 50000 COP | 0 % |
| Desde 50000 y menor de 100000 COP | 5 % |
| Desde 100000 COP | 10 % |

Los descuentos no se acumulan. Los importes se calculan con float, como pide el modelo de datos, y se redondean a dos decimales. Usa punto decimal y no escribas separadores de miles.

## Archivos y organización

```text
tiendapy/
  README.md
  GUIA_DEL_CODIGO.md
  VERIFICACION.md
  requirements.txt
  iniciar.bat
  data/
    inventario.txt
    ventas.txt
  src/
    main.py
    inventario.py
    ventas.py
    reportes.py
    persistencia.py
    validaciones.py
  tests/
    test_tiendapy.py
```

El inventario usa siete campos separados por |. El historial conserva fecha, total y los pares de código y cantidad, con los separadores indicados en el PDF. No se permite introducir esos separadores dentro de los textos de un producto.

Las rutas se resuelven desde la ubicación del programa. Si falta el inventario, aparece un aviso y se puede empezar vacío. Si falta el historial, se comienza sin ventas. Las líneas dañadas se omiten con una advertencia que indica su número; las demás se cargan. Al guardar el inventario, el archivo se reemplaza con los registros válidos que están en memoria, por lo que conviene respaldar un archivo dañado antes de seguir.

## Qué muestra el cierre

El total vendido es la suma de los totales después del descuento. El ticket promedio divide ese valor entre las transacciones de la fecha elegida. El producto más vendido se determina por unidades y, si hay empate, se muestran todos. Los productos sin ventas son los del inventario actual que no tuvieron movimiento en esa fecha. También se muestran las unidades vendidas por categoría.

El formato obligatorio del historial solo guarda códigos y cantidades, sin una copia del nombre o la categoría. Si se elimina un producto vendido, el cierre conserva sus unidades y el total, pero lo identifica por código como Producto eliminado. Para esos productos la categoría original no puede recuperarse. No reutilices códigos eliminados para productos distintos.

## Comprobar el funcionamiento

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Las pruebas usan datos temporales y no cambian los ejemplos. VERIFICACION.md relaciona los criterios del PDF con el código y los casos revisados.

El guardado usa un archivo temporal para evitar reemplazar el inventario con una escritura incompleta. Si falla el registro de una venta, se intenta recuperar el inventario anterior y se informa el error. Es una aplicación para una sola consola: no coordina varios procesos ni garantiza una transacción entre los dos archivos frente a un corte de energía. Conviene conservar copias de data.

## Entrega en GitHub

El repositorio Git local conserva los commits de esta implementación. Su autor técnico figura como Codex para no atribuir esos cambios a una persona sin sus datos. El entorno virtual queda fuera de Git y se reconstruye con requirements.txt.

La creación y publicación del repositorio en GitHub quedan pendientes, según lo acordado. Antes de entregar, revisa el código, practica la demostración y añade los datos reales de los integrantes que solicite el curso. No se han inventado nombres de estudiantes ni experiencias de aprendizaje.
