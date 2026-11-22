"""
Archivo:  backend/app/services/inventario_service.py
Proyecto: FacturApp (backend)

Qué hace:
    Las reglas del stock que no son entregas: consultar el inventario y
    registrar entradas al almacén (la única forma de aumentar el stock,
    RN-09).

Al registrar una entrada (todo dentro de una transacción):
    1. Bloquea el repuesto (FOR UPDATE) y revisa que exista y esté activo.
    2. Revisa la cantidad según la unidad (RN-12): entera si es "unidad".
    3. Suma el stock y guarda la entrada y su movimiento de inventario.
    4. RN-33: aparta la mercancía nueva para las solicitudes abiertas que
       la esperaban, de la más antigua a la más reciente.
"""

from decimal import Decimal
from typing import Any

from app.core.errores import Conflicto, DatosInvalidos, NoEncontrado
from app.repositories import catalogos_repo, inventario_repo
from app.repositories.tablas import Usuario
from app.schemas.catalogos import EntradaAlmacenEntrada


def revisar_cantidad_por_unidad(unidad_medida: str, cantidad: Decimal, campo: str = "cantidad") -> None:
    """RN-12: si el repuesto se cuenta en unidades, la cantidad debe ser entera."""
    if unidad_medida == "unidad" and cantidad != cantidad.to_integral_value():
        mensaje = "Este repuesto se maneja en unidades enteras. Escriba una cantidad sin decimales."
        raise DatosInvalidos("CANTIDAD_INVALIDA", mensaje, {campo: mensaje})


def listar_inventario(conexion: Any) -> list[dict[str, Any]]:
    """Stock de todos los repuestos (HU-20)."""
    return inventario_repo.listar_inventario(conexion)


def listar_entradas(conexion: Any, repuesto_id: int | None) -> list[dict[str, Any]]:
    """Entradas al almacén, de la más reciente a la más antigua."""
    return inventario_repo.listar_entradas(conexion, repuesto_id)


def registrar_entrada(conexion: Any, datos: EntradaAlmacenEntrada, usuario: Usuario) -> dict[str, Any]:
    """Registra mercancía que llega al almacén (HU-19)."""
    repuesto = catalogos_repo.buscar_repuesto(conexion, datos.repuesto_id, bloquear=True)
    if repuesto is None:
        raise NoEncontrado("NO_ENCONTRADO", "El repuesto no existe.")
    if not repuesto.activo:
        raise Conflicto("REPUESTO_INACTIVO", "El repuesto está desactivado; no se le pueden registrar entradas.")
    revisar_cantidad_por_unidad(repuesto.unidad_medida, datos.cantidad)

    # Paso 3: sube el stock y deja el rastro.
    entrada_id = inventario_repo.crear_entrada(conexion, repuesto.id, datos.cantidad, datos.observacion, usuario.id)
    inventario_repo.sumar_stock_almacen(conexion, repuesto.id, datos.cantidad)
    stock_nuevo = repuesto.stock_almacen + datos.cantidad
    inventario_repo.crear_movimiento(conexion, repuesto.id, "entrada", datos.cantidad, stock_nuevo, usuario.id,
                                     entrada_id=entrada_id)

    # Paso 4 (RN-33): reparte la mercancía nueva entre las solicitudes en espera.
    libre = stock_nuevo - repuesto.stock_apartado
    apartado_total = Decimal("0")
    for detalle in inventario_repo.detalles_en_espera(conexion, repuesto.id):
        if libre <= 0:
            break
        cantidad = min(libre, detalle["en_espera"])
        inventario_repo.sumar_apartado_detalle(conexion, detalle["id"], cantidad)
        apartado_total += cantidad
        libre -= cantidad
    if apartado_total:
        inventario_repo.sumar_stock_apartado(conexion, repuesto.id, apartado_total)

    return {"entrada_id": entrada_id, "repuesto_id": repuesto.id, "stock_almacen": stock_nuevo,
            "apartado_para_solicitudes": apartado_total}
