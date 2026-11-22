"""
Archivo:  backend/tests/test_catalogos.py
Proyecto: FacturApp (backend)

Qué prueba:
    Las reglas de categorías, repuestos, contratistas e inventario:
      - Consultar lo pueden hacer todos; crear, editar y subir el stock, solo el Admin.
      - Nada se borra: no hay rutas DELETE; se desactiva y el historial se conserva.
      - Los nombres de categoría no se repiten (sin importar mayúsculas ni tildes).
      - El stock no se escribe a mano: empieza en 0 y sube con entradas.
      - El stock es entero (en unidades) y nunca negativo; las cantidades son mayores que cero.
    Cada prueba se deshace al final (conftest.py): la base de datos no cambia.
"""

from decimal import Decimal

import pytest

from app.repositories import catalogos_repo
from tests.conftest import codigo_error

REPUESTO_NUEVO = {"codigo": "val-004", "nombre": "Válvula de servicio 1/4\"", "categoria_id": 2,
                  "unidad_medida": "unidad"}


def stock_de(cliente, admin, codigo: str) -> dict:
    """Devuelve la fila del inventario de un repuesto."""
    return next(f for f in cliente.get("/api/inventario", headers=admin).json() if f["codigo"] == codigo)


# ---------------------------------------------------------------- permisos

@pytest.mark.parametrize("ruta", ["/api/categorias", "/api/categorias/1", "/api/repuestos", "/api/repuestos/1",
                                  "/api/contratistas", "/api/contratistas/1"])
def test_todos_pueden_consultar(cliente, oficina, ruta):
    """La Oficina radicadora puede consultar los tres catálogos."""
    assert cliente.get(ruta, headers=oficina).status_code == 200


@pytest.mark.parametrize("metodo, ruta, cuerpo", [
    ("post", "/api/categorias", {"nombre": "Gas refrigerante"}),
    ("put", "/api/categorias/1", {"nombre": "Compresores"}),
    ("patch", "/api/categorias/1/estado", {"activo": False}),
    ("post", "/api/repuestos", REPUESTO_NUEVO),
    ("put", "/api/repuestos/1", REPUESTO_NUEVO),
    ("patch", "/api/repuestos/1/estado", {"activo": False}),
    ("post", "/api/contratistas", {"documento": "123", "nombre": "X"}),
    ("put", "/api/contratistas/1", {"documento": "123", "nombre": "X"}),
    ("patch", "/api/contratistas/1/estado", {"activo": False}),
    ("post", "/api/inventario/entradas", {"repuesto_id": 1, "cantidad": 5}),
])
def test_solo_admin_modifica(cliente, oficina, metodo, ruta, cuerpo):
    """Crear, editar, desactivar y subir el stock: la Oficina recibe 403."""
    respuesta = getattr(cliente, metodo)(ruta, json=cuerpo, headers=oficina)
    assert respuesta.status_code == 403
    assert codigo_error(respuesta) == "SIN_PERMISO"


@pytest.mark.parametrize("ruta", ["/api/inventario", "/api/inventario/entradas"])
def test_oficina_no_ve_el_stock(cliente, oficina, ruta):
    """RN-02: la Oficina radicadora no consulta el inventario."""
    assert cliente.get(ruta, headers=oficina).status_code == 403


def test_catalogo_de_repuestos_sin_stock(cliente, oficina):
    """El catálogo de repuestos que ven todos no trae datos de stock."""
    repuesto = cliente.get("/api/repuestos/1", headers=oficina).json()
    assert not any(clave.startswith("stock") for clave in repuesto)


# ---------------------------------------------------------------- nada se borra

@pytest.mark.parametrize("ruta", ["/api/categorias/1", "/api/repuestos/1", "/api/contratistas/1"])
def test_no_hay_ruta_para_borrar(cliente, admin, ruta):
    """RN-05: no existe DELETE en los catálogos."""
    respuesta = cliente.delete(ruta, headers=admin)
    assert respuesta.status_code == 405


def test_repuesto_con_historial_se_desactiva(cliente, conexion, admin):
    """COM-001 ya tiene entregas: se desactiva, sigue existiendo y sale de la lista de activos."""
    respuesta = cliente.patch("/api/repuestos/1/estado", json={"activo": False}, headers=admin)
    assert respuesta.status_code == 200 and respuesta.json()["activo"] is False
    assert catalogos_repo.buscar_repuesto(conexion, 1) is not None
    activos = {r["codigo"] for r in cliente.get("/api/repuestos?activo=true", headers=admin).json()}
    assert "COM-001" not in activos


def test_contratista_con_historial_se_desactiva(cliente, admin):
    """Un contratista con entregas se desactiva; no se borra."""
    respuesta = cliente.patch("/api/contratistas/1/estado", json={"activo": False}, headers=admin)
    assert respuesta.status_code == 200 and respuesta.json()["activo"] is False


# ---------------------------------------------------------------- categorías

def test_crear_categoria(cliente, admin):
    """El Admin crea una categoría activa."""
    respuesta = cliente.post("/api/categorias", json={"nombre": "  Gas refrigerante "}, headers=admin)
    assert respuesta.status_code == 201
    assert respuesta.json()["nombre"] == "Gas refrigerante"   # sin espacios en los extremos


@pytest.mark.parametrize("nombre", ["Válvulas", "valvulas", "  VÁLVULAS  "])
def test_nombre_de_categoria_no_se_repite(cliente, admin, nombre):
    """RN-07: el nombre no se repite, sin importar mayúsculas, tildes ni espacios."""
    respuesta = cliente.post("/api/categorias", json={"nombre": nombre}, headers=admin)
    assert respuesta.status_code == 409
    assert codigo_error(respuesta) == "NOMBRE_REPETIDO"


def test_editar_categoria_a_nombre_existente(cliente, admin):
    """Al editar tampoco se puede usar el nombre de otra categoría."""
    respuesta = cliente.put("/api/categorias/1", json={"nombre": "válvulas"}, headers=admin)
    assert respuesta.status_code == 409


def test_categoria_con_repuestos_activos_no_se_desactiva(cliente, admin):
    """RN-06: no se desactiva una categoría que tiene repuestos activos."""
    respuesta = cliente.patch("/api/categorias/1/estado", json={"activo": False}, headers=admin)
    assert respuesta.status_code == 409
    assert codigo_error(respuesta) == "CATEGORIA_CON_REPUESTOS"


def test_categoria_sin_repuestos_se_desactiva(cliente, admin):
    """Una categoría sin repuestos activos sí se puede desactivar."""
    nueva = cliente.post("/api/categorias", json={"nombre": "Gas refrigerante"}, headers=admin).json()
    respuesta = cliente.patch(f"/api/categorias/{nueva['id']}/estado", json={"activo": False}, headers=admin)
    assert respuesta.status_code == 200 and respuesta.json()["activo"] is False


def test_categoria_nombre_vacio_422(cliente, admin):
    """Un nombre vacío o solo con espacios no es válido."""
    respuesta = cliente.post("/api/categorias", json={"nombre": "   "}, headers=admin)
    assert respuesta.status_code == 422
    assert "nombre" in respuesta.json()["error"]["campos"]


# ---------------------------------------------------------------- repuestos

def test_crear_repuesto_empieza_en_cero(cliente, admin):
    """El repuesto nuevo empieza con stock 0, y su código se guarda en mayúsculas."""
    respuesta = cliente.post("/api/repuestos", json=REPUESTO_NUEVO, headers=admin)
    assert respuesta.status_code == 201
    assert respuesta.json()["codigo"] == "VAL-004"
    fila = stock_de(cliente, admin, "VAL-004")
    assert fila["stock_almacen"] == 0 and fila["disponible"] == 0


def test_stock_no_se_escribe_a_mano(cliente, admin):
    """RN-09: si se envía stock al crear o editar, se ignora."""
    cuerpo = {**REPUESTO_NUEVO, "stock_almacen": 500}
    cliente.post("/api/repuestos", json=cuerpo, headers=admin)
    assert stock_de(cliente, admin, "VAL-004")["stock_almacen"] == 0

    cliente.put("/api/repuestos/1", json={"codigo": "COM-001", "nombre": "Compresor hermético 1/2 HP R134a",
                                          "categoria_id": 1, "unidad_medida": "unidad", "stock_almacen": 500},
                headers=admin)
    assert stock_de(cliente, admin, "COM-001")["stock_almacen"] == 9


@pytest.mark.parametrize("campo, valor, codigo", [
    ("codigo", "COM-001", "CODIGO_REPETIDO"),
    ("nombre", "compresor hermético 1/2 hp r134a", "NOMBRE_REPETIDO"),
])
def test_repuesto_codigo_o_nombre_repetido(cliente, admin, campo, valor, codigo):
    """RN-07: código y nombre del repuesto no se repiten."""
    respuesta = cliente.post("/api/repuestos", json={**REPUESTO_NUEVO, campo: valor}, headers=admin)
    assert respuesta.status_code == 409
    assert codigo_error(respuesta) == codigo


def test_repuesto_codigo_con_caracteres_raros_422(cliente, admin):
    """RN-25: el código solo acepta letras sin tildes, números y guiones."""
    respuesta = cliente.post("/api/repuestos", json={**REPUESTO_NUEVO, "codigo": "VÁL 004"}, headers=admin)
    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["campos"]["codigo"].startswith("El código solo puede")


def test_repuesto_con_categoria_inexistente(cliente, admin):
    """La categoría del repuesto debe existir y estar activa."""
    respuesta = cliente.post("/api/repuestos", json={**REPUESTO_NUEVO, "categoria_id": 999}, headers=admin)
    assert respuesta.status_code == 409
    assert codigo_error(respuesta) == "CATEGORIA_NO_DISPONIBLE"


# ---------------------------------------------------------------- contratistas

def test_documento_repetido_sin_puntos(cliente, admin):
    """RN-08: "9004567891" es el mismo documento que "900.456.789-1"."""
    respuesta = cliente.post("/api/contratistas", json={"documento": "9004567891", "nombre": "Otro"}, headers=admin)
    assert respuesta.status_code == 409
    assert codigo_error(respuesta) == "DOCUMENTO_REPETIDO"


def test_contratistas_homonimos(cliente, admin):
    """El nombre sí puede repetirse si el documento es distinto."""
    respuesta = cliente.post("/api/contratistas", json={"documento": "79.555.123", "nombre": "Carlos Pérez Rincón"},
                             headers=admin)
    assert respuesta.status_code == 201


def test_documento_con_letras_422(cliente, admin):
    """RN-25: la cédula o NIT solo acepta números, puntos y guiones."""
    respuesta = cliente.post("/api/contratistas", json={"documento": "CC 123", "nombre": "X"}, headers=admin)
    assert respuesta.status_code == 422


# ---------------------------------------------------------------- stock

def test_entrada_sube_el_stock_y_deja_movimiento(cliente, conexion, admin):
    """Una entrada de 5 sube el stock de COM-001 de 9 a 14 y deja su movimiento."""
    respuesta = cliente.post("/api/inventario/entradas", json={"repuesto_id": 1, "cantidad": 5,
                                                               "observacion": "Factura 1001"}, headers=admin)
    assert respuesta.status_code == 201
    assert respuesta.json()["stock_almacen"] == 14
    with conexion.cursor() as cursor:
        cursor.execute("SELECT tipo, cantidad, stock_resultante FROM movimientos_inventario "
                       "WHERE repuesto_id = 1 ORDER BY id DESC LIMIT 1")
        movimiento = cursor.fetchone()
    assert movimiento == {"tipo": "entrada", "cantidad": Decimal("5.00"), "stock_resultante": Decimal("14.00")}


@pytest.mark.parametrize("cantidad", [0, -3])
def test_cantidad_debe_ser_mayor_que_cero(cliente, admin, cantidad):
    """RN-11: la cantidad de una entrada debe ser mayor que cero."""
    respuesta = cliente.post("/api/inventario/entradas", json={"repuesto_id": 1, "cantidad": cantidad}, headers=admin)
    assert respuesta.status_code == 422


def test_stock_en_unidades_es_entero(cliente, admin):
    """El stock de un repuesto en unidades es entero: 2,5 se rechaza (RN-12)."""
    respuesta = cliente.post("/api/inventario/entradas", json={"repuesto_id": 1, "cantidad": 2.5}, headers=admin)
    assert respuesta.status_code == 422
    assert codigo_error(respuesta) == "CANTIDAD_INVALIDA"
    assert stock_de(cliente, admin, "COM-001")["stock_almacen"] == 9


def test_stock_nunca_negativo_en_la_base(conexion):
    """RN-10: aunque el código fallara, la base de datos rechaza un stock negativo."""
    import pymysql
    with pytest.raises(pymysql.err.OperationalError):
        with conexion.cursor() as cursor:
            cursor.execute("UPDATE repuestos SET stock_almacen = -1 WHERE id = 1")


def test_entrada_a_repuesto_inactivo(cliente, admin):
    """No se registran entradas de un repuesto desactivado."""
    cliente.patch("/api/repuestos/1/estado", json={"activo": False}, headers=admin)
    respuesta = cliente.post("/api/inventario/entradas", json={"repuesto_id": 1, "cantidad": 5}, headers=admin)
    assert respuesta.status_code == 409
    assert codigo_error(respuesta) == "REPUESTO_INACTIVO"


def test_entrada_aparta_para_solicitudes_en_espera(cliente, conexion, admin):
    """RN-33: la mercancía nueva se aparta para la solicitud abierta que la esperaba.

    Se arma una solicitud que pidió 10 COM-002 y solo tiene 6 apartados (4 en espera).
    Una entrada de 3 aparta las 3 para esa solicitud.
    """
    with conexion.cursor() as cursor:
        cursor.execute("INSERT INTO solicitudes (numero, equipo_id, contratista_id, fecha_entrega, creado_por) "
                       "VALUES ('SOL-PRUEBA', 3, 3, CURDATE(), 2)")
        solicitud_id = cursor.lastrowid
        cursor.execute("INSERT INTO detalle_solicitud (solicitud_id, repuesto_id, cantidad_solicitada, cantidad_apartada) "
                       "VALUES (%s, 2, 10, 6)", (solicitud_id,))
        cursor.execute("UPDATE repuestos SET stock_apartado = 6 WHERE id = 2")

    assert stock_de(cliente, admin, "COM-002")["en_espera"] == 4
    respuesta = cliente.post("/api/inventario/entradas", json={"repuesto_id": 2, "cantidad": 3}, headers=admin)
    assert respuesta.json()["apartado_para_solicitudes"] == 3
    fila = stock_de(cliente, admin, "COM-002")
    assert (fila["stock_almacen"], fila["stock_apartado"], fila["disponible"], fila["en_espera"]) == (9, 9, 0, 1)
