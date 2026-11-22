"""
Archivo:  backend/app/core/dependencias.py
Proyecto: FacturApp (backend)

Qué hace:
    Las "dependencias" de seguridad que usan las rutas:
      - usuario_actual: lee el token del encabezado Authorization, lo
        verifica y busca al usuario en la base de datos.
      - requiere_admin: además exige que el usuario sea Admin.
    Esta es la protección REAL de permisos (RN-02); lo que oculta el
    frontend es solo comodidad.

Respuestas de error (formato de errores, Entregable 04 sección 7):
    401 NO_AUTENTICADO       no llegó ningún token
    401 SESION_VENCIDA       el token venció o fue alterado
    401 USUARIO_DESACTIVADO  el usuario ya no existe o fue desactivado (RN-01):
                             se revisa en CADA petición, así la desactivación
                             tiene efecto de inmediato (PA-25)
    403 SIN_PERMISO          el rol no puede hacer esa acción

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


def usuario_actual(
    credenciales: HTTPAuthorizationCredentials | None = Depends(esquema_bearer),
    conexion: Any = Depends(obtener_conexion),
) -> Usuario:
    """Devuelve el usuario que hace la petición, o lanza un error 401."""
    if credenciales is None:
        raise NoAutenticado("NO_AUTENTICADO", "Inicie sesión para continuar.")

    try:
        datos = leer_token(credenciales.credentials)
    except TokenInvalido as error:
        raise NoAutenticado("SESION_VENCIDA", "Su sesión expiró. Inicie sesión de nuevo.") from error

    usuario = usuarios_repo.buscar_por_id(conexion, int(datos["sub"]))
    if usuario is None or not usuario.activo:
        raise NoAutenticado("USUARIO_DESACTIVADO",
                            "Su usuario está desactivado. Comuníquese con el administrador.")
    return usuario


def requiere_admin(usuario: Usuario = Depends(usuario_actual)) -> Usuario:
    """Devuelve el usuario si es Admin; si no, lanza un error 403 (RN-02)."""
    if usuario.rol != "admin":
        raise SinPermiso("SIN_PERMISO", "No tiene permiso para hacer esta acción.")
    return usuario
