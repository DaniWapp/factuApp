"""
Paquete principal del backend de FacturApp (API FastAPI).

Qué es un "paquete": una carpeta de Python que tiene un archivo
__init__.py. Gracias a él se puede escribir, por ejemplo,
"from app.routers import salud".

Capas (cada una solo llama a la siguiente, RNF-23):
    routers -> services -> repositories -> base de datos

Carpetas:
    core/          Configuración, seguridad, usuario actual y errores.
    db/            Conexión a MySQL o MariaDB y transacciones.
    schemas/       Forma y validación de los datos (Pydantic).
    routers/       Rutas de la API.
    services/      Reglas del negocio.
    repositories/  Consultas SQL.
"""
