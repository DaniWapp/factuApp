"""
Archivo:  backend/app/db/conexion.py
Proyecto: FacturApp (backend)

Qué hace:
    Abre la conexión a la base de datos "facturapp" con PyMySQL, usando
    los datos del archivo .env, y ofrece una forma segura de trabajar
    con transacciones.

Cómo se usa (desde un service):
    from app.db.conexion import transaccion

    with transaccion() as conexion:
        ...  # varias consultas
    # Al salir del "with": si todo salió bien se guarda todo (COMMIT);
    # si hubo un error, no se guarda nada (ROLLBACK), como pide RN-17.

Conceptos:
    - Transacción: un grupo de cambios que se guarda completo o no se
      guarda. Por ejemplo, una entrega cambia el stock, crea la remisión
      y deja el historial: o pasan las tres cosas o ninguna.
    - DictCursor: cada fila llega como diccionario, por ejemplo
      {"id": 1, "nombre": "Válvulas"}, en lugar de una tupla (1, "Válvulas").
    - contextmanager: permite usar la función con "with", que asegura
      cerrar la conexión aunque ocurra un error.
"""

from collections.abc import Iterator
from contextlib import contextmanager

import pymysql
from pymysql.cursors import DictCursor

from app.core.config import obtener_configuracion

# Hora de Colombia (UTC-5, sin horario de verano). Así CURRENT_TIMESTAMP
# guarda la hora local en las fechas automáticas (RN-20, RNF-32).
ZONA_HORARIA_BD = "-05:00"


def abrir_conexion() -> pymysql.connections.Connection:
    """Abre una conexión nueva a la base de datos con los datos del .env.

    autocommit=False: nada se guarda hasta llamar a commit(), para poder
    deshacer todo si algo falla.
    charset="utf8mb4": guarda bien las tildes y la ñ.
    """
    config = obtener_configuracion()
    return pymysql.connect(
        host=config.db_host,
        port=config.db_port,
        user=config.db_user,
        password=config.db_password,
        database=config.db_name,
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=False,
        init_command=f"SET time_zone = '{ZONA_HORARIA_BD}'",
    )


@contextmanager
def transaccion() -> Iterator[pymysql.connections.Connection]:
    """Entrega una conexión dentro de una transacción.

    Si el bloque "with" termina bien, hace COMMIT; si ocurre cualquier
    error, hace ROLLBACK y vuelve a lanzar el error para que la API
    responda con el código que corresponda. Siempre cierra la conexión.
    """
    conexion = abrir_conexion()
    try:
        yield conexion
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()
