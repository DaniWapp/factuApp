"""
Archivo:  backend/tests/test_tablas.py
Proyecto: FacturApp (backend)

Qué hace:
    Comprueba que los modelos de app/repositories/tablas.py coinciden
    EXACTAMENTE con la base de datos real (la que crea database/schema.sql):
      1. Las mismas 14 tablas.
      2. Las mismas columnas, en el mismo orden.
      3. El mismo tipo SQL en cada columna.
      4. Las mismas columnas que aceptan NULL.
      5. Las mismas llaves foráneas (relaciones).
    Si alguien cambia schema.sql y olvida el modelo (o al revés), esta
    prueba falla y dice qué no coincide.

Requisito:
    La base de datos debe estar encendida y con schema.sql cargado.

Conceptos:
    - information_schema: una base de datos especial de MySQL que describe
      las demás (sus tablas, columnas y llaves). Solo se lee.
    - fixture: algo que pytest prepara antes de las pruebas; aquí, una
      conexión que se usa en todas y se cierra al final.
"""

import re
import types
import typing
from dataclasses import fields

import pytest

from app.core.config import obtener_configuracion
from app.db.conexion import abrir_conexion
from app.repositories.tablas import TABLAS


@pytest.fixture(scope="module")
def conexion():
    """Abre una conexión para todas las pruebas de este archivo y la cierra al final."""
    con = abrir_conexion()
    yield con
    con.close()


def normalizar_tipo(tipo_sql: str) -> str:
    """Quita el ancho de los enteros, que MySQL 8.0.17 y MariaDB muestran y versiones nuevas no.

    Ejemplo: "int(10) unsigned" -> "int unsigned". "tinyint(1)" se conserva,
    porque ese (1) sí indica que la columna es un sí o no.
    """
    return re.sub(r"\b(int|bigint|smallint)\(\d+\)", r"\1", tipo_sql.lower())


def acepta_null(anotacion) -> bool:
    """Dice si el tipo de un atributo acepta None (por ejemplo, "str | None")."""
    return type(None) in typing.get_args(anotacion) or (
        isinstance(anotacion, types.UnionType) and type(None) in anotacion.__args__
    )


def test_mismas_tablas(conexion):
    """La base de datos tiene exactamente las 14 tablas de los modelos."""
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT TABLE_NAME AS tabla FROM information_schema.TABLES WHERE TABLE_SCHEMA = %s",
            (obtener_configuracion().db_name,),
        )
        en_bd = {fila["tabla"] for fila in cursor.fetchall()}
    assert en_bd == set(TABLAS)


@pytest.mark.parametrize("tabla", list(TABLAS))
def test_columnas_tipos_y_nulos(conexion, tabla):
    """Cada modelo tiene las mismas columnas, en el mismo orden, tipo y nulabilidad que la tabla real."""
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT COLUMN_NAME AS nombre, COLUMN_TYPE AS tipo, IS_NULLABLE AS nula "
            "FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s "
            "ORDER BY ORDINAL_POSITION",
            (obtener_configuracion().db_name, tabla),
        )
        columnas_bd = cursor.fetchall()

    pistas = typing.get_type_hints(TABLAS[tabla])
    campos = fields(TABLAS[tabla])

    assert [c["nombre"] for c in columnas_bd] == [f.name for f in campos], "columnas u orden distintos"
    for col_bd, campo in zip(columnas_bd, campos):
        assert normalizar_tipo(col_bd["tipo"]) == normalizar_tipo(campo.metadata["sql"]), f"tipo de {campo.name}"
        assert (col_bd["nula"] == "YES") == acepta_null(pistas[campo.name]), f"NULL en {campo.name}"


@pytest.mark.parametrize("tabla", list(TABLAS))
def test_llaves_foraneas(conexion, tabla):
    """Cada modelo declara exactamente las mismas llaves foráneas que la tabla real."""
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT COLUMN_NAME AS columna, REFERENCED_TABLE_NAME AS tabla_ref, REFERENCED_COLUMN_NAME AS columna_ref "
            "FROM information_schema.KEY_COLUMN_USAGE "
            "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND REFERENCED_TABLE_NAME IS NOT NULL",
            (obtener_configuracion().db_name, tabla),
        )
        en_bd = {f["columna"]: f"{f['tabla_ref']}.{f['columna_ref']}" for f in cursor.fetchall()}

    en_modelo = {f.name: f.metadata["fk"] for f in fields(TABLAS[tabla]) if f.metadata["fk"]}
    assert en_modelo == en_bd
