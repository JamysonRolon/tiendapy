import math
import unicodedata


CATEGORIAS = ["Lacteos", "Bebidas", "Aseo", "Abarrotes", "Snacks"]


def texto_valido(texto):
    texto = texto.strip()
    if not texto or any(c in texto for c in "|:;\n\r"):
        raise ValueError("El texto no puede estar vacío ni contener | : ; o saltos de línea.")
    return texto


def normalizar(texto):
    # Así se puede buscar Lácteos o lacteos.
    texto = unicodedata.normalize("NFD", texto.strip().lower())
    return "".join(c for c in texto if not unicodedata.combining(c))


def categoria_valida(texto):
    for categoria in CATEGORIAS:
        if normalizar(texto) == normalizar(categoria):
            return categoria
    raise ValueError("Categorías disponibles: " + ", ".join(CATEGORIAS))


def numero_positivo(valor, entero=False, permitir_cero=False):
    try:
        numero = int(valor) if entero else float(valor)
    except (ValueError, TypeError, OverflowError):
        raise ValueError("Escribe un número entero." if entero else "Escribe un número válido.")
    if entero and isinstance(valor, float) and valor != numero:
        raise ValueError("Escribe un número entero.")
    try:
        finito = math.isfinite(numero)
    except OverflowError:
        raise ValueError("El número es demasiado grande.")
    if not finito:
        raise ValueError("El número debe ser finito.")
    if numero < 0 or (numero == 0 and not permitir_cero):
        raise ValueError("El número debe ser mayor o igual a cero." if permitir_cero
                         else "El número debe ser mayor que cero.")
    return numero


def leer_numero(mensaje, entero=False, permitir_cero=False):
    while True:
        try:
            return numero_positivo(input(mensaje), entero, permitir_cero)
        except ValueError as error:
            print(error)


def leer_texto(mensaje):
    while True:
        try:
            return texto_valido(input(mensaje))
        except ValueError as error:
            print(error)


def confirmar(mensaje):
    while True:
        respuesta = normalizar(input(mensaje + " (s/n): "))
        if respuesta in ("s", "si"):
            return True
        if respuesta in ("n", "no"):
            return False
        print("Responde s o n.")
