"""
Archivo:  backend/app/services/auth_service.py
Proyecto: FacturApp (backend)

Qué hace:
    Las reglas del inicio de sesión y del cambio de contraseña.

Inicio de sesión (HU-01):
    - Campos vacíos: 422 "Escriba su correo y su contraseña."
    - Correo que no existe o contraseña incorrecta: el MISMO error 401
      "Correo o contraseña incorrectos.", para no revelar qué correos
      están registrados (PA-02).
    - Usuario desactivado: 401 con el mensaje de HU-01 (RN-01).
    - Si todo está bien: un token de 120 minutos y si el usuario debe
      cambiar su contraseña temporal (HU-05).

Cambio de contraseña (HU-04 y HU-05):
    - La confirmación debe coincidir y la nueva debe cumplir RN-03.
    - La contraseña actual debe ser correcta.
    - La nueva debe ser diferente a la actual (también a la temporal).
    - Al cambiarla, deja de ser temporal.
"""

from typing import Any

from app.core.dependencias import MENSAJE_DESACTIVADO
from app.core.errores import Conflicto, DatosInvalidos, NoAutenticado
from app.core.seguridad import cifrar_contrasena, crear_token, validar_contrasena, verificar_contrasena
from app.repositories import usuarios_repo
from app.repositories.tablas import Usuario
from app.schemas.auth import CambioContrasenaEntrada, LoginEntrada

# Hash válido de una contraseña que nadie conoce. Se usa cuando el correo
# no existe, para que bcrypt tarde lo mismo y no se pueda adivinar, por el
# tiempo de respuesta, si un correo está registrado.
HASH_FALSO = cifrar_contrasena("NadieConoceEsta123")


def iniciar_sesion(conexion: Any, datos: LoginEntrada) -> dict[str, Any]:
    """Revisa correo y contraseña y devuelve el token con los datos del usuario."""
    if not datos.correo or not datos.contrasena:
        raise DatosInvalidos("CAMPOS_VACIOS", "Escriba su correo y su contraseña.")

    usuario = usuarios_repo.buscar_por_correo(conexion, datos.correo)
    hash_guardado = usuario.contrasena_hash if usuario else HASH_FALSO
    contrasena_correcta = verificar_contrasena(datos.contrasena, hash_guardado)

    if usuario is None or not contrasena_correcta:
        raise NoAutenticado("CREDENCIALES_INVALIDAS", "Correo o contraseña incorrectos.")
    if not usuario.activo:
        raise NoAutenticado("USUARIO_DESACTIVADO", MENSAJE_DESACTIVADO)

    return {
        "token": crear_token(usuario.id, usuario.rol),
        "tipo": "bearer",
        "debe_cambiar_contrasena": usuario.debe_cambiar_contrasena,
        "usuario": usuario,
    }


def cambiar_contrasena(conexion: Any, usuario: Usuario, datos: CambioContrasenaEntrada) -> None:
    """Cambia la contraseña del propio usuario y le quita la marca de temporal."""
    if datos.nueva != datos.confirmacion:
        raise DatosInvalidos("CONFIRMACION_DISTINTA", "Las contraseñas nuevas no coinciden.",
                             {"confirmacion": "Las contraseñas nuevas no coinciden."})
    error_regla = validar_contrasena(datos.nueva)
    if error_regla:
        raise DatosInvalidos("CONTRASENA_NO_VALIDA", error_regla, {"nueva": error_regla})

    # Se lee de nuevo, bloqueado, para comparar con el hash más reciente.
    guardado = usuarios_repo.buscar_por_id(conexion, usuario.id, bloquear=True)
    if not verificar_contrasena(datos.actual, guardado.contrasena_hash):
        raise Conflicto("CONTRASENA_ACTUAL_INCORRECTA", "La contraseña actual no es correcta.",
                        {"actual": "La contraseña actual no es correcta."})
    if datos.nueva == datos.actual:
        mensaje = ("La contraseña nueva debe ser diferente a la temporal." if guardado.debe_cambiar_contrasena
                   else "La contraseña nueva debe ser diferente a la actual.")
        raise DatosInvalidos("CONTRASENA_REPETIDA", mensaje, {"nueva": mensaje})

    usuarios_repo.cambiar_contrasena(conexion, usuario.id, cifrar_contrasena(datos.nueva), temporal=False)
