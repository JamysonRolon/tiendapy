# Revisión de requisitos

Se revisaron los trece criterios funcionales y los seis de robustez del enunciado. La ejecución automatizada contiene once métodos de prueba; varios métodos comprueban más de un caso. También se prueba el menú en un proceso independiente y se vuelve a abrir con los mismos archivos temporales.

| Criterio | Implementación y comprobación |
| --- | --- |
| CF-01 | main carga el inventario antes del menú; la prueba de reinicio ejecuta ese recorrido. |
| CF-02 | El menú usa while True; la prueba introduce una opción inválida, vende y sale con 0. |
| CF-03 | registrar_producto valida todos los atributos y rechaza códigos repetidos, incluso con distinta capitalización. |
| CF-04 | buscar_codigo y buscar_categoria; pruebas con código existente, inexistente y categoría con tilde. |
| CF-05 | modificar_producto y eliminar_producto; prueba de cambios y eliminación. |
| CF-06 | Carrito con leche y un segundo producto; el flujo de consola muestra nombre, cantidad, precio e importe. |
| CF-07 | Casos de subtotal 49999, 50000, 99999, 100000 y 150000. |
| CF-08 | Pago insuficiente, reintento, pago exacto y cambio positivo. |
| CF-09 | Un código agregado dos veces no supera el stock; los rechazos conservan las existencias. |
| CF-10 | Confirmación desde el menú, escritura del historial y descuento de stock verificados. |
| CF-11 | Agrupación por proveedor y comprobación de la etiqueta AGOTADO. |
| CF-12 | Total, transacciones, promedio, empates, productos sin ventas y fecha sin movimientos. También se cuentan categorías. |
| CF-13 | Guardado, lectura y reinicio real en otro proceso con los mismos datos. |
| CR-01 | Entradas de texto, números negativos y valores no finitos se rechazan y permiten reintentar. |
| CR-02 | Rechazo de precio y stock manual no positivos y de cantidades no positivas; agotados admitidos al cargar. |
| CR-03 | Archivo ausente: aviso e inventario vacío. |
| CR-04 | Líneas mal formadas, códigos repetidos, fechas inválidas y bytes inválidos se omiten con aviso. |
| CR-05 | Lecturas y escrituras usan with; se prueba un error de registro y la recuperación del inventario. |
| CR-06 | Las reglas lanzan ValueError; main y el flujo de venta capturan esos errores. |

Las cancelaciones se prueban durante el carrito y después de mostrar el cobro. El historial admite agregar una venta cuando la última línea anterior no termina en salto de línea.

Los archivos incluidos cubren las cinco categorías, dos productos del mismo proveedor, un producto bajo el mínimo y otro agotado. El ejemplo histórico usa un total de 14200 COP: dos leches de 4200 y una gaseosa de 5800. El total de 18400 que aparece junto a esas cantidades en el PDF no coincide con sus precios; se usa la suma correcta.

El entregable pendiente es la publicación en GitHub. Los archivos de código, los datos de ejemplo, la documentación y las pruebas se preparan en el repositorio local. Sus límites de persistencia y de reportes de productos eliminados están explicados en README.md.
