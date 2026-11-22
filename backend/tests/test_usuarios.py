"""
Archivo:  backend/tests/test_usuarios.py
Proyecto: FacturApp (backend)

Qué prueba:
    Las rutas de usuarios y sus reglas. Cada prueba se deshace al final
    (ver conftest.py), así que la base de datos no cambia.
"""

import pytest

from app.core.errores import Conflicto
from app.core.seguridad import validar_contrasena, verificar_contrasena
from app.repositories import usuarios_repo
from app.repositories.tablas import Usuario
from app.services import usuarios_service
from tests.conftest import codigo_error, encabezado

NUEVO = {"nombre": "Marta Rincón", "correo": "marta.rincon@facturapp.test", "rol": "oficina"}


# ---------------------------------------------------------------- permisos

RUTAS = [
    ("get", "/api/usuarios", None),
    ("get", "/api/usuarios/2", None),
    ("post", "/api/usuarios", NUEVO),
    ("put", "/api/usuarios/3", NUEVO),
    ("patch", "/api/usuarios/3/estado", {"activo": False}),
    ("post", "/api/usuarios/3/restaurar-contrasena", None),
]


@pytest.mark.parametrize("metodo, ruta, cuerpo", RUTAS)
def test_usuario_normal_recibe_403(cliente, oficina, metodo, ruta, cuerpo):
    """La Oficina radicadora no puede usar ninguna ruta de usuarios (RN-02)."""
    respuesta = getattr(cliente, metodo)(ruta, json=cuerpo, headers=oficina) if cuerpo else \
        getattr(cliente, metodo)(ruta, headers=oficina)
    assert respuesta.status_code == 403
    assert codigo_error(respuesta) == "SIN_PERMISO"


def test_sin_token_recibe_401(cliente):
    """Sin token, la API responde 401."""
    respuesta = cliente.get("/api/usuarios")
    assert respuesta.status_code == 401
    assert codigo_error(respuesta) == "NO_AUTENTICADO"


def test_token_alterado_recibe_401(cliente):
    """Con un token falso o alterado, la API responde 401 SESION_VENCIDA."""
    respuesta = cliente.get("/api/usuarios", headers={"Authorization": "Bearer token-falso"})
    assert respuesta.status_code == 401
    assert codigo_error(respuesta) == "SESION_VENCIDA"


# ---------------------------------------------------------------- listar y ver

def test_listar_sin_contrasenas(cliente, admin):
    """El Admin ve los usuarios, y ninguna respuesta trae contrasena_hash."""
    respuesta = cliente.get("/api/usuarios", headers=admin)
    assert respuesta.status_code == 200
    correos = {u["correo"] for u in respuesta.json()}
    assert {"admin@facturapp.test", "laura.gomez@facturapp.test"} <= correos
    assert all("contrasena_hash" not in u for u in respuesta.json())


def test_ver_usuario_inexistente_404(cliente, admin):
    """Un id que no existe responde 404."""
    respuesta = cliente.get("/api/usuarios/99999", headers=admin)
    assert respuesta.status_code == 404
    assert codigo_error(respuesta) == "NO_ENCONTRADO"


# ---------------------------------------------------------------- crear

def test_crear_con_contrasena_temporal(cliente, conexion, admin):
    """Al crear, la API devuelve una contraseña temporal válida y marca debe_cambiar_contrasena."""
    respuesta = cliente.post("/api/usuarios", json=NUEVO, headers=admin)
    assert respuesta.status_code == 201
    assert respuesta.headers["Cache-Control"] == "no-store"

    cuerpo = respuesta.json()
    temporal = cuerpo["contrasena_temporal"]
    assert validar_contrasena(temporal) is None          # cumple RN-03
    assert cuerpo["usuario"]["debe_cambiar_contrasena"] is True
    assert cuerpo["usuario"]["activo"] is True

    # En la base de datos queda solo el hash, y corresponde a la temporal.
    guardado = usuarios_repo.buscar_por_correo(conexion, NUEVO["correo"])
    assert guardado.contrasena_hash != temporal
    assert verificar_contrasena(temporal, guardado.contrasena_hash)

    # La contraseña no vuelve a aparecer al consultar el usuario.
    consulta = cliente.get(f"/api/usuarios/{guardado.id}", headers=admin).json()
    assert "contrasena_temporal" not in consulta and "contrasena_hash" not in consulta


def test_crear_correo_repetido_409(cliente, admin):
    """No se puede repetir un correo, aunque cambien las mayúsculas."""
    datos = {**NUEVO, "correo": "  ADMIN@facturapp.test "}
    respuesta = cliente.post("/api/usuarios", json=datos, headers=admin)
    assert respuesta.status_code == 409
    assert codigo_error(respuesta) == "CORREO_REPETIDO"


def test_crear_datos_invalidos_422(cliente, admin):
    """Datos con forma inválida responden 422 y dicen qué campo falló."""
    respuesta = cliente.post("/api/usuarios", json={"nombre": " ", "correo": "malo", "rol": "jefe"},
                             headers=admin)
    assert respuesta.status_code == 422
    campos = respuesta.json()["error"]["campos"]
    assert set(campos) == {"nombre", "correo", "rol"}
    assert campos["correo"] == "Escriba un correo válido."


def test_json_mal_armado_400(cliente, admin):
    """Un JSON roto responde 400 PETICION_INVALIDA."""
    respuesta = cliente.post("/api/usuarios", content="{nombre:", headers={**admin, "Content-Type": "application/json"})
    assert respuesta.status_code == 400
    assert codigo_error(respuesta) == "PETICION_INVALIDA"


# ---------------------------------------------------------------- editar

def test_editar_usuario(cliente, admin):
    """El Admin cambia nombre, correo y rol de otro usuario."""
    datos = {"nombre": "Laura Gómez Ruiz", "correo": "laura.ruiz@facturapp.test", "rol": "admin"}
    respuesta = cliente.put("/api/usuarios/2", json=datos, headers=admin)
    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "Laura Gómez Ruiz"
    assert respuesta.json()["rol"] == "admin"


def test_editar_correo_de_otro_409(cliente, admin):
    """Al editar no se puede usar el correo de otro usuario."""
    datos = {**NUEVO, "correo": "andres.munoz@facturapp.test"}
    respuesta = cliente.put("/api/usuarios/2", json=datos, headers=admin)
    assert respuesta.status_code == 409
    assert codigo_error(respuesta) == "CORREO_REPETIDO"


def test_admin_no_puede_quitarse_su_rol(cliente, admin):
    """Un Admin no puede pasarse a sí mismo a Oficina radicadora."""
    datos = {"nombre": "Administrador", "correo": "admin@facturapp.test", "rol": "oficina"}
    respuesta = cliente.put("/api/usuarios/1", json=datos, headers=admin)
    assert respuesta.status_code == 409
    assert codigo_error(respuesta) == "NO_PUEDE_CAMBIAR_SU_ROL"


# ---------------------------------------------------------------- estado

def test_desactivar_y_activar(cliente, admin):
    """El Admin desactiva y vuelve a activar a otro usuario."""
    respuesta = cliente.patch("/api/usuarios/3/estado", json={"activo": False}, headers=admin)
    assert respuesta.status_code == 200 and respuesta.json()["activo"] is False
    respuesta = cliente.patch("/api/usuarios/3/estado", json={"activo": True}, headers=admin)
    assert respuesta.status_code == 200 and respuesta.json()["activo"] is True


def test_desactivado_queda_fuera_de_inmediato(cliente, admin):
    """RN-01 y PA-25: un usuario desactivado recibe 401 en su siguiente petición, aunque su token siga vigente."""
    creado = cliente.post("/api/usuarios", json={**NUEVO, "rol": "admin"}, headers=admin).json()
    admin_dos = encabezado(creado["usuario"]["id"], "admin")
    # /api/auth/yo funciona aunque tenga la contraseña temporal pendiente de cambiar.
    assert cliente.get("/api/auth/yo", headers=admin_dos).status_code == 200

    cliente.patch(f"/api/usuarios/{creado['usuario']['id']}/estado", json={"activo": False}, headers=admin)
    respuesta = cliente.get("/api/auth/yo", headers=admin_dos)
    assert respuesta.status_code == 401
    assert codigo_error(respuesta) == "USUARIO_DESACTIVADO"


def test_admin_no_puede_desactivarse(cliente, admin):
    """RN-32: un Admin no puede desactivarse a sí mismo."""
    respuesta = cliente.patch("/api/usuarios/1/estado", json={"activo": False}, headers=admin)
    assert respuesta.status_code == 409
    assert codigo_error(respuesta) == "NO_PUEDE_DESACTIVARSE"


def test_no_queda_sin_admins(conexion):
    """RN-32: el último Admin activo no se puede desactivar ni pasar a Oficina.

    Por la API no se llega a este caso (quien lo intenta también es Admin
    activo), así que se prueba el service directamente, con un Admin
    hipotético (id 9999) que actúa sobre el único Admin del sistema.
    """
    # Deja al usuario 1 como único Admin activo (se deshace al final de la prueba).
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE usuarios SET activo = 0 WHERE rol = 'admin' AND id <> 1")

    otro = Usuario(id=9999, nombre="Otro", correo="otro@x.co", contrasena_hash="", rol="admin",
                   activo=True, debe_cambiar_contrasena=False, creado_en=None)
    with pytest.raises(Conflicto) as error:
        usuarios_service.cambiar_estado(conexion, 1, False, otro)
    assert error.value.codigo == "ULTIMO_ADMIN"

    with pytest.raises(Conflicto) as error:
        usuarios_service.editar(conexion, 1, usuarios_service.UsuarioEntrada(
            nombre="Admin", correo="admin@facturapp.test", rol="oficina"), otro)
    assert error.value.codigo == "ULTIMO_ADMIN"


def test_desactivar_inexistente_404(cliente, admin):
    """Desactivar un id que no existe responde 404."""
    respuesta = cliente.patch("/api/usuarios/99999/estado", json={"activo": False}, headers=admin)
    assert respuesta.status_code == 404


# ---------------------------------------------------------------- restaurar contraseña

def test_restaurar_contrasena(cliente, conexion, admin):
    """Restaurar devuelve una temporal nueva, una sola vez, y marca que debe cambiarse."""
    respuesta = cliente.post("/api/usuarios/3/restaurar-contrasena", headers=admin)
    assert respuesta.status_code == 200
    assert respuesta.headers["Cache-Control"] == "no-store"
    temporal = respuesta.json()["contrasena_temporal"]
    assert validar_contrasena(temporal) is None

    guardado = usuarios_repo.buscar_por_id(conexion, 3)
    assert guardado.debe_cambiar_contrasena is True
    assert verificar_contrasena(temporal, guardado.contrasena_hash)


def test_restaurar_inexistente_404(cliente, admin):
    """Restaurar la contraseña de un id que no existe responde 404."""
    respuesta = cliente.post("/api/usuarios/99999/restaurar-contrasena", headers=admin)
    assert respuesta.status_code == 404


def test_no_hay_ruta_para_borrar(cliente, admin):
    """No existe DELETE: los usuarios se desactivan, no se borran (RN-05)."""
    respuesta = cliente.delete("/api/usuarios/3", headers=admin)
    assert respuesta.status_code == 405
    assert codigo_error(respuesta) == "METODO_NO_PERMITIDO"
