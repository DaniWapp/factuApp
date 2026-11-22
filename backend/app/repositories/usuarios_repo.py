"""
Archivo:  backend/app/repositories/usuarios_repo.py
Proyecto: FacturApp (backend)

Qué hace:
    Consultas SQL de la tabla "usuarios". Es la única parte del código
    que lee o escribe esa tabla (capa repositories).

Seguridad (RNF-05):
    Todos los valores van como parámetros (%s). PyMySQL los escapa, así
    que un texto escrito por el usuario nunca se ejecuta como SQL.

Cómo se usa:
    Cada función recibe una conexión abierta (de app.db.conexion) para
    que varias consultas puedan ir dentro de la misma transacción.
"""

from typing import Any

from app.repositories.tablas import Usuario, desde_fila

# Columnas de la tabla en el orden de schema.sql, para los SELECT.
COLUMNAS = "id, nombre, correo, contrasena_hash, rol, activo, debe_cambiar_contrasena, creado_en"


def buscar_por_correo(conexion: Any, correo: str) -> Usuario | None:
    """Busca un usuario por su correo. Devuelve None si no existe."""
    with conexion.cursor() as cursor:
        cursor.execute(f"SELECT {COLUMNAS} FROM usuarios WHERE correo = %s", (correo,))
        fila = cursor.fetchone()
    return desde_fila(Usuario, fila) if fila else None


def crear(conexion: Any, nombre: str, correo: str, contrasena_hash: str, rol: str,
          debe_cambiar_contrasena: bool) -> int:
    """Guarda un usuario nuevo y devuelve su id.

    activo y creado_en no se escriben: la base de datos les pone sus
    valores por defecto (1 y la fecha actual).
    """
    with conexion.cursor() as cursor:
        cursor.execute(
            "INSERT INTO usuarios (nombre, correo, contrasena_hash, rol, debe_cambiar_contrasena) "
            "VALUES (%s, %s, %s, %s, %s)",
            (nombre, correo, contrasena_hash, rol, int(debe_cambiar_contrasena)),
        )
        return cursor.lastrowid  # el id que la base de datos le asignó


def actualizar_como_admin(conexion: Any, usuario_id: int, nombre: str, contrasena_hash: str) -> None:
    """Cambia nombre y contraseña de un usuario, lo deja como Admin activo y sin contraseña temporal."""
    with conexion.cursor() as cursor:
        cursor.execute(
            "UPDATE usuarios SET nombre = %s, contrasena_hash = %s, rol = 'admin', "
            "activo = 1, debe_cambiar_contrasena = 0 WHERE id = %s",
            (nombre, contrasena_hash, usuario_id),
        )
