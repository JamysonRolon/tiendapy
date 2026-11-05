# Estas validaciones se comparten entre el menú y las funciones del negocio.
import math  # Permite rechazar infinito y NaN, que no sirven como precios.
import unicodedata


CATEGORIAS = ["Lacteos", "Bebidas", "Aseo", "Abarrotes", "Snacks"]


def texto_valido(texto):
    # Devuelve el texto sin espacios en los extremos o avisa si no es válido.
    # Los separadores se reservan para los archivos de inventario y ventas.
    texto = texto.strip()
    if not texto or any(c in texto for c in "|:;\n\r"):
        raise ValueError("El texto no puede estar vacío ni contener | : ; o saltos de línea.")
    return texto


def normalizar(texto):
    # Así se puede buscar Lácteos o lacteos.
    # NFD separa la letra de su tilde; combining identifica esas marcas.
    texto = unicodedata.normalize("NFD", texto.strip().lower())
    return "".join(c for c in texto if not unicodedata.combining(c))


def categoria_valida(texto):
    # Compara sin tildes ni mayúsculas y devuelve el nombre de la lista oficial.
    for categoria in CATEGORIAS:
        if normalizar(texto) == normalizar(categoria):
            return categoria
    raise ValueError("Categorías disponibles: " + ", ".join(CATEGORIAS))


def numero_positivo(valor, entero=False, permitir_cero=False):
    # entero=True se usa para unidades; False permite decimales para el dinero.
    # permitir_cero=True se usa para el mínimo y para cargar productos agotados.
    try:
        numero = int(valor) if entero else float(valor)
    except (ValueError, TypeError, OverflowError):
        raise ValueError("Escribe un número entero." if entero else "Escribe un número válido.")
    # int(1.5) daría 1: rechazarlo evita perder la parte decimal sin avisar.
    if entero and isinstance(valor, float) and valor != numero:
        raise ValueError("Escribe un número entero.")
    try:
        finito = math.isfinite(numero)
    except OverflowError:
        raise ValueError("El número es demasiado grande.")
    if not finito:
        raise ValueError("El número debe ser finito.")
    # raise entrega el error a quien llamó la función; aquí no se pide otro dato.
    if numero < 0 or (numero == 0 and not permitir_cero):
        raise ValueError("El número debe ser mayor o igual a cero." if permitir_cero
                         else "El número debe ser mayor que cero.")
    return numero


def leer_numero(mensaje, entero=False, permitir_cero=False):
    # Repite la pregunta hasta obtener un número que cumpla las reglas.
    # El except muestra el error y deja que el while vuelva a pedir la entrada.
    while True:
        try:
            return numero_positivo(input(mensaje), entero, permitir_cero)
        except ValueError as error:
            print(error)


def leer_texto(mensaje):
    # Usa la misma idea de reintento para nombres, códigos y proveedores.
    while True:
        try:
            return texto_valido(input(mensaje))
        except ValueError as error:
            print(error)


def confirmar(mensaje):
    # Devuelve True para sí y False para no; otras respuestas se vuelven a pedir.
    while True:
        respuesta = normalizar(input(mensaje + " (s/n): "))
        if respuesta in ("s", "si"):
            return True
        if respuesta in ("n", "no"):
            return False
        print("Responde s o n.")
