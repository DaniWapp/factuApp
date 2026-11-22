"""
Archivo:  backend/app/repositories/entregas_repo.py
Proyecto: FacturApp (backend)

Qué hace:
    Consultas SQL de las entregas (remisiones), de su detalle, de las
    solicitudes y del consecutivo de remisiones. Todas usan parámetros %s
    (RNF-05) y reciben una conexión abierta, para que la entrega completa
    vaya dentro de UNA transacción (ver services/entregas_service.py).
"""

from decimal import Decimal
from typing import Any


# ---------------------------------------------------------------- solicitud y su detalle

def bloquear_solicitud(conexion: Any, solicitud_id: int) -> dict[str, Any] | None:
    """Lee la solicitud y la bloquea (FOR UPDATE) hasta el final de la transacción."""
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT s.id, s.numero, s.estado, s.contratista_id, c.activo AS contratista_activo "
            "FROM solicitudes s JOIN contratistas c ON c.id = s.contratista_id WHERE s.id = %s FOR UPDATE",
            (solicitud_id,),
        )
        return cursor.fetchone()


def bloquear_detalle(conexion: Any, solicitud_id: int) -> dict[int, dict[str, Any]]:
    """Lee y bloquea las filas del detalle de la solicitud. Devuelve {repuesto_id: fila}."""
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT id, repuesto_id, cantidad_solicitada, cantidad_apartada, cantidad_entregada, "
            "cantidad_reemplazada FROM detalle_solicitud WHERE solicitud_id = %s FOR UPDATE",
            (solicitud_id,),
        )
        return {fila["repuesto_id"]: fila for fila in cursor.fetchall()}


def bloquear_repuestos(conexion: Any, ids: list[int]) -> dict[int, dict[str, Any]]:
    """Lee y bloquea los repuestos de la entrega, en orden de id. Devuelve {id: fila}.

    Se bloquean siempre en el mismo orden (de menor a mayor id) para que
    dos entregas al mismo tiempo no se queden esperándose la una a la
    otra para siempre (eso se llama "interbloqueo" o deadlock).
    """
    marcadores = ", ".join(["%s"] * len(ids))
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT id, codigo, nombre, unidad_medida, stock_almacen, stock_apartado "
            f"FROM repuestos WHERE id IN ({marcadores}) ORDER BY id FOR UPDATE",
            tuple(sorted(ids)),
        )
        return {fila["id"]: fila for fila in cursor.fetchall()}


def registrar_entrega_en_detalle(conexion: Any, detalle_id: int, entregado: Decimal, de_apartado: Decimal) -> None:
    """Suma lo entregado y descuenta de lo apartado en la fila del detalle de la solicitud."""
    with conexion.cursor() as cursor:
        cursor.execute(
            "UPDATE detalle_solicitud SET cantidad_entregada = cantidad_entregada + %s, "
            "cantidad_apartada = cantidad_apartada - %s WHERE id = %s",
            (entregado, de_apartado, detalle_id),
        )


def descontar_stock(conexion: Any, repuesto_id: int, cantidad: Decimal, de_apartado: Decimal) -> None:
    """Baja el stock en almacén y lo apartado de un repuesto."""
    with conexion.cursor() as cursor:
        cursor.execute(
            "UPDATE repuestos SET stock_almacen = stock_almacen - %s, stock_apartado = stock_apartado - %s "
            "WHERE id = %s",
            (cantidad, de_apartado, repuesto_id),
        )


def resumen_entrega_solicitud(conexion: Any, solicitud_id: int) -> dict[str, Decimal]:
    """Suma lo entregado y lo pendiente de toda la solicitud, para calcular su estado (RN-21)."""
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT COALESCE(SUM(cantidad_entregada), 0) AS entregado, "
            "COALESCE(SUM(cantidad_solicitada - cantidad_reemplazada - cantidad_entregada), 0) AS pendiente "
            "FROM detalle_solicitud WHERE solicitud_id = %s",
            (solicitud_id,),
        )
        return cursor.fetchone()


# ---------------------------------------------------------------- consecutivo y entrega

def siguiente_numero(conexion: Any, tipo: str) -> int:
    """Toma el siguiente número del consecutivo (RN-18).

    FOR UPDATE bloquea la fila del contador: si dos entregas llegan al
    mismo tiempo, la segunda espera a que la primera termine, así nunca
    salen dos remisiones con el mismo número. Y como el aumento va en la
    misma transacción, si la entrega falla también se deshace, así que
    no quedan números saltados.
    """
    with conexion.cursor() as cursor:
        cursor.execute("SELECT ultimo_numero FROM consecutivos WHERE tipo = %s FOR UPDATE", (tipo,))
        numero = int(cursor.fetchone()["ultimo_numero"]) + 1
        cursor.execute("UPDATE consecutivos SET ultimo_numero = %s WHERE tipo = %s", (numero, tipo))
    return numero


def crear_entrega(conexion: Any, numero_remision: str, solicitud_id: int, contratista_id: int,
                  usuario_id: int) -> int:
    """Guarda la entrega. La fecha y hora las pone la base de datos (RN-20)."""
    with conexion.cursor() as cursor:
        cursor.execute(
            "INSERT INTO entregas (numero_remision, solicitud_id, contratista_id, registrado_por) "
            "VALUES (%s, %s, %s, %s)",
            (numero_remision, solicitud_id, contratista_id, usuario_id),
        )
        return cursor.lastrowid


def crear_detalle_entrega(conexion: Any, entrega_id: int, repuesto_id: int, cantidad: Decimal) -> None:
    """Guarda un repuesto entregado en la remisión."""
    with conexion.cursor() as cursor:
        cursor.execute("INSERT INTO detalle_entrega (entrega_id, repuesto_id, cantidad) VALUES (%s, %s, %s)",
                       (entrega_id, repuesto_id, cantidad))


def crear_historial(conexion: Any, solicitud_id: int, accion: str, detalle: str, usuario_id: int,
                    motivo: str | None = None) -> None:
    """Deja una línea en la línea de tiempo de la solicitud (HU-18)."""
    with conexion.cursor() as cursor:
        cursor.execute(
            "INSERT INTO historial_solicitud (solicitud_id, accion, detalle, motivo, usuario_id) "
            "VALUES (%s, %s, %s, %s, %s)",
            (solicitud_id, accion, detalle, motivo, usuario_id),
        )


# ---------------------------------------------------------------- consultas para listar y ver

def listar(conexion: Any, solicitud_id: int | None = None) -> list[dict[str, Any]]:
    """Entregas de la más reciente a la más antigua, con solicitud, contratista y usuario."""
    filtro, parametros = ("WHERE e.solicitud_id = %s ", (solicitud_id,)) if solicitud_id else ("", ())
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT e.id, e.numero_remision, e.solicitud_id, s.numero AS solicitud, c.nombre AS contratista, "
            "u.nombre AS registrado_por, e.registrado_en, e.retractada, "
            "(SELECT COUNT(*) FROM detalle_entrega d WHERE d.entrega_id = e.id) AS repuestos "
            "FROM entregas e JOIN solicitudes s ON s.id = e.solicitud_id "
            "JOIN contratistas c ON c.id = e.contratista_id JOIN usuarios u ON u.id = e.registrado_por "
            f"{filtro}ORDER BY e.registrado_en DESC, e.id DESC",
            parametros,
        )
        return cursor.fetchall()


def buscar_cabecera(conexion: Any, entrega_id: int) -> dict[str, Any] | None:
    """Datos de la remisión: entrega, solicitud, equipo, contratista y usuario que la registró."""
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT e.id, e.numero_remision, e.registrado_en, e.retractada, e.motivo_retraccion, e.retractada_en, "
            "s.id AS solicitud_id, s.numero AS solicitud_numero, "
            "eq.codigo AS equipo_codigo, eq.descripcion AS equipo_descripcion, "
            "c.id AS contratista_id, c.nombre AS contratista_nombre, c.documento AS contratista_documento, "
            "c.telefono AS contratista_telefono, u.id AS usuario_id, u.nombre AS usuario_nombre "
            "FROM entregas e JOIN solicitudes s ON s.id = e.solicitud_id JOIN equipos eq ON eq.id = s.equipo_id "
            "JOIN contratistas c ON c.id = e.contratista_id JOIN usuarios u ON u.id = e.registrado_por "
            "WHERE e.id = %s",
            (entrega_id,),
        )
        return cursor.fetchone()


def buscar_repuestos_entregados(conexion: Any, entrega_id: int) -> list[dict[str, Any]]:
    """Repuestos y cantidades de una entrega, en orden de código."""
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT d.repuesto_id, r.codigo, r.nombre, r.unidad_medida, d.cantidad "
            "FROM detalle_entrega d JOIN repuestos r ON r.id = d.repuesto_id WHERE d.entrega_id = %s ORDER BY r.codigo",
            (entrega_id,),
        )
        return cursor.fetchall()
