"""
Archivo:  backend/tests/bd_pruebas.py
Proyecto: FacturApp (backend)

Qué hace:
    Crea de cero la base de datos de PRUEBAS "facturapp_pruebas" con los
    mismos archivos de la base real: database/schema.sql (las tablas) y
    database/seed.sql (los datos de ejemplo). Solo cambia el nombre de
    la base, así las pruebas nunca tocan "facturapp", la base real.

Cuándo se usa:
    - Automáticamente, al empezar cada ejecución de pytest (conftest.py).
    - A mano, si se quiere dejarla limpia:
          cd backend
          .venv\\Scripts\\python.exe -m tests.bd_pruebas

Requisito (se hace una sola vez, ya está hecho en este equipo):
    La base vacía y el permiso del usuario del proyecto sobre ella:
        CREATE DATABASE facturapp_pruebas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
        GRANT ALL PRIVILEGES ON facturapp_pruebas.* TO 'facturapp'@'localhost';
        GRANT ALL PRIVILEGES ON facturapp_pruebas.* TO 'facturapp'@'127.0.0.1';

Conceptos:
    - MULTI_STATEMENTS: permite enviar a MySQL un archivo con muchas
      instrucciones SQL juntas (separadas por ";") en una sola llamada.
    - nextset(): recorre los resultados de cada instrucción, para que
      MySQL termine de ejecutarlas todas.
"""

from pathlib import Path

import pymysql
from pymysql.constants import CLIENT

from app.core.config import obtener_configuracion

CARPETA_DATABASE = Path(__file__).resolve().parents[2] / "database"
NOMBRE_REAL = "facturapp"


def preparar_sql(texto: str, nombre_pruebas: str) -> str:
    """Cambia en el SQL solo las dos líneas que nombran la base de datos real."""
    return (texto.replace(f"CREATE DATABASE IF NOT EXISTS {NOMBRE_REAL}\n", f"CREATE DATABASE IF NOT EXISTS {nombre_pruebas}\n")
                 .replace(f"USE {NOMBRE_REAL};", f"USE {nombre_pruebas};"))


def recrear_bd_pruebas() -> None:
    """Borra las tablas de la base de pruebas y las vuelve a crear con los datos de ejemplo."""
    config = obtener_configuracion()
    # Protección: este código jamás debe correr sobre la base real.
    if not config.db_name.endswith("_pruebas"):
        raise RuntimeError(f"La base de pruebas debe terminar en _pruebas, no {config.db_name!r}.")

    conexion = pymysql.connect(host=config.db_host, port=config.db_port, user=config.db_user,
                               password=config.db_password, charset="utf8mb4",
                               client_flag=CLIENT.MULTI_STATEMENTS, autocommit=True)
    try:
        with conexion.cursor() as cursor:
            for archivo in ("schema.sql", "seed.sql"):
                sql = preparar_sql((CARPETA_DATABASE / archivo).read_text(encoding="utf-8"), config.db_name)
                if f"USE {config.db_name};" not in sql:
                    raise RuntimeError(f"{archivo} no apunta a la base de pruebas; no se ejecuta.")
                cursor.execute(sql)
                while cursor.nextset():  # espera a que terminen todas las instrucciones del archivo
                    pass
    finally:
        conexion.close()


if __name__ == "__main__":
    import os
    os.environ.setdefault("DB_NAME", "facturapp_pruebas")
    obtener_configuracion.cache_clear()
    recrear_bd_pruebas()
    print(f"Base {obtener_configuracion().db_name} creada con schema.sql y seed.sql.")
