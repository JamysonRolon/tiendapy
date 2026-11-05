# Guía para entender TiendaPy

Cada producto es un diccionario. El inventario es otro diccionario que usa el código como llave. De esa manera se puede buscar un producto sin recorrer todos los nombres. El historial es una lista de ventas y cada venta guarda fecha, total y un diccionario de cantidades por código.

## Por dónde empezar

Abre main.py. La función main carga los archivos y entra en un while True que muestra el menú. Cada opción llama a una función. La opción 0 guarda y usa break para terminar. Los errores de negocio llegan como ValueError y el menú los captura para mostrar un mensaje y continuar.

En validaciones.py están las comprobaciones que se repiten. leer_numero pide otra entrada cuando el usuario escribe texto o un número no permitido. numero_positivo también se usa desde las funciones del negocio: una regla no depende solamente de que el usuario haya pasado por una pantalla concreta.

inventario.py contiene el registro, las búsquedas, la modificación y la eliminación. Antes de modificar precio y stock se revisan ambos valores. Si uno está mal, no se cambia ninguno.

## Cómo se hace una venta

El carrito comienza como un diccionario vacío. agregar_al_carrito toma el código, revisa su existencia y comprueba el stock. Si el producto ya estaba en el carrito, suma las cantidades antes de validar.

calcular_venta recorre el carrito, suma los importes y aplica el descuento correspondiente. Se revisa primero el umbral de 100000, porque también cumple la condición de ser mayor o igual a 50000.

preparar_venta valida el pago y prepara una copia del inventario con las nuevas existencias. Todavía no cambia el inventario original. Después de la confirmación, guardar_compra escribe los archivos. Solo si ese paso termina se actualizan el inventario y el historial de la sesión.

## Cómo se leen los archivos

persistencia.py usa with para cerrar los archivos incluso si ocurre un error. La lectura separa cada línea por sus delimitadores y convierte los campos numéricos. Una línea inválida genera un aviso y la lectura sigue con la siguiente.

El inventario se escribe primero en un archivo temporal. Cuando termina, ese archivo reemplaza al anterior. El historial se abre para agregar al final y no borrar ventas anteriores.

## Cómo se arman los reportes

alertas_stock recorre el inventario y agrupa por proveedor los productos cuyo stock es menor o igual al mínimo. mostrar_alertas usa la palabra AGOTADO para los que tienen cero unidades.

cierre_dia filtra las ventas de una fecha. Luego suma los totales y cuenta las unidades de cada código. La lista de productos sin ventas se obtiene comparando esos códigos con el inventario actual.

## Preguntas para practicar

1. ¿Por qué no se descuenta el stock al agregar un producto al carrito?
2. ¿Qué ocurre si agregas 12 unidades y después 9, pero solamente hay 20?
3. ¿Por qué se usa elif para el descuento del 5 %?
4. ¿Qué diferencia hay entre registrar stock cero y vender la última unidad?
5. ¿Para qué sirven raise y except en este programa?
6. ¿Qué información se pierde al eliminar un producto si el historial solo guarda su código?

Para revisar las respuestas, sigue las funciones indicadas en esta guía y ejecuta las pruebas. Cambia un valor de prueba y observa cuál comprobación falla; hazlo sobre una copia para conservar la versión que funciona.
