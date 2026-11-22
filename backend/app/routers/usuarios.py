"""
Archivo:  backend/app/routers/usuarios.py
Proyecto: FacturApp (backend)

Qué hace:
    Las rutas de usuarios. Todas son solo para el Admin (requiere_admin):
        GET    /api/usuarios                              listar (HU-09)
        GET    /api/usuarios/{id}                         ver uno (HU-08)
        POST   /api/usuarios                              crear con contraseña temporal (HU-07)
        PUT    /api/usuarios/{id}                         editar (HU-08)
        PATCH  /api/usuarios/{id}/estado                  activar o desactivar (HU-10)
        POST   /api/usuarios/{id}/restaurar-contrasena    contraseña temporal nueva (HU-11)
    No hay ruta para borrar: los usuarios se desactivan (RN-05).

Capas:
    El router no tiene reglas ni SQL: recibe, llama al service y responde.

Conceptos:
    - response_model: la forma de la respuesta; FastAPI deja solo esos
      campos, así contrasena_hash nunca sale aunque esté en el objeto.
    - Cache-Control: no-store: le pide al navegador y a los intermediarios
      que no guarden la respuesta; se usa cuando trae una contraseña.
"""

from typing import Any

from fastapi import APIRouter, Depends, Response, status

from app.core.dependencias import requiere_admin
from app.db.conexion import obtener_conexion
from app.repositories.tablas import Usuario
from app.schemas.usuarios import (ContrasenaTemporalSalida, EstadoEntrada, UsuarioCreadoSalida,
                                  UsuarioEntrada, UsuarioSalida)
from app.services import usuarios_service

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


def _no_guardar(respuesta: Response) -> None:
    """Marca la respuesta para que no se guarde en ninguna caché (trae una contraseña)."""
    respuesta.headers["Cache-Control"] = "no-store"


@router.get("", response_model=list[UsuarioSalida])
def listar_usuarios(_admin: Usuario = Depends(requiere_admin), conexion: Any = Depends(obtener_conexion)):
    """Lista todos los usuarios."""
    return usuarios_service.listar(conexion)


@router.get("/{usuario_id}", response_model=UsuarioSalida)
def ver_usuario(usuario_id: int, _admin: Usuario = Depends(requiere_admin),
                conexion: Any = Depends(obtener_conexion)):
    """Devuelve un usuario."""
    return usuarios_service.obtener(conexion, usuario_id)


@router.post("", response_model=UsuarioCreadoSalida, status_code=status.HTTP_201_CREATED)
def crear_usuario(datos: UsuarioEntrada, respuesta: Response, _admin: Usuario = Depends(requiere_admin),
                  conexion: Any = Depends(obtener_conexion)):
    """Crea un usuario y devuelve, una sola vez, su contraseña temporal."""
    usuario, temporal = usuarios_service.crear(conexion, datos)
    _no_guardar(respuesta)
    return {"usuario": usuario, "contrasena_temporal": temporal}


@router.put("/{usuario_id}", response_model=UsuarioSalida)
def editar_usuario(usuario_id: int, datos: UsuarioEntrada, admin: Usuario = Depends(requiere_admin),
                   conexion: Any = Depends(obtener_conexion)):
    """Cambia nombre, correo y rol."""
    return usuarios_service.editar(conexion, usuario_id, datos, admin)


@router.patch("/{usuario_id}/estado", response_model=UsuarioSalida)
def cambiar_estado_usuario(usuario_id: int, datos: EstadoEntrada, admin: Usuario = Depends(requiere_admin),
                           conexion: Any = Depends(obtener_conexion)):
    """Activa o desactiva un usuario."""
    return usuarios_service.cambiar_estado(conexion, usuario_id, datos.activo, admin)


@router.post("/{usuario_id}/restaurar-contrasena", response_model=ContrasenaTemporalSalida)
def restaurar_contrasena(usuario_id: int, respuesta: Response, _admin: Usuario = Depends(requiere_admin),
                         conexion: Any = Depends(obtener_conexion)):
    """Asigna una contraseña temporal nueva y la devuelve una sola vez."""
    temporal = usuarios_service.restaurar_contrasena(conexion, usuario_id)
    _no_guardar(respuesta)
    return {"contrasena_temporal": temporal}
