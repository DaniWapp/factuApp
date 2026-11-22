"""
Archivo:  backend/tests/test_auth.py
Proyecto: FacturApp (backend)

Qué prueba:
    Los criterios de aceptación del grupo Acceso (entregables/02-requisitos.md),
    sobre la base de PRUEBAS facturapp_pruebas:
      HU-01 Iniciar sesión        criterios 1 a 4
      HU-02 Cerrar sesión         criterio 3 (sesión vencida); 1 y 2 los hace Flask
      HU-03 Opciones del rol      criterios 1 a 3 (rol en /yo y 403 en rutas de Admin)
      HU-04 Cambiar contraseña    criterios 1 a 4
      HU-05 Contraseña temporal   criterios 1 a 4
      HU-06 Vista de Oficina      la maneja Flask; aquí no aplica.

    Los usuarios de seed.sql tienen un hash de ejemplo; cada prueba les
    pone una contraseña conocida dentro de su transacción (se deshace).
"""

import pytest

from app.core import seguridad
from app.core.config import obtener_configuracion
from app.repositories import usuarios_repo
from tests.conftest import codigo_error, encabezado

CLAVE = "Frio2026valv"
ADMIN = "admin@facturapp.test"
LAURA = "laura.gomez@facturapp.test"


@pytest.fixture
def claves(conexion):
    """Pone la contraseña CLAVE al Admin (1) y a Laura (2), solo dentro de esta prueba."""
    for usuario_id in (1, 2):
        usuarios_repo.cambiar_contrasena(conexion, usuario_id, seguridad.cifrar_contrasena(CLAVE), temporal=False)


def iniciar(cliente, correo, contrasena):
    """Llama a POST /api/auth/login."""
    return cliente.post("/api/auth/login", json={"correo": correo, "contrasena": contrasena})


def test_usa_la_base_de_pruebas():
    """Seguridad de las pruebas: nunca se usa la base real."""
    assert obtener_configuracion().db_name == "facturapp_pruebas"


# ---------------------------------------------------------------- HU-01 Iniciar sesión

def test_hu01_c1_login_correcto(cliente, claves):
    """C1: con datos correctos entra, recibe el token y su rol."""
    respuesta = iniciar(cliente, ADMIN, CLAVE)
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["tipo"] == "bearer"
    assert cuerpo["debe_cambiar_contrasena"] is False
    assert cuerpo["usuario"]["rol"] == "admin"
    datos = seguridad.leer_token(cuerpo["token"])
    assert datos["sub"] == "1" and datos["exp"] - datos["iat"] == 120 * 60   # dura 120 minutos


def test_hu01_c1_correo_sin_importar_mayusculas(cliente, claves):
    """El correo se acepta con mayúsculas o espacios en los extremos."""
    assert iniciar(cliente, "  Admin@FacturApp.test ", CLAVE).status_code == 200


@pytest.mark.parametrize("correo, contrasena", [(ADMIN, "Otra1234x"), ("nadie@facturapp.test", CLAVE)])
def test_hu01_c2_datos_incorrectos(cliente, claves, correo, contrasena):
    """C2: contraseña incorrecta o correo inexistente: el MISMO mensaje (no revela qué correos existen)."""
    respuesta = iniciar(cliente, correo, contrasena)
    assert respuesta.status_code == 401
    assert respuesta.json()["error"] == {"codigo": "CREDENCIALES_INVALIDAS",
                                         "mensaje": "Correo o contraseña incorrectos.", "campos": None}


def test_hu01_c3_usuario_desactivado(cliente, conexion, claves):
    """C3: con datos correctos, pero desactivado, no entra y ve el mensaje de HU-01."""
    usuarios_repo.cambiar_estado(conexion, 2, False)
    respuesta = iniciar(cliente, LAURA, CLAVE)
    assert respuesta.status_code == 401
    assert respuesta.json()["error"]["mensaje"] == "Su usuario está desactivado. Comuníquese con el administrador."


@pytest.mark.parametrize("correo, contrasena", [("", CLAVE), (ADMIN, ""), ("   ", "")])
def test_hu01_c4_campos_vacios(cliente, correo, contrasena):
    """C4: correo o contraseña vacíos: "Escriba su correo y su contraseña."."""
    respuesta = iniciar(cliente, correo, contrasena)
    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["mensaje"] == "Escriba su correo y su contraseña."


# ---------------------------------------------------------------- HU-02 Sesión vencida

def test_hu02_c3_sesion_vencida(cliente, monkeypatch):
    """C3: con un token vencido, la API responde "Su sesión expiró. Inicie sesión de nuevo."."""
    monkeypatch.setattr(obtener_configuracion(), "jwt_minutos_vigencia", -1)
    vencido = {"Authorization": f"Bearer {seguridad.crear_token(1, 'admin')}"}
    respuesta = cliente.get("/api/auth/yo", headers=vencido)
    assert respuesta.status_code == 401
    assert respuesta.json()["error"]["mensaje"] == "Su sesión expiró. Inicie sesión de nuevo."


def test_hu02_sin_token(cliente):
    """Sin token (por ejemplo, después de cerrar sesión en Flask), la API responde 401."""
    respuesta = cliente.get("/api/auth/yo")
    assert respuesta.status_code == 401
    assert codigo_error(respuesta) == "NO_AUTENTICADO"


# ---------------------------------------------------------------- HU-03 Opciones del rol

@pytest.mark.parametrize("usuario_id, rol", [(1, "admin"), (2, "oficina")])
def test_hu03_yo_devuelve_el_rol(cliente, usuario_id, rol):
    """C1 y C3: /api/auth/yo dice el rol, para que Flask arme el menú."""
    respuesta = cliente.get("/api/auth/yo", headers=encabezado(usuario_id, rol))
    assert respuesta.status_code == 200
    assert respuesta.json()["rol"] == rol
    assert "contrasena_hash" not in respuesta.json()


@pytest.mark.parametrize("ruta", ["/api/usuarios", "/api/inventario"])
def test_hu03_c2_oficina_en_ruta_de_admin(cliente, oficina, ruta):
    """C2: la Oficina que intenta una página del Admin recibe 403 "No tiene permiso..."."""
    respuesta = cliente.get(ruta, headers=oficina)
    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["mensaje"] == "No tiene permiso para hacer esta acción."


def test_usuario_desactivado_con_token_vigente(cliente, conexion):
    """RN-01: si lo desactivan, su token sigue vigente pero la API ya no lo deja pasar."""
    usuarios_repo.cambiar_estado(conexion, 2, False)
    respuesta = cliente.get("/api/auth/yo", headers=encabezado(2, "oficina"))
    assert respuesta.status_code == 401
    assert codigo_error(respuesta) == "USUARIO_DESACTIVADO"


# ---------------------------------------------------------------- HU-04 Cambiar mi contraseña

def cambiar(cliente, headers, actual, nueva, confirmacion=None):
    """Llama a POST /api/auth/contrasena."""
    return cliente.post("/api/auth/contrasena", headers=headers, json={
        "actual": actual, "nueva": nueva, "confirmacion": nueva if confirmacion is None else confirmacion})


def test_hu04_c1_cambio_correcto(cliente, claves, oficina):
    """C1: con la actual correcta y una nueva válida, cambia y responde "Contraseña actualizada."."""
    respuesta = cambiar(cliente, oficina, CLAVE, "NuevaClave2027")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"mensaje": "Contraseña actualizada."}
    assert iniciar(cliente, LAURA, "NuevaClave2027").status_code == 200   # entra con la nueva
    assert iniciar(cliente, LAURA, CLAVE).status_code == 401              # ya no con la anterior


def test_hu04_c2_actual_incorrecta(cliente, claves, oficina):
    """C2: si la actual está mal, no cambia y dice "La contraseña actual no es correcta."."""
    respuesta = cambiar(cliente, oficina, "Equivocada1", "NuevaClave2027")
    assert respuesta.status_code == 409
    assert respuesta.json()["error"]["mensaje"] == "La contraseña actual no es correcta."


def test_hu04_c3_confirmacion_distinta(cliente, claves, oficina):
    """C3: si la confirmación no coincide: "Las contraseñas nuevas no coinciden."."""
    respuesta = cambiar(cliente, oficina, CLAVE, "NuevaClave2027", "NuevaClave2028")
    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["mensaje"] == "Las contraseñas nuevas no coinciden."


@pytest.mark.parametrize("nueva, mensaje", [
    ("Corta1", "La contraseña debe tener al menos 8 caracteres."),
    ("SoloLetrasAqui", "La contraseña debe tener letras y números."),
])
def test_hu04_c4_regla_de_contrasena(cliente, claves, oficina, nueva, mensaje):
    """C4 (RN-03): mínimo 8 caracteres, con letras y números."""
    respuesta = cambiar(cliente, oficina, CLAVE, nueva)
    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["mensaje"] == mensaje


def test_hu04_nueva_igual_a_la_actual(cliente, claves, oficina):
    """La nueva debe ser diferente a la actual."""
    respuesta = cambiar(cliente, oficina, CLAVE, CLAVE)
    assert respuesta.status_code == 422
    assert codigo_error(respuesta) == "CONTRASENA_REPETIDA"


# ---------------------------------------------------------------- HU-05 Contraseña temporal

@pytest.fixture
def temporal(cliente, admin):
    """El Admin restaura la contraseña de Laura: devuelve la temporal."""
    return cliente.post("/api/usuarios/2/restaurar-contrasena", headers=admin).json()["contrasena_temporal"]


def test_hu05_c1_login_avisa_cambio(cliente, temporal):
    """C1: al entrar con la temporal, el login avisa que debe cambiarla."""
    respuesta = iniciar(cliente, LAURA, temporal)
    assert respuesta.status_code == 200
    assert respuesta.json()["debe_cambiar_contrasena"] is True


def test_hu05_c2_no_puede_usar_otras_rutas(cliente, temporal):
    """C2: mientras no la cambie, cualquier otra ruta responde 403 con el mensaje de HU-05."""
    token = iniciar(cliente, LAURA, temporal).json()["token"]
    respuesta = cliente.get("/api/repuestos", headers={"Authorization": f"Bearer {token}"})
    assert respuesta.status_code == 403
    assert respuesta.json()["error"] == {"codigo": "CAMBIO_CONTRASENA_REQUERIDO", "campos": None,
                                         "mensaje": "Debe cambiar su contraseña temporal antes de continuar."}
    # Sí puede ver sus datos, para que Flask sepa a dónde llevarla.
    assert cliente.get("/api/auth/yo", headers={"Authorization": f"Bearer {token}"}).status_code == 200


def test_hu05_c3_nueva_igual_a_la_temporal(cliente, temporal):
    """C3: no puede repetir la temporal: "La contraseña nueva debe ser diferente a la temporal."."""
    headers = {"Authorization": f"Bearer {iniciar(cliente, LAURA, temporal).json()['token']}"}
    respuesta = cambiar(cliente, headers, temporal, temporal)
    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["mensaje"] == "La contraseña nueva debe ser diferente a la temporal."


def test_hu05_c4_cambio_y_acceso_normal(cliente, temporal):
    """C4: al cambiarla, ya puede usar el sistema y el login no vuelve a pedir el cambio."""
    headers = {"Authorization": f"Bearer {iniciar(cliente, LAURA, temporal).json()['token']}"}
    assert cambiar(cliente, headers, temporal, "MiClave2027").json() == {"mensaje": "Contraseña actualizada."}
    assert cliente.get("/api/repuestos", headers=headers).status_code == 200
    assert iniciar(cliente, LAURA, "MiClave2027").json()["debe_cambiar_contrasena"] is False


def test_usuario_creado_debe_cambiarla(cliente, admin):
    """PA-36: un usuario nuevo entra con su temporal y debe cambiarla."""
    creado = cliente.post("/api/usuarios", headers=admin, json={
        "nombre": "Marta Rincón", "correo": "marta@facturapp.test", "rol": "oficina"}).json()
    respuesta = iniciar(cliente, "marta@facturapp.test", creado["contrasena_temporal"])
    assert respuesta.json()["debe_cambiar_contrasena"] is True
