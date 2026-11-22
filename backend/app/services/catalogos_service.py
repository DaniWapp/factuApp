"""
Archivo:  backend/app/services/catalogos_service.py
Proyecto: FacturApp (backend)

Qué hace:
    Las reglas de negocio de categorías, repuestos y contratistas.

Reglas:
    - Nada se borra: los registros se desactivan (RN-05). No hay
      funciones de borrar.
    - Nombres de categoría, y código y nombre de repuesto, no se repiten
      (RN-07); la cédula o NIT de un contratista tampoco (RN-08).
    - No se desactiva una categoría con repuestos activos (RN-06).
    - Un repuesto solo puede usar una categoría que exista y esté activa.
    - Un repuesto nuevo empieza con stock 0; el stock nunca se edita aquí
      (RN-09): cambia con las entradas y las entregas.
"""

import re
from typing import Any

from app.core.errores import Conflicto, NoEncontrado
from app.repositories import catalogos_repo as repo
from app.repositories.tablas import Categoria, Contratista
from app.schemas.catalogos import CategoriaEntrada, ContratistaEntrada, RepuestoEntrada


# ---------------------------------------------------------------- categorías

def listar_categorias(conexion: Any, activo: bool | None) -> list[dict[str, Any]]:
    """Categorías con su cantidad de repuestos activos."""
    return repo.listar_categorias(conexion, activo)


def obtener_categoria(conexion: Any, categoria_id: int, bloquear: bool = False) -> dict[str, Any]:
    """Una categoría con su cantidad de repuestos activos, o 404."""
    categoria = repo.buscar_categoria(conexion, categoria_id, bloquear)
    if categoria is None:
        raise NoEncontrado("NO_ENCONTRADO", "La categoría no existe.")
    return {**categoria.__dict__, "repuestos_activos": repo.contar_repuestos_activos(conexion, categoria_id)}


def _revisar_nombre_categoria(conexion: Any, nombre: str, excepto_id: int | None = None) -> None:
    """RN-07: lanza 409 si otra categoría ya tiene ese nombre."""
    otra = repo.buscar_categoria_por_nombre(conexion, nombre)
    if otra is not None and otra.id != excepto_id:
        raise Conflicto("NOMBRE_REPETIDO", "Ya existe una categoría con ese nombre.",
                        {"nombre": "Ya existe una categoría con ese nombre."})


def crear_categoria(conexion: Any, datos: CategoriaEntrada) -> dict[str, Any]:
    """Crea una categoría activa."""
    _revisar_nombre_categoria(conexion, datos.nombre)
    return obtener_categoria(conexion, repo.crear_categoria(conexion, datos.nombre))


def editar_categoria(conexion: Any, categoria_id: int, datos: CategoriaEntrada) -> dict[str, Any]:
    """Cambia el nombre de una categoría."""
    obtener_categoria(conexion, categoria_id, bloquear=True)
    _revisar_nombre_categoria(conexion, datos.nombre, excepto_id=categoria_id)
    repo.actualizar_categoria(conexion, categoria_id, datos.nombre)
    return obtener_categoria(conexion, categoria_id)


def cambiar_estado_categoria(conexion: Any, categoria_id: int, activo: bool) -> dict[str, Any]:
    """Activa o desactiva una categoría. RN-06: no se desactiva si tiene repuestos activos."""
    obtener_categoria(conexion, categoria_id, bloquear=True)
    if not activo and repo.contar_repuestos_activos(conexion, categoria_id) > 0:
        raise Conflicto("CATEGORIA_CON_REPUESTOS",
                        "Esta categoría tiene repuestos activos. Cámbielos de categoría o desactívelos primero.")
    repo.cambiar_estado_categoria(conexion, categoria_id, activo)
    return obtener_categoria(conexion, categoria_id)


# ---------------------------------------------------------------- repuestos

def listar_repuestos(conexion: Any, activo: bool | None) -> list[dict[str, Any]]:
    """Catálogo de repuestos, sin stock."""
    return repo.listar_repuestos(conexion, activo)


def obtener_repuesto(conexion: Any, repuesto_id: int) -> dict[str, Any]:
    """Un repuesto del catálogo (sin stock), o 404."""
    for fila in repo.listar_repuestos(conexion):
        if fila["id"] == repuesto_id:
            return fila
    raise NoEncontrado("NO_ENCONTRADO", "El repuesto no existe.")


def _revisar_repuesto(conexion: Any, datos: RepuestoEntrada, excepto_id: int | None = None) -> None:
    """Revisa que la categoría sirva y que el código y el nombre no se repitan (RN-07)."""
    categoria: Categoria | None = repo.buscar_categoria(conexion, datos.categoria_id)
    if categoria is None or not categoria.activo:
        raise Conflicto("CATEGORIA_NO_DISPONIBLE", "La categoría no existe o está desactivada.",
                        {"categoria_id": "Elija una categoría activa."})
    for columna, mensaje in (("codigo", "Ya existe un repuesto con ese código."),
                             ("nombre", "Ya existe un repuesto con ese nombre.")):
        otro = repo.buscar_repuesto_por(conexion, columna, getattr(datos, columna))
        if otro is not None and otro.id != excepto_id:
            raise Conflicto(f"{columna.upper()}_REPETIDO", mensaje, {columna: mensaje})


def crear_repuesto(conexion: Any, datos: RepuestoEntrada) -> dict[str, Any]:
    """Crea un repuesto activo con stock 0 (RN-09)."""
    _revisar_repuesto(conexion, datos)
    nuevo_id = repo.crear_repuesto(conexion, datos.codigo, datos.nombre, datos.categoria_id, datos.unidad_medida)
    return obtener_repuesto(conexion, nuevo_id)


def editar_repuesto(conexion: Any, repuesto_id: int, datos: RepuestoEntrada) -> dict[str, Any]:
    """Cambia los datos del catálogo; el stock no se toca."""
    actual = repo.buscar_repuesto(conexion, repuesto_id, bloquear=True)
    if actual is None:
        raise NoEncontrado("NO_ENCONTRADO", "El repuesto no existe.")
    _revisar_repuesto(conexion, datos, excepto_id=repuesto_id)
    # RN-12: no se puede pasar a "unidad" un repuesto que tiene stock con decimales.
    if datos.unidad_medida == "unidad" and actual.stock_almacen != actual.stock_almacen.to_integral_value():
        raise Conflicto("UNIDAD_NO_COMPATIBLE", "El stock tiene decimales; no se puede cambiar a unidades.")
    repo.actualizar_repuesto(conexion, repuesto_id, datos.codigo, datos.nombre, datos.categoria_id,
                             datos.unidad_medida)
    return obtener_repuesto(conexion, repuesto_id)


def cambiar_estado_repuesto(conexion: Any, repuesto_id: int, activo: bool) -> dict[str, Any]:
    """Activa o desactiva un repuesto. Su historial se conserva (RN-05)."""
    if repo.buscar_repuesto(conexion, repuesto_id, bloquear=True) is None:
        raise NoEncontrado("NO_ENCONTRADO", "El repuesto no existe.")
    repo.cambiar_estado_repuesto(conexion, repuesto_id, activo)
    return obtener_repuesto(conexion, repuesto_id)


# ---------------------------------------------------------------- contratistas

def normalizar_documento(documento: str) -> str:
    """RN-08: deja solo los dígitos. "900.456.789-1" y "9004567891" son el mismo documento."""
    return re.sub(r"\D", "", documento)


def listar_contratistas(conexion: Any, activo: bool | None) -> list[Contratista]:
    """Contratistas ordenados por nombre."""
    return repo.listar_contratistas(conexion, activo)


def obtener_contratista(conexion: Any, contratista_id: int, bloquear: bool = False) -> Contratista:
    """Un contratista, o 404."""
    contratista = repo.buscar_contratista(conexion, contratista_id, bloquear)
    if contratista is None:
        raise NoEncontrado("NO_ENCONTRADO", "El contratista no existe.")
    return contratista


def _revisar_documento(conexion: Any, normalizado: str, excepto_id: int | None = None) -> None:
    """RN-08: lanza 409 si otro contratista ya tiene ese documento. El nombre sí puede repetirse."""
    otro = repo.buscar_contratista_por_documento(conexion, normalizado)
    if otro is not None and otro.id != excepto_id:
        raise Conflicto("DOCUMENTO_REPETIDO", "Ya existe un contratista con ese documento.",
                        {"documento": "Ya existe un contratista con ese documento."})


def crear_contratista(conexion: Any, datos: ContratistaEntrada) -> Contratista:
    """Crea un contratista activo."""
    normalizado = normalizar_documento(datos.documento)
    _revisar_documento(conexion, normalizado)
    nuevo_id = repo.crear_contratista(conexion, datos.documento, normalizado, datos.nombre, datos.telefono)
    return obtener_contratista(conexion, nuevo_id)


def editar_contratista(conexion: Any, contratista_id: int, datos: ContratistaEntrada) -> Contratista:
    """Cambia los datos de un contratista."""
    obtener_contratista(conexion, contratista_id, bloquear=True)
    normalizado = normalizar_documento(datos.documento)
    _revisar_documento(conexion, normalizado, excepto_id=contratista_id)
    repo.actualizar_contratista(conexion, contratista_id, datos.documento, normalizado, datos.nombre,
                                datos.telefono)
    return obtener_contratista(conexion, contratista_id)


def cambiar_estado_contratista(conexion: Any, contratista_id: int, activo: bool) -> Contratista:
    """Activa o desactiva un contratista. Sus solicitudes y remisiones no cambian (RN-05, RN-31)."""
    obtener_contratista(conexion, contratista_id, bloquear=True)
    repo.cambiar_estado_contratista(conexion, contratista_id, activo)
    return obtener_contratista(conexion, contratista_id)
