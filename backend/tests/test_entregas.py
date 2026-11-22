"""
Archivo:  backend/tests/test_entregas.py
Proyecto: FacturApp (backend)

Qué prueba:
    Las entregas (HU-21) y las remisiones (HU-24):
      - Una entrega correcta baja el stock, genera la remisión con número
        consecutivo y pone sola la fecha y el usuario.
      - Si un repuesto no alcanza, NO se guarda nada (todo o nada) y la
        respuesta dice qué repuesto falta. Se comprueba comparando la base
        de datos antes y después.
      - Las demás reglas: permisos, solicitud cerrada, más de lo
        pendiente, unidades enteras, datos inválidos.
    Datos de ejemplo (seed.sql): SOL-000002 (abierta) pidió 3 MOT-001,
    entregó 1 y tiene 2 apartados; MOT-001 tiene 14 en almacén.
    Cada prueba se deshace al final (conftest.py).
"""

from datetime import datetime, timedelta

import pytest

from tests.conftest import codigo_error

ENTREGA_MOTORES = {"repuestos": [{"repuesto_id": 5, "cantidad": 2}]}


def foto_de_la_base(conexion) -> dict:
    """Toma una "foto" de todo lo que una entrega podría cambiar, para comparar antes y después."""
    consultas = {
        "repuestos": "SELECT id, stock_almacen, stock_apartado FROM repuestos ORDER BY id",
        "detalle_solicitud": "SELECT id, cantidad_apartada, cantidad_entregada FROM detalle_solicitud ORDER BY id",
        "entregas": "SELECT COUNT(*) AS n FROM entregas",
        "detalle_entrega": "SELECT COUNT(*) AS n FROM detalle_entrega",
        "movimientos": "SELECT COUNT(*) AS n FROM movimientos_inventario",
        "historial": "SELECT COUNT(*) AS n FROM historial_solicitud",
        "consecutivo_rem": "SELECT ultimo_numero FROM consecutivos WHERE tipo = 'REM'",
    }
    foto = {}
    with conexion.cursor() as cursor:
        for nombre, sql in consultas.items():
            cursor.execute(sql)
            foto[nombre] = cursor.fetchall()
    return foto


@pytest.fixture
def solicitud_sin_stock(conexion) -> int:
    """Arma una solicitud abierta para probar la falta de stock:
         - VAL-001: pidió 2, nada apartado, y hay 23 libres  -> sí alcanza.
         - COM-002: pidió 10, 6 apartados y 0 libres        -> alcanzan solo 6.
    """
    with conexion.cursor() as cursor:
        cursor.execute("INSERT INTO solicitudes (numero, equipo_id, contratista_id, fecha_entrega, creado_por) "
                       "VALUES ('SOL-PRUEBA', 3, 3, CURDATE(), 2)")
        solicitud_id = cursor.lastrowid
        cursor.execute("INSERT INTO detalle_solicitud (solicitud_id, repuesto_id, cantidad_solicitada) "
                       "VALUES (%s, 3, 2)", (solicitud_id,))
        cursor.execute("INSERT INTO detalle_solicitud (solicitud_id, repuesto_id, cantidad_solicitada, "
                       "cantidad_apartada) VALUES (%s, 2, 10, 6)", (solicitud_id,))
        cursor.execute("UPDATE repuestos SET stock_apartado = 6 WHERE id = 2")
    return solicitud_id


# ---------------------------------------------------------------- entrega correcta

def test_entrega_correcta(cliente, conexion, admin):
    """Entregar los 2 motores pendientes de SOL-000002: stock, remisión, fecha y usuario."""
    antes = datetime.now() - timedelta(minutes=1)
    respuesta = cliente.post("/api/solicitudes/2/entregas", json=ENTREGA_MOTORES, headers=admin)
    assert respuesta.status_code == 201

    remision = respuesta.json()
    assert remision["numero_remision"] == "REM-000003"          # siguiente después de REM-000002
    assert remision["registrado_por"] == {"id": 1, "nombre": "Administrador del sistema",
                                          "documento": None, "telefono": None}
    assert datetime.fromisoformat(remision["registrado_en"]) >= antes  # la fecha la puso el sistema
    assert remision["contratista"]["nombre"] == "Carlos Pérez Rincón"  # sale de la solicitud
    assert remision["repuestos"] == [{"repuesto_id": 5, "codigo": "MOT-001",
                                      "nombre": "Motor ventilador condensador 9 W",
                                      "unidad_medida": "unidad", "cantidad": 2.0}]
    assert remision["estado_entrega"] == "Completa"

    with conexion.cursor() as cursor:
        cursor.execute("SELECT stock_almacen, stock_apartado FROM repuestos WHERE id = 5")
        assert cursor.fetchone() == {"stock_almacen": 12, "stock_apartado": 0}
        cursor.execute("SELECT cantidad_entregada, cantidad_apartada FROM detalle_solicitud WHERE id = 4")
        assert cursor.fetchone() == {"cantidad_entregada": 3, "cantidad_apartada": 0}
        cursor.execute("SELECT tipo, cantidad, stock_resultante FROM movimientos_inventario ORDER BY id DESC LIMIT 1")
        assert cursor.fetchone() == {"tipo": "entrega", "cantidad": -2, "stock_resultante": 12}
        cursor.execute("SELECT accion, detalle FROM historial_solicitud ORDER BY id DESC LIMIT 1")
        assert cursor.fetchone() == {"accion": "entrega", "detalle": "Remisión REM-000003: entrega completa"}


def test_numero_de_remision_consecutivo(cliente, admin, solicitud_sin_stock):
    """Dos entregas seguidas reciben REM-000003 y REM-000004."""
    primera = cliente.post("/api/solicitudes/2/entregas", json=ENTREGA_MOTORES, headers=admin)
    segunda = cliente.post(f"/api/solicitudes/{solicitud_sin_stock}/entregas",
                           json={"repuestos": [{"repuesto_id": 3, "cantidad": 1}]}, headers=admin)
    assert primera.json()["numero_remision"] == "REM-000003"
    assert segunda.json()["numero_remision"] == "REM-000004"
    assert segunda.json()["estado_entrega"] == "Parcial"


def test_entrega_parcial_usa_stock_libre(cliente, admin, solicitud_sin_stock):
    """Si no hay nada apartado pero sí stock libre, se entrega del stock libre (VAL-001)."""
    respuesta = cliente.post(f"/api/solicitudes/{solicitud_sin_stock}/entregas",
                             json={"repuestos": [{"repuesto_id": 3, "cantidad": 2}]}, headers=admin)
    assert respuesta.status_code == 201
    assert respuesta.json()["estado_entrega"] == "Parcial"   # COM-002 sigue pendiente


# ---------------------------------------------------------------- todo o nada

def test_stock_insuficiente_no_guarda_nada(cliente, conexion, admin, solicitud_sin_stock):
    """Si COM-002 no alcanza, tampoco se entrega VAL-001: la base queda exactamente igual."""
    antes = foto_de_la_base(conexion)

    respuesta = cliente.post(f"/api/solicitudes/{solicitud_sin_stock}/entregas", json={"repuestos": [
        {"repuesto_id": 3, "cantidad": 2},    # VAL-001: sí alcanza
        {"repuesto_id": 2, "cantidad": 8},    # COM-002: solo hay 6
    ]}, headers=admin)

    assert respuesta.status_code == 409
    error = respuesta.json()["error"]
    assert error["codigo"] == "STOCK_INSUFICIENTE"
    assert error["mensaje"] == "No hay stock suficiente de COM-002 Compresor hermético 1/3 HP R600a. Disponible: 6."
    assert list(error["campos"]) == ["repuestos.1.cantidad"]   # dice exactamente qué repuesto falta

    assert foto_de_la_base(conexion) == antes                  # nada cambió


def test_dos_repuestos_sin_stock_se_informan_los_dos(cliente, conexion, admin, solicitud_sin_stock):
    """Si faltan varios repuestos, la respuesta los nombra todos, y tampoco se guarda nada."""
    with conexion.cursor() as cursor:  # la misma solicitud también pide 20 VAL-002; solo hay 10
        cursor.execute("INSERT INTO detalle_solicitud (solicitud_id, repuesto_id, cantidad_solicitada) "
                       "VALUES (%s, 4, 20)", (solicitud_sin_stock,))
    antes = foto_de_la_base(conexion)

    respuesta = cliente.post(f"/api/solicitudes/{solicitud_sin_stock}/entregas", json={"repuestos": [
        {"repuesto_id": 2, "cantidad": 8},     # COM-002: hay 6
        {"repuesto_id": 4, "cantidad": 15},    # VAL-002: hay 10
    ]}, headers=admin)

    assert respuesta.status_code == 409
    campos = respuesta.json()["error"]["campos"]
    assert campos == {
        "repuestos.0.cantidad": "No hay stock suficiente de COM-002 Compresor hermético 1/3 HP R600a. Disponible: 6.",
        "repuestos.1.cantidad": "No hay stock suficiente de VAL-002 Válvula solenoide 1/4\". Disponible: 10.",
    }
    assert foto_de_la_base(conexion) == antes


def test_mas_de_lo_pendiente_en_otro_repuesto(cliente, admin):
    """VAL-002 ya se entregó completo en SOL-000002: entregar otro más se rechaza."""
    respuesta = cliente.post("/api/solicitudes/2/entregas", json={"repuestos": [
        {"repuesto_id": 5, "cantidad": 2}, {"repuesto_id": 4, "cantidad": 1}]}, headers=admin)
    assert respuesta.status_code == 409
    assert codigo_error(respuesta) == "MAS_DE_LO_PENDIENTE"


# ---------------------------------------------------------------- otras reglas

def test_usuario_normal_no_registra_entregas(cliente, oficina):
    """RN-02: solo el Admin registra entregas."""
    respuesta = cliente.post("/api/solicitudes/2/entregas", json=ENTREGA_MOTORES, headers=oficina)
    assert respuesta.status_code == 403
    assert codigo_error(respuesta) == "SIN_PERMISO"


def test_mas_de_lo_pendiente(cliente, admin):
    """RN-16: de MOT-001 faltan 2; entregar 3 se rechaza."""
    respuesta = cliente.post("/api/solicitudes/2/entregas",
                             json={"repuestos": [{"repuesto_id": 5, "cantidad": 3}]}, headers=admin)
    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["mensaje"] == "No puede entregar más de lo pendiente. Pendiente de MOT-001: 2."


def test_solicitud_cerrada(cliente, admin):
    """RN-22: SOL-000001 está en "reparado": no acepta entregas."""
    respuesta = cliente.post("/api/solicitudes/1/entregas",
                             json={"repuestos": [{"repuesto_id": 1, "cantidad": 1}]}, headers=admin)
    assert respuesta.status_code == 409
    assert codigo_error(respuesta) == "SOLICITUD_CERRADA"


def test_solicitud_inexistente(cliente, admin):
    """Una solicitud que no existe responde 404."""
    respuesta = cliente.post("/api/solicitudes/999/entregas", json=ENTREGA_MOTORES, headers=admin)
    assert respuesta.status_code == 404


def test_repuesto_que_no_esta_en_la_solicitud(cliente, admin):
    """Solo se entregan repuestos de la solicitud."""
    respuesta = cliente.post("/api/solicitudes/2/entregas",
                             json={"repuestos": [{"repuesto_id": 6, "cantidad": 1}]}, headers=admin)
    assert respuesta.status_code == 409
    assert codigo_error(respuesta) == "REPUESTO_NO_SOLICITADO"


def test_contratista_desactivado(cliente, admin):
    """RN-31: si el contratista de la solicitud fue desactivado, no se entrega."""
    cliente.patch("/api/contratistas/2/estado", json={"activo": False}, headers=admin)
    respuesta = cliente.post("/api/solicitudes/2/entregas", json=ENTREGA_MOTORES, headers=admin)
    assert respuesta.status_code == 409
    assert codigo_error(respuesta) == "CONTRATISTA_INACTIVO"


def test_cantidad_con_decimales_en_unidades(cliente, admin):
    """RN-12: MOT-001 se cuenta en unidades; 1,5 se rechaza."""
    respuesta = cliente.post("/api/solicitudes/2/entregas",
                             json={"repuestos": [{"repuesto_id": 5, "cantidad": 1.5}]}, headers=admin)
    assert respuesta.status_code == 422
    assert codigo_error(respuesta) == "CANTIDAD_INVALIDA"


@pytest.mark.parametrize("cuerpo", [
    {"repuestos": []},                                                             # sin repuestos
    {"repuestos": [{"repuesto_id": 5, "cantidad": 0}]},                            # cantidad 0
    {"repuestos": [{"repuesto_id": 5, "cantidad": 1}, {"repuesto_id": 5, "cantidad": 1}]},  # repetido
])
def test_datos_invalidos_422(cliente, admin, cuerpo):
    """Sin repuestos, cantidad 0 o un repuesto repetido: 422."""
    respuesta = cliente.post("/api/solicitudes/2/entregas", json=cuerpo, headers=admin)
    assert respuesta.status_code == 422
    assert codigo_error(respuesta) == "DATOS_INVALIDOS"


# ---------------------------------------------------------------- listar y ver la remisión

def test_listar_entregas(cliente, oficina):
    """Todos pueden listar las entregas, de la más reciente a la más antigua."""
    respuesta = cliente.get("/api/entregas", headers=oficina)
    assert respuesta.status_code == 200
    assert [e["numero_remision"] for e in respuesta.json()][:2] == ["REM-000002", "REM-000001"]


def test_ver_remision_para_imprimir(cliente, oficina):
    """La remisión trae contratista con documento, usuario que la registró y repuestos."""
    for ruta in ("/api/entregas/1", "/api/entregas/1/remision"):
        remision = cliente.get(ruta, headers=oficina).json()
        assert remision["numero_remision"] == "REM-000001"
        assert remision["contratista"]["nombre"] == "Refrigeración Andina S.A.S."
        assert remision["contratista"]["documento"] == "900.456.789-1"
        assert remision["registrado_por"]["nombre"] == "Administrador del sistema"
        assert remision["equipo_codigo"] == "NEV-0001"
        assert [(r["codigo"], r["cantidad"]) for r in remision["repuestos"]] == [("COM-001", 1.0), ("VAL-001", 2.0)]


def test_remision_inexistente(cliente, admin):
    """Una entrega que no existe responde 404."""
    assert cliente.get("/api/entregas/999", headers=admin).status_code == 404


def test_no_se_edita_ni_borra_una_remision(cliente, admin):
    """RN-19: no hay rutas para editar ni borrar una entrega."""
    assert cliente.put("/api/entregas/1", json={}, headers=admin).status_code == 405
    assert cliente.delete("/api/entregas/1", headers=admin).status_code == 405
