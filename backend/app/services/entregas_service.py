"""
Archivo:  backend/app/services/entregas_service.py
Proyecto: FacturApp (backend)

Qué hace:
    Registra una entrega de repuestos de una solicitud y genera su
    remisión (HU-21). También lista las entregas y arma la remisión para
    verla o imprimirla (HU-24).

---------------------------------------------------------------------
¿QUÉ ES UNA TRANSACCIÓN?
    Un grupo de cambios en la base de datos que se guarda COMPLETO o NO
    SE GUARDA (RN-17). Una entrega cambia varias tablas: baja el stock,
    actualiza lo entregado de la solicitud, aumenta el consecutivo, crea
    la remisión, su detalle, los movimientos de inventario y el
    historial. Si algo falla a mitad de camino (por ejemplo, el tercer
    repuesto no alcanza), la base de datos deshace todo lo anterior
    (ROLLBACK), como si nada hubiera pasado. Si todo sale bien, se guarda
    de una sola vez (COMMIT).
    Aquí la transacción la abre obtener_conexion (app/db/conexion.py)
    para toda la petición: si este service lanza un error, nada se guarda.

¿POR QUÉ BLOQUEAMOS LAS FILAS (SELECT ... FOR UPDATE)?
    Imagine que quedan 2 motores y dos personas registran al mismo tiempo
    una entrega de 2 motores cada una. Sin bloqueo, las dos leen "hay 2",
    las dos aprueban y el stock termina en -2. Con FOR UPDATE, la primera
    reserva la fila del repuesto; la segunda tiene que ESPERAR hasta que
    la primera termine, y cuando por fin lee, ya ve el stock real (0) y
    se rechaza. Lo mismo con la fila de la solicitud y con el contador de
    remisiones, para que no se repitan números (RN-18).
    El bloqueo dura solo hasta el COMMIT o el ROLLBACK.
---------------------------------------------------------------------

De dónde sale lo que se entrega:
    Primero de lo APARTADO para esta solicitud y, si no alcanza, del
    stock LIBRE del almacén (en almacén - apartado para todos). Si ni así
    alcanza, se rechaza la entrega completa y se dice qué repuesto falta.
"""

from decimal import Decimal
from typing import Any

from app.core.errores import Conflicto, NoEncontrado
from app.repositories import entregas_repo, inventario_repo
from app.repositories.tablas import Usuario
from app.schemas.entregas import EntregaEntrada
from app.services.inventario_service import revisar_cantidad_por_unidad


def _numero(valor: Decimal) -> str:
    """Muestra una cantidad sin ceros de más: 2.00 -> "2", 2.50 -> "2.5"."""
    return format(valor.normalize(), "f")


def estado_entrega(conexion: Any, solicitud_id: int) -> str:
    """RN-21: "Pendiente" si no se ha entregado nada, "Completa" si no falta nada, si no "Parcial"."""
    resumen = entregas_repo.resumen_entrega_solicitud(conexion, solicitud_id)
    if resumen["entregado"] == 0:
        return "Pendiente"
    return "Completa" if resumen["pendiente"] == 0 else "Parcial"


def registrar(conexion: Any, solicitud_id: int, datos: EntregaEntrada, usuario: Usuario) -> dict[str, Any]:
    """Registra una entrega completa o no registra nada."""

    # Paso 1: bloquear y revisar la solicitud.
    solicitud = entregas_repo.bloquear_solicitud(conexion, solicitud_id)
    if solicitud is None:
        raise NoEncontrado("NO_ENCONTRADO", "La solicitud no existe.")
    if solicitud["estado"] != "abierta":
        raise Conflicto("SOLICITUD_CERRADA", "La solicitud está cerrada. No se pueden registrar más cambios.")
    if not solicitud["contratista_activo"]:
        raise Conflicto("CONTRATISTA_INACTIVO", "El contratista de esta solicitud está desactivado. "
                        "Reasigne un contratista activo antes de registrar la entrega.")

    # Paso 2: bloquear el detalle de la solicitud y los repuestos (en orden de id).
    detalle = entregas_repo.bloquear_detalle(conexion, solicitud_id)
    repuestos = entregas_repo.bloquear_repuestos(conexion, [r.repuesto_id for r in datos.repuestos])

    # Paso 3: revisar TODOS los repuestos antes de cambiar nada.
    faltantes: dict[str, str] = {}
    plan = []  # lo que se va a hacer con cada repuesto, si todo está bien
    for posicion, pedido in enumerate(datos.repuestos):
        campo = f"repuestos.{posicion}.cantidad"
        fila = detalle.get(pedido.repuesto_id)
        repuesto = repuestos.get(pedido.repuesto_id)
        if fila is None or repuesto is None:
            raise Conflicto("REPUESTO_NO_SOLICITADO", "Ese repuesto no está en la solicitud.",
                            {f"repuestos.{posicion}.repuesto_id": "Ese repuesto no está en la solicitud."})
        revisar_cantidad_por_unidad(repuesto["unidad_medida"], pedido.cantidad, campo)  # RN-12

        pendiente = fila["cantidad_solicitada"] - fila["cantidad_reemplazada"] - fila["cantidad_entregada"]
        if pedido.cantidad > pendiente:  # RN-16
            raise Conflicto("MAS_DE_LO_PENDIENTE",
                            f"No puede entregar más de lo pendiente. Pendiente de {repuesto['codigo']}: "
                            f"{_numero(pendiente)}.", {campo: f"Pendiente: {_numero(pendiente)}."})

        libre = repuesto["stock_almacen"] - repuesto["stock_apartado"]
        disponible = fila["cantidad_apartada"] + libre
        if pedido.cantidad > disponible:  # RN-10
            faltantes[campo] = (f"No hay stock suficiente de {repuesto['codigo']} {repuesto['nombre']}. "
                                f"Disponible: {_numero(disponible)}.")
            continue
        de_apartado = min(pedido.cantidad, fila["cantidad_apartada"])
        plan.append((pedido, fila, repuesto, de_apartado))

    if faltantes:
        # No se guardó nada: todavía no se ha escrito en ninguna tabla, y
        # además la transacción se deshace al lanzar este error.
        primero = next(iter(faltantes.values()))
        raise Conflicto("STOCK_INSUFICIENTE", primero, faltantes)

    # Paso 4: número de remisión consecutivo (RN-18).
    numero_remision = f"REM-{entregas_repo.siguiente_numero(conexion, 'REM'):06d}"

    # Paso 5: guardar la entrega. La fecha y el usuario se ponen solos (RN-20).
    entrega_id = entregas_repo.crear_entrega(conexion, numero_remision, solicitud_id,
                                             solicitud["contratista_id"], usuario.id)

    # Paso 6: por cada repuesto, el detalle, la solicitud, el stock y el movimiento.
    for pedido, fila, repuesto, de_apartado in plan:
        entregas_repo.crear_detalle_entrega(conexion, entrega_id, pedido.repuesto_id, pedido.cantidad)
        entregas_repo.registrar_entrega_en_detalle(conexion, fila["id"], pedido.cantidad, de_apartado)
        entregas_repo.descontar_stock(conexion, pedido.repuesto_id, pedido.cantidad, de_apartado)
        inventario_repo.crear_movimiento(conexion, pedido.repuesto_id, "entrega", -pedido.cantidad,
                                         repuesto["stock_almacen"] - pedido.cantidad, usuario.id,
                                         entrega_id=entrega_id)

    # Paso 7: la línea de tiempo de la solicitud (HU-18).
    estado = estado_entrega(conexion, solicitud_id)
    entregas_repo.crear_historial(conexion, solicitud_id, "entrega",
                                  f"Remisión {numero_remision}: entrega {estado.lower()}", usuario.id)

    remision = obtener_remision(conexion, entrega_id)
    remision["estado_entrega"] = estado
    return remision


def listar(conexion: Any, solicitud_id: int | None) -> list[dict[str, Any]]:
    """Entregas de la más reciente a la más antigua."""
    return entregas_repo.listar(conexion, solicitud_id)


def obtener_remision(conexion: Any, entrega_id: int) -> dict[str, Any]:
    """Arma la remisión: entrega, solicitud, equipo, contratista, usuario y repuestos (HU-24)."""
    cabecera = entregas_repo.buscar_cabecera(conexion, entrega_id)
    if cabecera is None:
        raise NoEncontrado("NO_ENCONTRADO", "La entrega no existe.")
    return {
        "id": cabecera["id"],
        "numero_remision": cabecera["numero_remision"],
        "registrado_en": cabecera["registrado_en"],
        "solicitud_id": cabecera["solicitud_id"],
        "solicitud_numero": cabecera["solicitud_numero"],
        "equipo_codigo": cabecera["equipo_codigo"],
        "equipo_descripcion": cabecera["equipo_descripcion"],
        "contratista": {"id": cabecera["contratista_id"], "nombre": cabecera["contratista_nombre"],
                        "documento": cabecera["contratista_documento"], "telefono": cabecera["contratista_telefono"]},
        "registrado_por": {"id": cabecera["usuario_id"], "nombre": cabecera["usuario_nombre"]},
        "repuestos": entregas_repo.buscar_repuestos_entregados(conexion, entrega_id),
        "retractada": bool(cabecera["retractada"]),
        "motivo_retraccion": cabecera["motivo_retraccion"],
    }
