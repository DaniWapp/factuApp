"""
Archivo:  backend/app/services/usuarios_service.py
Proyecto: FacturApp (backend)

Qué hace:
    Las reglas de negocio de los usuarios (capa services). El router solo
    recibe la petición y llama a estas funciones; el SQL está en
    usuarios_repo.

Reglas que aplica:
    - El correo no se repite (409 CORREO_REPETIDO).
    - Al crear y al restaurar se genera una contraseña temporal; se
      devuelve una sola vez y queda marcada para cambiarse (PA-36).
    - Un Admin no puede desactivarse a sí mismo ni quitarse su rol de
      Admin, y nunca puede quedar el sistema sin un Admin activo (RN-32).
"""

from typing import Any

from app.core.errores import Conflicto, NoEncontrado
from app.core.seguridad import cifrar_contrasena, generar_contrasena_temporal
from app.repositories import usuarios_repo
from app.repositories.tablas import Usuario
from app.schemas.usuarios import UsuarioEntrada


def listar(conexion: Any) -> list[Usuario]:
    """Devuelve todos los usuarios."""
    return usuarios_repo.listar(conexion)


def obtener(conexion: Any, usuario_id: int, bloquear: bool = False) -> Usuario:
    """Devuelve un usuario o lanza 404 si no existe."""
    usuario = usuarios_repo.buscar_por_id(conexion, usuario_id, bloquear)
    if usuario is None:
        raise NoEncontrado("NO_ENCONTRADO", "El usuario no existe.")
    return usuario


def _revisar_correo_libre(conexion: Any, correo: str, excepto_id: int | None = None) -> None:
    """Lanza 409 si otro usuario ya tiene ese correo."""
    otro = usuarios_repo.buscar_por_correo(conexion, correo)
    if otro is not None and otro.id != excepto_id:
        raise Conflicto("CORREO_REPETIDO", "Ya existe un usuario con ese correo.",
                        {"correo": "Ya existe un usuario con ese correo."})


def _revisar_que_quede_un_admin(conexion: Any, usuario: Usuario) -> None:
    """RN-32: si el usuario es el último Admin activo, no puede dejar de serlo."""
    if usuario.rol == "admin" and usuario.activo and usuarios_repo.contar_admins_activos(conexion) <= 1:
        raise Conflicto("ULTIMO_ADMIN", "No se puede dejar el sistema sin un Admin activo.")


def crear(conexion: Any, datos: UsuarioEntrada) -> tuple[Usuario, str]:
    """Crea un usuario con una contraseña temporal. Devuelve el usuario y esa contraseña."""
    _revisar_correo_libre(conexion, datos.correo)
    temporal = generar_contrasena_temporal()
    nuevo_id = usuarios_repo.crear(conexion, datos.nombre, datos.correo, cifrar_contrasena(temporal),
                                   rol=datos.rol, debe_cambiar_contrasena=True)
    return obtener(conexion, nuevo_id), temporal


def editar(conexion: Any, usuario_id: int, datos: UsuarioEntrada, actual: Usuario) -> Usuario:
    """Cambia nombre, correo y rol, respetando las reglas del Admin."""
    usuario = obtener(conexion, usuario_id, bloquear=True)
    _revisar_correo_libre(conexion, datos.correo, excepto_id=usuario_id)

    deja_de_ser_admin = usuario.rol == "admin" and datos.rol != "admin"
    if deja_de_ser_admin:
        if usuario.id == actual.id:
            raise Conflicto("NO_PUEDE_CAMBIAR_SU_ROL", "No puede quitarse a sí mismo el rol de Admin.")
        _revisar_que_quede_un_admin(conexion, usuario)

    usuarios_repo.actualizar_datos(conexion, usuario_id, datos.nombre, datos.correo, datos.rol)
    return obtener(conexion, usuario_id)


def cambiar_estado(conexion: Any, usuario_id: int, activo: bool, actual: Usuario) -> Usuario:
    """Activa o desactiva un usuario (HU-10). Al desactivar se aplican RN-32."""
    usuario = obtener(conexion, usuario_id, bloquear=True)
    if not activo:
        if usuario.id == actual.id:
            raise Conflicto("NO_PUEDE_DESACTIVARSE", "No puede desactivar su propio usuario.")
        _revisar_que_quede_un_admin(conexion, usuario)
    usuarios_repo.cambiar_estado(conexion, usuario_id, activo)
    return obtener(conexion, usuario_id)


def restaurar_contrasena(conexion: Any, usuario_id: int) -> str:
    """Asigna una contraseña temporal nueva (HU-11) y la devuelve una sola vez."""
    obtener(conexion, usuario_id, bloquear=True)
    temporal = generar_contrasena_temporal()
    usuarios_repo.cambiar_contrasena(conexion, usuario_id, cifrar_contrasena(temporal), temporal=True)
    return temporal
