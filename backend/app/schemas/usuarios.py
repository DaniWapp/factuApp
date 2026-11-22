"""
Archivo:  backend/app/schemas/usuarios.py
Proyecto: FacturApp (backend)

Qué hace:
    Define la forma de los datos de usuarios que entran y salen de la API.
    Pydantic revisa los datos que llegan; si algo no cumple, la API
    responde 422 con el campo que falló, antes de tocar la base de datos.

Seguridad:
    Ninguna respuesta incluye contrasena_hash. La contraseña temporal
    solo sale UNA vez, en la respuesta de crear o restaurar.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from app.schemas.comunes import Correo, texto


class UsuarioEntrada(BaseModel):
    """Datos para crear o editar un usuario (POST y PUT /api/usuarios)."""
    nombre: texto(100)
    correo: Correo
    rol: Literal["admin", "oficina"]


class EstadoEntrada(BaseModel):
    """Datos para activar o desactivar (PATCH .../estado)."""
    activo: bool


class UsuarioSalida(BaseModel):
    """Un usuario tal como lo devuelve la API (sin la contraseña)."""
    id: int
    nombre: str
    correo: str
    rol: str
    activo: bool
    debe_cambiar_contrasena: bool
    creado_en: datetime


class UsuarioCreadoSalida(BaseModel):
    """Respuesta al crear: el usuario y su contraseña temporal, que se muestra una sola vez."""
    usuario: UsuarioSalida
    contrasena_temporal: str


class ContrasenaTemporalSalida(BaseModel):
    """Respuesta al restaurar la contraseña: la temporal nueva, que se muestra una sola vez."""
    contrasena_temporal: str
