"""
Archivo:  backend/app/repositories/inventario_repo.py
Proyecto: FacturApp (backend)

Qué hace:
    Consultas SQL del stock: el inventario, las entradas al almacén, los
    movimientos de inventario y lo que las solicitudes tienen apartado o
    en espera. Las usan los services de inventario y de entregas.

Recordatorio (RN-09): el stock nunca se escribe a mano; solo cambia con
estas funciones, y cada cambio deja su movimiento de inventario.
"""

from decimal import Decimal
from typing import Any

# Lo que una fila del detalle tiene "en espera": lo pedido que todavía no
# se ha entregado, ni apartado, ni pasado a otro repuesto (RN-33).
EN_ESPERA = ("(ds.cantidad_solicitada - ds.cantidad_reemplazada - ds.cantidad_entregada - ds.cantidad_apartada)")


def listar_inventario(conexion: Any) -> list[dict[str, Any]]:
    """Stock de cada repuesto: en almacén, apartado, disponible y en espera (HU-20).

    "En espera" solo cuenta las solicitudes abiertas.
    """
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT r.id, r.codigo, r.nombre, r.unidad_medida, r.stock_almacen, r.stock_apartado, "
            "(r.stock_almacen - r.stock_apartado) AS disponible, "
            f"COALESCE((SELECT SUM({EN_ESPERA}) FROM detalle_solicitud ds "
            "JOIN solicitudes s ON s.id = ds.solicitud_id "
            "WHERE ds.repuesto_id = r.id AND s.estado = 'abierta'), 0) AS en_espera, r.activo "
            "FROM repuestos r ORDER BY r.codigo"
        )
        return cursor.fetchall()


def sumar_stock_almacen(conexion: Any, repuesto_id: int, cantidad: Decimal) -> None:
    """Suma (o resta, si la cantidad es negativa) al stock en almacén.

    Si el resultado quedara negativo o por debajo de lo apartado, los
    CHECK de la base de datos lo rechazan (RN-10, RN-27).
    """
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE repuestos SET stock_almacen = stock_almacen + %s WHERE id = %s",
                       (cantidad, repuesto_id))


def sumar_stock_apartado(conexion: Any, repuesto_id: int, cantidad: Decimal) -> None:
    """Suma (o resta) a lo apartado de un repuesto."""
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE repuestos SET stock_apartado = stock_apartado + %s WHERE id = %s",
                       (cantidad, repuesto_id))


def crear_entrada(conexion: Any, repuesto_id: int, cantidad: Decimal, observacion: str | None,
                  usuario_id: int) -> int:
    """Guarda una entrada al almacén. La fecha la pone la base de datos (RN-20)."""
    with conexion.cursor() as cursor:
        cursor.execute("INSERT INTO entradas_almacen (repuesto_id, cantidad, observacion, registrado_por) "
                       "VALUES (%s, %s, %s, %s)", (repuesto_id, cantidad, observacion, usuario_id))
        return cursor.lastrowid


def listar_entradas(conexion: Any, repuesto_id: int | None = None) -> list[dict[str, Any]]:
    """Entradas al almacén, de la más reciente a la más antigua, con el repuesto y el usuario."""
    filtro, parametros = ("WHERE e.repuesto_id = %s ", (repuesto_id,)) if repuesto_id else ("", ())
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT e.id, e.repuesto_id, r.codigo, r.nombre AS repuesto, e.cantidad, e.observacion, "
            "e.registrado_por, u.nombre AS registrado_por_nombre, e.registrado_en, e.retractada, e.motivo_retraccion "
            "FROM entradas_almacen e JOIN repuestos r ON r.id = e.repuesto_id "
            f"JOIN usuarios u ON u.id = e.registrado_por {filtro}ORDER BY e.registrado_en DESC, e.id DESC",
            parametros,
        )
        return cursor.fetchall()


def crear_movimiento(conexion: Any, repuesto_id: int, tipo: str, cantidad: Decimal, stock_resultante: Decimal,
                     usuario_id: int, entrada_id: int | None = None, entrega_id: int | None = None,
                     devolucion_id: int | None = None) -> None:
    """Deja el rastro de un cambio de stock en movimientos_inventario (HU-27)."""
    with conexion.cursor() as cursor:
        cursor.execute(
            "INSERT INTO movimientos_inventario (repuesto_id, tipo, cantidad, stock_resultante, "
            "entrada_id, entrega_id, devolucion_id, usuario_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (repuesto_id, tipo, cantidad, stock_resultante, entrada_id, entrega_id, devolucion_id, usuario_id),
        )


def detalles_en_espera(conexion: Any, repuesto_id: int) -> list[dict[str, Any]]:
    """Filas de solicitudes abiertas que esperan este repuesto, de la solicitud más antigua a la más nueva.

    FOR UPDATE las reserva para que dos entradas al mismo tiempo no
    aparten la misma mercancía dos veces (RN-33).
    """
    with conexion.cursor() as cursor:
        cursor.execute(
            f"SELECT ds.id, ds.solicitud_id, {EN_ESPERA} AS en_espera FROM detalle_solicitud ds "
            "JOIN solicitudes s ON s.id = ds.solicitud_id "
            f"WHERE ds.repuesto_id = %s AND s.estado = 'abierta' AND {EN_ESPERA} > 0 "
            "ORDER BY s.creado_en, s.id FOR UPDATE",
            (repuesto_id,),
        )
        return cursor.fetchall()


def sumar_apartado_detalle(conexion: Any, detalle_id: int, cantidad: Decimal) -> None:
    """Suma (o resta) a lo apartado de una fila del detalle de una solicitud."""
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE detalle_solicitud SET cantidad_apartada = cantidad_apartada + %s WHERE id = %s",
                       (cantidad, detalle_id))
