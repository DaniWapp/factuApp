"""
Archivo:  backend/tests/conftest.py
Proyecto: FacturApp (backend)

Qué hace:
    Prepara lo que comparten todas las pruebas ("fixtures").

    1. BASE DE DATOS APARTE: antes de importar la API, cambia el nombre de
       la base a "facturapp_pruebas". Así las pruebas NUNCA tocan
       "facturapp", la base con los datos reales.
    2. Al empezar la ejecución, recrea "facturapp_pruebas" con
       database/schema.sql y database/seed.sql (ver bd_pruebas.py).
    3. Cada prueba trabaja dentro de una transacción que se deshace
       (ROLLBACK) al terminar: una prueba no afecta a la siguiente.

Fixtures:
    conexion  conexión a la base de pruebas que se deshace al final
    cliente   cliente de la API que usa esa conexión
    admin     encabezado con un token del Admin (usuario 1)
    oficina   encabezado con un token de la Oficina radicadora (usuario 2)

Conceptos:
    - Variable de entorno: pydantic-settings le da prioridad sobre el
      .env, por eso basta con poner DB_NAME aquí.
    - scope="session": se ejecuta una sola vez para todas las pruebas.
    - dependency_overrides: reemplaza una dependencia de FastAPI durante
      las pruebas (aquí, obtener_conexion).
"""

import os

# 1. Antes de cualquier "from app...": la API debe leer el nombre de la base de pruebas.
os.environ["DB_NAME"] = "facturapp_pruebas"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.core.config import obtener_configuracion  # noqa: E402
from app.core.seguridad import crear_token  # noqa: E402
from app.db.conexion import abrir_conexion, obtener_conexion  # noqa: E402
from app.main import app  # noqa: E402
from tests.bd_pruebas import recrear_bd_pruebas  # noqa: E402

obtener_configuracion.cache_clear()  # por si algo ya la había leído con el nombre real
assert obtener_configuracion().db_name == "facturapp_pruebas", "Las pruebas deben usar la base de pruebas"


@pytest.fixture(scope="session", autouse=True)
def base_de_pruebas_limpia():
    """2. Recrea la base de pruebas una vez, al empezar todas las pruebas."""
    recrear_bd_pruebas()


@pytest.fixture
def conexion():
    """3. Conexión a la base de pruebas dentro de una transacción que se deshace al final."""
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
