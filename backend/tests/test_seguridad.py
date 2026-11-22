"""
Archivo:  backend/tests/test_seguridad.py
Proyecto: FacturApp (backend)

Qué prueba:
    Las funciones de app/core/seguridad.py: la regla de contraseña, el
    cifrado con bcrypt y los tokens JWT. No usa la base de datos.

Conceptos:
    - monkeypatch: herramienta de pytest para cambiar algo solo durante
      una prueba (aquí, la duración del token, para probar que vence).
"""

import time

import pytest

from app.core import seguridad
from app.core.config import obtener_configuracion


# ---------------------------------------------------------------- regla de contraseña

@pytest.mark.parametrize("contrasena, mensaje", [
    ("abc123", "La contraseña debe tener al menos 8 caracteres."),
    ("solamenteletras", "La contraseña debe tener letras y números."),
    ("1234567890", "La contraseña debe tener letras y números."),
    ("a1" * 40, "La contraseña es demasiado larga (máximo 72 caracteres)."),
])
def test_contrasena_invalida(contrasena, mensaje):
    """Las contraseñas que no cumplen RN-03 devuelven el mensaje que verá el usuario."""
    assert seguridad.validar_contrasena(contrasena) == mensaje


def test_contrasena_valida():
    """Una contraseña con 8 o más caracteres, letras y números es válida."""
    assert seguridad.validar_contrasena("Frio2026valv") is None


# ---------------------------------------------------------------- bcrypt

def test_cifrar_y_verificar():
    """El hash no contiene la contraseña y solo la contraseña correcta coincide."""
    hash_guardado = seguridad.cifrar_contrasena("Frio2026valv")
    assert hash_guardado.startswith("$2b$")
    assert "Frio2026valv" not in hash_guardado
    assert seguridad.verificar_contrasena("Frio2026valv", hash_guardado) is True
    assert seguridad.verificar_contrasena("otra1234", hash_guardado) is False


def test_misma_contrasena_hash_distinto():
    """Por la sal aleatoria, la misma contraseña produce hashes distintos."""
    assert seguridad.cifrar_contrasena("Frio2026valv") != seguridad.cifrar_contrasena("Frio2026valv")


def test_hash_de_ejemplo_no_falla():
    """El hash de ejemplo de seed.sql responde False en lugar de lanzar un error."""
    hash_ejemplo = "$2b$12$HashDeEjemploNoValido.SeCreaRealmenteEnElBackendE06.."
    assert seguridad.verificar_contrasena("cualquier1", hash_ejemplo) is False


# ---------------------------------------------------------------- JWT

def test_token_ida_y_vuelta():
    """Un token creado se puede leer y trae el usuario, el rol y 120 minutos de vigencia."""
    token = seguridad.crear_token(1, "admin")
    datos = seguridad.leer_token(token)
    assert datos["sub"] == "1"
    assert datos["rol"] == "admin"
    assert datos["exp"] - datos["iat"] == obtener_configuracion().jwt_minutos_vigencia * 60
    assert obtener_configuracion().jwt_minutos_vigencia == 120


def test_token_alterado():
    """Si se cambia una letra del token, la firma ya no coincide."""
    token = seguridad.crear_token(1, "oficina")
    alterado = token[:-2] + ("A" if token[-2] != "A" else "B") + token[-1]
    with pytest.raises(seguridad.TokenInvalido):
        seguridad.leer_token(alterado)


def test_token_vencido(monkeypatch):
    """Un token cuya vigencia ya pasó se rechaza."""
    config = obtener_configuracion()
    monkeypatch.setattr(config, "jwt_minutos_vigencia", -1)  # nace vencido
    token = seguridad.crear_token(1, "admin")
    with pytest.raises(seguridad.TokenInvalido, match="venció"):
        seguridad.leer_token(token)
