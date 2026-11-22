"""
Archivo:  backend/app/repositories/base.py
Proyecto: FacturApp (backend)

Qué hace:
    Consultas que sirven para cualquier tabla. Por ahora, contar cuántos
    registros tiene una tabla.

Seguridad (RNF-05):
    Los valores siempre van como parámetros (%s). El nombre de una tabla
    no puede ir como parámetro, por eso solo se aceptan los nombres que
    están en TABLAS (tablas.py); cualquier otro se rechaza.
"""

from typing import Any

from app.repositories.tablas import TABLAS


def contar_registros(conexion: Any, tabla: str) -> int:
    """Devuelve cuántos registros tiene una tabla de la base de datos."""
    if tabla not in TABLAS:
        raise ValueError(f"Tabla no permitida: {tabla}")
    with conexion.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) AS total FROM `{tabla}`")
        return int(cursor.fetchone()["total"])
