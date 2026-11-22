"""
Archivo:  backend/tests/conftest.py
Proyecto: FacturApp (backend)

Qué hace:
    Prepara lo que comparten las pruebas de la API ("fixtures"):
      - conexion: una conexión a la base real dentro de una transacción
        que se DESHACE (ROLLBACK) al terminar cada prueba. Así las pruebas
        pueden crear, editar y entregar sin cambiar los datos de verdad.
      - cliente: un cliente de la API que usa esa conexión.
      - admin / oficina: encabezados con un token del Admin (usuario 1) y
        de la Oficina radicadora (usuario 2) de database/seed.sql.

Requisito:
    MySQL encendido, con database/schema.sql y database/seed.sql cargados.

Conceptos:
    - conftest.py: pytest lo lee solo; sus fixtures sirven en todos los
      archivos de pruebas de la carpeta.
    - dependency_overrides: reemplaza una dependencia de FastAPI durante
      las pruebas; aquí, obtener_conexion por la conexión que se deshace.
"""

import pytest
from fastapi.testclient import TestClient

from app.core.seguridad import crear_token
from app.db.conexion import abrir_conexion, obtener_conexion
from app.main import app


@pytest.fixture
def conexion():
    """Conexión dentro de una transacción que se deshace al final de la prueba."""
    con = abrir_conexion()
    yield con
    con.rollback()
    con.close()


@pytest.fixture
def cliente(conexion):
    """Cliente de la API que trabaja sobre la conexión que se deshace."""

    def conexion_de_prueba():
        yield conexion

    app.dependency_overrides[obtener_conexion] = conexion_de_prueba
    yield TestClient(app)
    app.dependency_overrides.clear()


def encabezado(usuario_id: int, rol: str) -> dict[str, str]:
    """Arma el encabezado Authorization con un token válido para ese usuario."""
    return {"Authorization": f"Bearer {crear_token(usuario_id, rol)}"}


@pytest.fixture
def admin() -> dict[str, str]:
    """Token del Admin de los datos de ejemplo (usuario 1)."""
    return encabezado(1, "admin")


@pytest.fixture
def oficina() -> dict[str, str]:
    """Token de la Oficina radicadora de los datos de ejemplo (usuario 2, Laura Gómez)."""
    return encabezado(2, "oficina")


def codigo_error(respuesta) -> str:
    """Devuelve el código corto del error, por ejemplo "SIN_PERMISO"."""
    return respuesta.json()["error"]["codigo"]
