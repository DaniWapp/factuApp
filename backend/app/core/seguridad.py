"""
Archivo:  backend/app/core/seguridad.py
Proyecto: FacturApp (backend)

Qué hace:
    1. Revisa que una contraseña cumpla la regla del sistema (RN-03):
       al menos 8 caracteres, con letras y números.
    2. Cifra contraseñas con bcrypt y comprueba si una contraseña
       escrita coincide con la guardada (RNF-01).
    3. Crea y lee los tokens JWT del inicio de sesión. El token dura
       los minutos de JWT_MINUTOS_VIGENCIA del .env (120) y se firma con
       JWT_CLAVE_SECRETA.

Conceptos:
    - Hash (cifrado de una sola vía): bcrypt convierte la contraseña en un
      texto como "$2b$12$..." del que NO se puede sacar la contraseña.
      Para comprobarla, se cifra lo que escribe la persona y se compara.
    - Sal (salt): un valor aleatorio que bcrypt mezcla con la contraseña,
      para que dos personas con la misma contraseña tengan hashes distintos.
    - JWT: un texto firmado que dice quién es el usuario y hasta cuándo
      vale. Si alguien lo modifica, la firma deja de coincidir.
    - "sub" (subject): dentro del token, el id del usuario.
    - "exp" (expiration): la fecha y hora en que el token vence.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from app.core.config import obtener_configuracion

# Regla de contraseña (RN-03).
LARGO_MINIMO = 8
# bcrypt solo usa los primeros 72 bytes de una contraseña; más largas se rechazan.
LARGO_MAXIMO_BYTES = 72


class TokenInvalido(Exception):
    """Se lanza cuando un token está vencido, fue alterado o no es un token válido."""


# ---------------------------------------------------------------- contraseñas

def validar_contrasena(contrasena: str) -> str | None:
    """Revisa la regla de contraseña.

    Devuelve None si la contraseña es válida, o el mensaje de error que
    se le mostrará al usuario si no lo es.
    """
    if len(contrasena) < LARGO_MINIMO:
        return "La contraseña debe tener al menos 8 caracteres."
    # any(...) es True si al menos un carácter cumple la condición.
    tiene_letra = any(caracter.isalpha() for caracter in contrasena)
    tiene_numero = any(caracter.isdigit() for caracter in contrasena)
    if not (tiene_letra and tiene_numero):
        return "La contraseña debe tener letras y números."
    if len(contrasena.encode("utf-8")) > LARGO_MAXIMO_BYTES:
        return "La contraseña es demasiado larga (máximo 72 caracteres)."
    return None


def cifrar_contrasena(contrasena: str) -> str:
    """Devuelve el hash bcrypt de una contraseña, listo para guardarlo en la base de datos.

    bcrypt trabaja con bytes, por eso se convierte el texto con encode()
    y el resultado se vuelve a texto con decode().
    """
    sal = bcrypt.gensalt()  # 12 rondas por defecto: lento a propósito, para dificultar ataques
    return bcrypt.hashpw(contrasena.encode("utf-8"), sal).decode("utf-8")


def verificar_contrasena(contrasena: str, hash_guardado: str) -> bool:
    """Dice si la contraseña escrita coincide con el hash guardado.

    Devuelve False (y no un error) si el hash guardado no es válido, por
    ejemplo el hash de ejemplo de database/seed.sql.
    """
    try:
        return bcrypt.checkpw(contrasena.encode("utf-8"), hash_guardado.encode("utf-8"))
    except ValueError:
        return False


# ---------------------------------------------------------------- tokens JWT

def crear_token(usuario_id: int, rol: str) -> str:
    """Crea un token JWT firmado para el usuario, que vence en JWT_MINUTOS_VIGENCIA minutos."""
    config = obtener_configuracion()
    ahora = datetime.now(timezone.utc)  # los tokens usan la hora universal (UTC)
    datos = {
        "sub": str(usuario_id),  # PyJWT exige que "sub" sea texto
        "rol": rol,
        "iat": ahora,  # "issued at": cuándo se creó
        "exp": ahora + timedelta(minutes=config.jwt_minutos_vigencia),
    }
    return jwt.encode(datos, config.jwt_clave_secreta, algorithm=config.jwt_algoritmo)


def leer_token(token: str) -> dict[str, Any]:
    """Comprueba la firma y la vigencia de un token y devuelve sus datos.

    Lanza TokenInvalido si el token venció, fue alterado o está mal
    formado. La API lo convertirá en una respuesta 401.
    """
    config = obtener_configuracion()
    try:
        # algorithms=[...] es obligatorio: evita que alguien cambie el algoritmo del token.
        return jwt.decode(token, config.jwt_clave_secreta, algorithms=[config.jwt_algoritmo])
    except jwt.ExpiredSignatureError as error:
        raise TokenInvalido("El token venció.") from error
    except jwt.InvalidTokenError as error:
        raise TokenInvalido("El token no es válido.") from error
