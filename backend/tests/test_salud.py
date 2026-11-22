"""
Archivo:  backend/tests/test_salud.py
Proyecto: FacturApp (backend)

Qué hace:
    Prueba automática de la ruta GET /api/salud.

Cómo se ejecuta (desde la carpeta backend/):
    .venv\\Scripts\\python.exe -m pytest

Conceptos:
    - pytest busca los archivos que empiezan por "test_" y ejecuta las
      funciones que empiezan por "test_".
    - assert: comprueba que algo sea cierto; si no lo es, la prueba falla.
    - TestClient: llama a la API sin encender el servidor (usa httpx).
"""

from fastapi.testclient import TestClient

from app.main import app

cliente = TestClient(app)


def test_salud_responde_ok():
    """GET /api/salud debe responder 200 y {"estado": "ok"}."""
    respuesta = cliente.get("/api/salud")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "ok"}
