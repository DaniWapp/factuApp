"""
Archivo:  backend/app/core/config.py
Proyecto: FacturApp (backend)

Qué hace:
    Lee la configuración del archivo backend/.env (datos de la base de
    datos, clave de los tokens, puerto...) y la deja disponible para
    toda la API con la función obtener_configuracion().

Por qué así:
    Las contraseñas y claves nunca se escriben en el código (RNF-06):
    viven en el .env, que no se sube a GitHub.

Conceptos:
    - pydantic-settings: lee las variables del .env y revisa su tipo.
      Si DB_PORT no es un número, la API no arranca y avisa el error.
    - Los nombres de los atributos (db_host) coinciden con las variables
      del .env (DB_HOST) sin importar las mayúsculas.
    - lru_cache: guarda el resultado la primera vez, para no leer el
      archivo .env en cada petición.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Ruta absoluta de backend/.env: así se encuentra aunque la API se
# ejecute desde otra carpeta. parents[2] sube de app/core/ a backend/.
ARCHIVO_ENV = Path(__file__).resolve().parents[2] / ".env"


class Configuracion(BaseSettings):
    """Variables del archivo .env, con su tipo y un valor por defecto cuando aplica."""

    # Base de datos
    db_host: str = "127.0.0.1"
    db_port: int = 3306
    db_name: str = "facturapp"
    db_user: str
    db_password: str = ""

    # Tokens JWT
    jwt_clave_secreta: str
    jwt_algoritmo: str = "HS256"
    jwt_minutos_vigencia: int = 120

    # API
    api_puerto: int = 8000
    zona_horaria: str = "America/Bogota"
    modo_depuracion: bool = False

    # Dónde está el .env y cómo leerlo. extra="ignore" no falla si el
    # .env trae variables que esta clase todavía no usa.
    model_config = SettingsConfigDict(env_file=ARCHIVO_ENV, env_file_encoding="utf-8", extra="ignore")


@lru_cache
def obtener_configuracion() -> Configuracion:
    """Devuelve la configuración leída del .env (la lee una sola vez)."""
    return Configuracion()
