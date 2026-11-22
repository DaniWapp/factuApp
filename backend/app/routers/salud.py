"""
Archivo:  backend/app/routers/salud.py
Proyecto: FacturApp (backend)

Qué hace:
    Define la ruta GET /api/salud, que responde {"estado": "ok"}.
    Sirve para comprobar rápido que la API está encendida y responde.
    No necesita iniciar sesión ni toca la base de datos.

Conceptos:
    - APIRouter: un grupo de rutas. Se crea aquí y main.py lo registra.
    - @router.get("/salud"): "decorador" que conecta la función de abajo
      con una petición GET a esa dirección.
"""

from fastapi import APIRouter

# Grupo de rutas de este módulo. "tags" agrupa las rutas en la
# documentación automática de http://localhost:8000/docs.
router = APIRouter(tags=["salud"])


@router.get("/salud")
def revisar_salud() -> dict[str, str]:
    """Responde que la API está funcionando.

    FastAPI convierte el diccionario de Python en JSON automáticamente,
    y responde con el código 200 (OK).
    """
    return {"estado": "ok"}
