"""
Archivo:  backend/app/main.py
Proyecto: FacturApp (backend)

Qué hace:
    Es el punto de arranque de la API. Crea la aplicación FastAPI y
    registra los routers de cada módulo bajo el prefijo /api.

Cómo se ejecuta (desde la carpeta backend/, con el entorno virtual):
    .venv\\Scripts\\python.exe -m uvicorn app.main:app --reload --port 8000

    - app.main:app  significa "en el archivo app/main.py, usa la variable app".
    - --reload      reinicia la API sola cada vez que se guarda un archivo.
    - --port 8000   el puerto de la API (Entregable 04, sección 8).

Después de arrancarla:
    http://localhost:8000/api/salud  responde {"estado": "ok"}
    http://localhost:8000/docs       documentación interactiva de la API
"""

from fastapi import FastAPI

from app.routers import salud

# La aplicación. El título y la versión aparecen en /docs.
app = FastAPI(
    title="API de FacturApp",
    description="Solicitud, entrega y trazabilidad de repuestos de refrigeración.",
    version="0.6.0",
)

# Todas las rutas de la API empiezan por /api (Entregable 04, sección 3.1).
# Aquí se irán registrando los demás routers: usuarios, repuestos, entregas...
app.include_router(salud.router, prefix="/api")
