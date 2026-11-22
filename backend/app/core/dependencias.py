"""
Archivo:  backend/app/core/dependencias.py
Proyecto: FacturApp (backend)

Qué hace:
    Las "dependencias" de seguridad que usan las rutas. Son la protección
    REAL de permisos (RN-02); lo que oculta el frontend es solo comodidad.

      usuario_del_token  verifica el token y que el usuario siga ACTIVO,
                         en CADA petición (RN-01). Lo usan solo las rutas
                         de la propia cuenta (/auth/yo y /auth/contrasena).
      usuario_actual     lo anterior, y además exige que NO tenga una
                         contraseña temporal pendiente de cambiar (RN-04).
                         Lo usan todas las demás rutas.
      requiere_admin     lo anterior, y además exige el rol Admin.

    (Equivalen a get_current_user y require_admin; el proyecto usa
    nombres en español.)

Respuestas de error (formato de errores, Entregable 04 sección 7):
    401 NO_AUTENTICADO              no llegó ningún token
    401 SESION_VENCIDA              el token venció o fue alterado
    401 USUARIO_DESACTIVADO         el usuario no existe o fue desactivado;
                                    se revisa en cada petición, así la
                                    desactivación tiene efecto de inmediato
    403 CAMBIO_CONTRASENA_REQUERIDO tiene una contraseña temporal sin cambiar
    403 SIN_PERMISO                 el rol no puede hacer esa acción

Conceptos:
    - Depends(...): le pide a FastAPI que ejecute otra función antes de
      la ruta y le pase el resultado. Si esa función lanza un error, la
      ruta ni siquiera se ejecuta.
    - HTTPBearer: lee el encabezado "Authorization: Bearer <token>".
"""

from typing import Any

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.errores import NoAutenticado, SinPermiso
from app.core.seguridad import TokenInvalido, leer_token
from app.db.conexion import obtener_conexion
from app.repositories import usuarios_repo
from app.repositories.tablas import Usuario

# auto_error=False: si no hay token, en lugar del error en inglés de
# FastAPI, lanzamos nuestro propio error 401 con el formato del proyecto.
esquema_bearer = HTTPBearer(auto_error=False)

MENSAJE_DESACTIVADO = "Su usuario está desactivado. Comuníquese con el administrador."


def usuario_del_token(
    credenciales: HTTPAuthorizationCredentials | None = Depends(esquema_bearer),
    conexion: Any = Depends(obtener_conexion),
) -> Usuario:
    """Devuelve el usuario dueño del token, si sigue activo; si no, lanza 401."""
    if credenciales is None:
        raise NoAutenticado("NO_AUTENTICADO", "Inicie sesión para continuar.")

    try:
        datos = leer_token(credenciales.credentials)
    except TokenInvalido as error:
        raise NoAutenticado("SESION_VENCIDA", "Su sesión expiró. Inicie sesión de nuevo.") from error

    # El token puede seguir vigente aunque el Admin haya desactivado al
    # usuario: por eso se consulta la base de datos en cada petición.
    usuario = usuarios_repo.buscar_por_id(conexion, int(datos["sub"]))
    if usuario is None or not usuario.activo:
        raise NoAutenticado("USUARIO_DESACTIVADO", MENSAJE_DESACTIVADO)
    return usuario


def usuario_actual(usuario: Usuario = Depends(usuario_del_token)) -> Usuario:
    """Igual que usuario_del_token, pero bloquea a quien debe cambiar su contraseña temporal (RN-04)."""
    if usuario.debe_cambiar_contrasena:
        raise SinPermiso("CAMBIO_CONTRASENA_REQUERIDO", "Debe cambiar su contraseña temporal antes de continuar.")
    return usuario


def requiere_admin(usuario: Usuario = Depends(usuario_actual)) -> Usuario:
    """Devuelve el usuario si es Admin; si no, lanza un error 403 (RN-02)."""
    if usuario.rol != "admin":
        raise SinPermiso("SIN_PERMISO", "No tiene permiso para hacer esta acción.")
    return usuario
