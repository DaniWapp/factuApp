"""
Archivo:  backend/app/routers/auth.py
Proyecto: FacturApp (backend)

Qué hace:
    Las rutas de la propia cuenta:
        POST /api/auth/login        iniciar sesión (público, HU-01)
        GET  /api/auth/yo           datos del usuario del token (HU-03)
        POST /api/auth/contrasena   cambiar la propia contraseña (HU-04, HU-05)

    /yo y /contrasena usan usuario_del_token y no usuario_actual: así
    quien tiene una contraseña temporal puede ver sus datos y cambiarla,
    aunque todavía no pueda usar el resto del sistema.

    Cerrar sesión (HU-02) no necesita ruta: Flask borra su sesión y el
    token deja de enviarse.
"""

from typing import Any

from fastapi import APIRouter, Depends

from app.core.dependencias import usuario_del_token
from app.db.conexion import obtener_conexion
from app.repositories.tablas import Usuario
from app.schemas.auth import CambioContrasenaEntrada, LoginEntrada, LoginSalida, MensajeSalida, UsuarioSesion
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["autenticación"])


@router.post("/login", response_model=LoginSalida)
def iniciar_sesion(datos: LoginEntrada, conexion: Any = Depends(obtener_conexion)):
    """Recibe correo y contraseña y responde con el token (120 minutos)."""
    return auth_service.iniciar_sesion(conexion, datos)


@router.get("/yo", response_model=UsuarioSesion)
def mis_datos(usuario: Usuario = Depends(usuario_del_token)):
    """Devuelve los datos del usuario dueño del token."""
    return usuario


@router.post("/contrasena", response_model=MensajeSalida)
def cambiar_contrasena(datos: CambioContrasenaEntrada, usuario: Usuario = Depends(usuario_del_token),
                       conexion: Any = Depends(obtener_conexion)):
    """Cambia la propia contraseña: pide la actual, la nueva y la confirmación."""
    auth_service.cambiar_contrasena(conexion, usuario, datos)
    return {"mensaje": "Contraseña actualizada."}
