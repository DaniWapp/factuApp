"""
Archivo:  backend/app/db/verificar.py
Proyecto: FacturApp (backend)

Qué hace:
    Comprueba que la API puede conectarse a la base de datos y muestra
    cuántos registros hay en cada tabla. No cambia nada.

Cómo se ejecuta (desde la carpeta backend/):
    .venv\\Scripts\\python.exe -m app.db.verificar

    "-m app.db.verificar" ejecuta este archivo como parte del paquete app,
    para que funcionen los "from app...".
"""

from app.core.config import obtener_configuracion
from app.db.conexion import transaccion
from app.repositories.base import contar_registros
from app.repositories.tablas import TABLAS


def main() -> None:
    """Se conecta, cuenta los registros de cada tabla y los muestra."""
    config = obtener_configuracion()
    print(f"Conectando a {config.db_name} en {config.db_host}:{config.db_port} con el usuario {config.db_user}...")

    with transaccion() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT VERSION() AS version")
            print(f"Conexión correcta. Servidor: {cursor.fetchone()['version']}\n")

        print(f"{'Tabla':<24}{'Registros':>10}")
        print("-" * 34)
        total = 0
        for tabla in TABLAS:
            cantidad = contar_registros(conexion, tabla)
            total += cantidad
            print(f"{tabla:<24}{cantidad:>10}")
        print("-" * 34)
        print(f"{'Total':<24}{total:>10}")


if __name__ == "__main__":
    main()
