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


def listar(conexion: Any) -> list[Usuario]:
    """Devuelve todos los usuarios, ordenados por nombre."""
    with conexion.cursor() as cursor:
        cursor.execute(f"SELECT {COLUMNAS} FROM usuarios ORDER BY nombre")
        return [desde_fila(Usuario, fila) for fila in cursor.fetchall()]


def buscar_por_id(conexion: Any, usuario_id: int, bloquear: bool = False) -> Usuario | None:
    """Busca un usuario por su id. Devuelve None si no existe.

    bloquear=True agrega FOR UPDATE: la fila queda reservada hasta el
    final de la transacción, para que nadie la cambie al mismo tiempo.
    """
    sql = f"SELECT {COLUMNAS} FROM usuarios WHERE id = %s" + (" FOR UPDATE" if bloquear else "")
    with conexion.cursor() as cursor:
        cursor.execute(sql, (usuario_id,))
        fila = cursor.fetchone()
    return desde_fila(Usuario, fila) if fila else None


def contar_admins_activos(conexion: Any) -> int:
    """Cuenta los Admin activos, bloqueando sus filas (FOR UPDATE).

    El bloqueo evita que dos Admin se desactiven entre sí al mismo
    tiempo y el sistema quede sin ningún Admin (RN-32).
    """
    with conexion.cursor() as cursor:
        cursor.execute("SELECT id FROM usuarios WHERE rol = 'admin' AND activo = 1 FOR UPDATE")
        return len(cursor.fetchall())


def actualizar_datos(conexion: Any, usuario_id: int, nombre: str, correo: str, rol: str) -> None:
    """Cambia el nombre, el correo y el rol de un usuario."""
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE usuarios SET nombre = %s, correo = %s, rol = %s WHERE id = %s",
                       (nombre, correo, rol, usuario_id))


def cambiar_estado(conexion: Any, usuario_id: int, activo: bool) -> None:
    """Activa o desactiva un usuario."""
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE usuarios SET activo = %s WHERE id = %s", (int(activo), usuario_id))


def cambiar_contrasena(conexion: Any, usuario_id: int, contrasena_hash: str, temporal: bool) -> None:
    """Guarda un hash de contraseña nuevo e indica si es temporal (debe cambiarla al entrar)."""
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE usuarios SET contrasena_hash = %s, debe_cambiar_contrasena = %s WHERE id = %s",
                       (contrasena_hash, int(temporal), usuario_id))


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
