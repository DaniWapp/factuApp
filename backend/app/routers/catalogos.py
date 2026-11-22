"""
Archivo:  backend/app/routers/catalogos.py
Proyecto: FacturApp (backend)

Qué hace:
    Las rutas de los catálogos y del inventario.

    Consultar (Admin y Oficina radicadora):
        GET  /api/categorias, /api/categorias/{id}
        GET  /api/repuestos,  /api/repuestos/{id}     (sin stock: RN-02)
        GET  /api/contratistas, /api/contratistas/{id}
    Crear, editar, activar o desactivar (solo Admin):
        POST, PUT /{id} y PATCH /{id}/estado en los tres catálogos
    Stock (solo Admin):
        GET  /api/inventario
        GET  /api/inventario/entradas
        POST /api/inventario/entradas   la única forma de subir el stock (RN-09)

    No hay rutas DELETE: nada se borra, se desactiva (RN-05).

Conceptos:
    - ?activo=true en la dirección: filtro opcional ("parámetro de consulta").
    - status_code=201: la respuesta de "crear" es 201 Created.
"""

from typing import Any

from fastapi import APIRouter, Depends, status

from app.core.dependencias import requiere_admin, usuario_actual
from app.db.conexion import obtener_conexion
from app.repositories.tablas import Usuario
from app.schemas.catalogos import (CategoriaEntrada, CategoriaSalida, ContratistaEntrada, ContratistaSalida,
                                   EntradaAlmacenEntrada, EntradaAlmacenSalida, EntradaRegistradaSalida,
                                   InventarioSalida, RepuestoEntrada, RepuestoSalida)
from app.schemas.comunes import EstadoEntrada
from app.services import catalogos_service as servicio
from app.services import inventario_service

router = APIRouter(tags=["catálogos"])

# Atajos para no repetir las dependencias en cada ruta.
TODOS = Depends(usuario_actual)
ADMIN = Depends(requiere_admin)
CONEXION = Depends(obtener_conexion)


# ---------------------------------------------------------------- categorías

@router.get("/categorias", response_model=list[CategoriaSalida])
def listar_categorias(activo: bool | None = None, _u: Usuario = TODOS, conexion: Any = CONEXION):
    """Lista las categorías (todos los roles)."""
    return servicio.listar_categorias(conexion, activo)


@router.get("/categorias/{categoria_id}", response_model=CategoriaSalida)
def ver_categoria(categoria_id: int, _u: Usuario = TODOS, conexion: Any = CONEXION):
    """Devuelve una categoría (todos los roles)."""
    return servicio.obtener_categoria(conexion, categoria_id)


@router.post("/categorias", response_model=CategoriaSalida, status_code=status.HTTP_201_CREATED)
def crear_categoria(datos: CategoriaEntrada, _a: Usuario = ADMIN, conexion: Any = CONEXION):
    """Crea una categoría (solo Admin)."""
    return servicio.crear_categoria(conexion, datos)


@router.put("/categorias/{categoria_id}", response_model=CategoriaSalida)
def editar_categoria(categoria_id: int, datos: CategoriaEntrada, _a: Usuario = ADMIN, conexion: Any = CONEXION):
    """Cambia el nombre de una categoría (solo Admin)."""
    return servicio.editar_categoria(conexion, categoria_id, datos)


@router.patch("/categorias/{categoria_id}/estado", response_model=CategoriaSalida)
def estado_categoria(categoria_id: int, datos: EstadoEntrada, _a: Usuario = ADMIN, conexion: Any = CONEXION):
    """Activa o desactiva una categoría (solo Admin, RN-06)."""
    return servicio.cambiar_estado_categoria(conexion, categoria_id, datos.activo)


# ---------------------------------------------------------------- repuestos

@router.get("/repuestos", response_model=list[RepuestoSalida])
def listar_repuestos(activo: bool | None = None, _u: Usuario = TODOS, conexion: Any = CONEXION):
    """Lista el catálogo de repuestos, sin stock (todos los roles)."""
    return servicio.listar_repuestos(conexion, activo)


@router.get("/repuestos/{repuesto_id}", response_model=RepuestoSalida)
def ver_repuesto(repuesto_id: int, _u: Usuario = TODOS, conexion: Any = CONEXION):
    """Devuelve un repuesto del catálogo (todos los roles)."""
    return servicio.obtener_repuesto(conexion, repuesto_id)


@router.post("/repuestos", response_model=RepuestoSalida, status_code=status.HTTP_201_CREATED)
def crear_repuesto(datos: RepuestoEntrada, _a: Usuario = ADMIN, conexion: Any = CONEXION):
    """Crea un repuesto con stock 0 (solo Admin)."""
    return servicio.crear_repuesto(conexion, datos)


@router.put("/repuestos/{repuesto_id}", response_model=RepuestoSalida)
def editar_repuesto(repuesto_id: int, datos: RepuestoEntrada, _a: Usuario = ADMIN, conexion: Any = CONEXION):
    """Cambia los datos del catálogo de un repuesto; nunca el stock (solo Admin)."""
    return servicio.editar_repuesto(conexion, repuesto_id, datos)


@router.patch("/repuestos/{repuesto_id}/estado", response_model=RepuestoSalida)
def estado_repuesto(repuesto_id: int, datos: EstadoEntrada, _a: Usuario = ADMIN, conexion: Any = CONEXION):
    """Activa o desactiva un repuesto (solo Admin)."""
    return servicio.cambiar_estado_repuesto(conexion, repuesto_id, datos.activo)


# ---------------------------------------------------------------- contratistas

@router.get("/contratistas", response_model=list[ContratistaSalida])
def listar_contratistas(activo: bool | None = None, _u: Usuario = TODOS, conexion: Any = CONEXION):
    """Lista los contratistas (todos los roles)."""
    return servicio.listar_contratistas(conexion, activo)


@router.get("/contratistas/{contratista_id}", response_model=ContratistaSalida)
def ver_contratista(contratista_id: int, _u: Usuario = TODOS, conexion: Any = CONEXION):
    """Devuelve un contratista (todos los roles)."""
    return servicio.obtener_contratista(conexion, contratista_id)


@router.post("/contratistas", response_model=ContratistaSalida, status_code=status.HTTP_201_CREATED)
def crear_contratista(datos: ContratistaEntrada, _a: Usuario = ADMIN, conexion: Any = CONEXION):
    """Crea un contratista (solo Admin)."""
    return servicio.crear_contratista(conexion, datos)


@router.put("/contratistas/{contratista_id}", response_model=ContratistaSalida)
def editar_contratista(contratista_id: int, datos: ContratistaEntrada, _a: Usuario = ADMIN,
                       conexion: Any = CONEXION):
    """Cambia los datos de un contratista (solo Admin)."""
    return servicio.editar_contratista(conexion, contratista_id, datos)


@router.patch("/contratistas/{contratista_id}/estado", response_model=ContratistaSalida)
def estado_contratista(contratista_id: int, datos: EstadoEntrada, _a: Usuario = ADMIN, conexion: Any = CONEXION):
    """Activa o desactiva un contratista (solo Admin)."""
    return servicio.cambiar_estado_contratista(conexion, contratista_id, datos.activo)


# ---------------------------------------------------------------- inventario (solo Admin)

@router.get("/inventario", response_model=list[InventarioSalida])
def ver_inventario(_a: Usuario = ADMIN, conexion: Any = CONEXION):
    """Stock en almacén, apartado, disponible y en espera de cada repuesto (HU-20)."""
    return inventario_service.listar_inventario(conexion)


@router.get("/inventario/entradas", response_model=list[EntradaAlmacenSalida])
def listar_entradas(repuesto_id: int | None = None, _a: Usuario = ADMIN, conexion: Any = CONEXION):
    """Entradas al almacén, de la más reciente a la más antigua."""
    return inventario_service.listar_entradas(conexion, repuesto_id)


@router.post("/inventario/entradas", response_model=EntradaRegistradaSalida, status_code=status.HTTP_201_CREATED)
def registrar_entrada(datos: EntradaAlmacenEntrada, admin: Usuario = ADMIN, conexion: Any = CONEXION):
    """Registra mercancía que llega: sube el stock y aparta para solicitudes en espera (HU-19, RN-33)."""
    return inventario_service.registrar_entrada(conexion, datos, admin)
