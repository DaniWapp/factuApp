"""
Archivo:  backend/app/schemas/comunes.py
Proyecto: FacturApp (backend)

Qué hace:
    Piezas de validación que comparten varios schemas.

Conceptos:
    - Annotated[str, ...]: un tipo "con reglas". Por ejemplo, TextoCorto
      es un texto al que se le quitan los espacios de los extremos y que
      no puede quedar vacío.
    - StringConstraints: reglas de un texto (largo mínimo, máximo...).
    - AfterValidator: una función que revisa el valor después de las
      reglas básicas; si lanza ValueError, el mensaje llega al usuario.
"""

import re
from typing import Annotated

from pydantic import AfterValidator, StringConstraints

# Patrón sencillo de correo: texto, @, texto, punto, texto, sin espacios.
PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
# RN-25: códigos solo con letras sin tildes, números y guiones.
PATRON_CODIGO = re.compile(r"^[A-Za-z0-9-]+$")
# RN-25: cédula o NIT solo con números, puntos y guiones.
PATRON_DOCUMENTO = re.compile(r"^[0-9.\-]+$")


def validar_correo(valor: str) -> str:
    """Revisa el formato del correo y lo devuelve en minúsculas."""
    if not PATRON_CORREO.match(valor):
        raise ValueError("Escriba un correo válido.")
    return valor.lower()


def validar_codigo(valor: str) -> str:
    """RN-25: el código solo puede tener letras sin tildes, números y guiones. Se guarda en mayúsculas."""
    if not PATRON_CODIGO.match(valor):
        raise ValueError("El código solo puede tener letras sin tildes, números y guiones.")
    return valor.upper()


def validar_documento(valor: str) -> str:
    """RN-25: la cédula o NIT solo puede tener números, puntos y guiones, y al menos un número."""
    if not PATRON_DOCUMENTO.match(valor) or not any(c.isdigit() for c in valor):
        raise ValueError("La cédula o NIT solo puede tener números, puntos y guiones.")
    return valor


def texto(maximo: int):
    """Texto obligatorio: sin espacios en los extremos (RN-07), de 1 a "maximo" caracteres."""
    return Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=maximo)]


def texto_opcional(maximo: int):
    """Texto que puede faltar (None); si viene, sin espacios en los extremos y de máximo "maximo" caracteres."""
    return Annotated[str, StringConstraints(strip_whitespace=True, max_length=maximo)] | None


Correo = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=150),
                   AfterValidator(validar_correo)]
Codigo = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=30),
                   AfterValidator(validar_codigo)]
Documento = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20),
                      AfterValidator(validar_documento)]
