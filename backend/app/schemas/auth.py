"""
Archivo:  backend/app/schemas/auth.py
Proyecto: FacturApp (backend)

Qué hace:
    Forma de los datos del inicio de sesión, de "mis datos" y del cambio
    de contraseña.

Por qué el login acepta campos vacíos aquí:
    Si el correo o la contraseña llegan vacíos, el service responde con
    el mensaje exacto de HU-01 ("Escriba su correo y su contraseña."), en
    lugar del mensaje general de validación.
"""

from pydantic import BaseModel, Field, field_validator


class LoginEntrada(BaseModel):
    """Correo y contraseña para iniciar sesión."""
    correo: str = Field(default="", max_length=150)
    contrasena: str = Field(default="", max_length=200)

    @field_validator("correo")
    @classmethod
    def normalizar_correo(cls, valor: str) -> str:
        """El correo se compara sin espacios en los extremos y en minúsculas."""
        return valor.strip().lower()


class UsuarioSesion(BaseModel):
    """Datos del usuario que inició sesión (también la respuesta de GET /api/auth/yo)."""
    id: int
    nombre: str
    correo: str
    rol: str
    debe_cambiar_contrasena: bool


class LoginSalida(BaseModel):
    """Respuesta del login: el token, su tipo y los datos del usuario.

    debe_cambiar_contrasena se repite arriba para que el frontend sepa
    de inmediato si debe llevar al usuario a cambiarla (HU-05).
    """
    token: str
    tipo: str = "bearer"
    debe_cambiar_contrasena: bool
    usuario: UsuarioSesion


class CambioContrasenaEntrada(BaseModel):
    """Contraseña actual, la nueva y su confirmación (HU-04, HU-05)."""
    actual: str = Field(min_length=1, max_length=200)
    nueva: str = Field(min_length=1, max_length=200)
    confirmacion: str = Field(min_length=1, max_length=200)


class MensajeSalida(BaseModel):
    """Respuesta con un mensaje para mostrar a la persona."""
    mensaje: str
