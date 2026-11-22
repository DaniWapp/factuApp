"""
Archivo:  backend/crear_admin.py
Proyecto: FacturApp (backend)

Qué hace:
    Crea un usuario Admin en la base de datos, con la contraseña cifrada
    con bcrypt. Se usa la primera vez que se instala el sistema, o para
    darle una contraseña real al Admin de los datos de ejemplo
    (admin@facturapp.test), que viene con un hash que no sirve para entrar.

Cómo se ejecuta (desde la carpeta backend/, con MySQL encendido):
    .venv\\Scripts\\python.exe crear_admin.py

    El script pregunta el nombre, el correo y la contraseña. La
    contraseña se escribe dos veces y NO se ve en la pantalla mientras
    se escribe (es normal: así funciona getpass).

Reglas que revisa:
    - Nombre: obligatorio, máximo 100 caracteres.
    - Correo: con formato de correo, máximo 150 caracteres.
    - Contraseña: al menos 8 caracteres, con letras y números (RN-03).

Conceptos:
    - input(): muestra una pregunta y espera lo que escriba la persona.
    - getpass(): igual que input(), pero sin mostrar lo que se escribe.
    - Expresión regular (re): un patrón para revisar textos; aquí, que
      el correo tenga la forma algo@algo.algo.
    - transaccion(): guarda todo junto al final (COMMIT) o nada si falla.
"""

import re
import sys
from getpass import getpass

from app.core.seguridad import cifrar_contrasena, validar_contrasena
from app.db.conexion import transaccion
from app.repositories import usuarios_repo

# Patrón sencillo de correo: texto, una @, texto, un punto y texto, sin espacios.
PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def pedir_nombre() -> str:
    """Pide el nombre hasta que sea válido."""
    while True:
        nombre = input("Nombre del administrador: ").strip()  # strip() quita espacios al inicio y al final
        if not nombre:
            print("  Escriba el nombre.")
        elif len(nombre) > 100:
            print("  El nombre puede tener máximo 100 caracteres.")
        else:
            return nombre


def pedir_correo() -> str:
    """Pide el correo hasta que tenga un formato válido. Lo guarda en minúsculas."""
    while True:
        correo = input("Correo: ").strip().lower()
        if not PATRON_CORREO.match(correo):
            print("  Escriba un correo válido, por ejemplo admin@empresa.com.")
        elif len(correo) > 150:
            print("  El correo puede tener máximo 150 caracteres.")
        else:
            return correo


def pedir_contrasena() -> str:
    """Pide la contraseña dos veces, sin mostrarla, hasta que sea válida y coincida."""
    print("La contraseña debe tener al menos 8 caracteres, con letras y números.")
    print("(Mientras la escribe no se verá nada en la pantalla.)")
    while True:
        contrasena = getpass("Contraseña: ")
        error = validar_contrasena(contrasena)
        if error:
            print(f"  {error}")
            continue
        confirmacion = getpass("Repita la contraseña: ")
        if confirmacion != contrasena:
            print("  Las contraseñas no coinciden. Intente de nuevo.")
            continue
        return contrasena


def preguntar_si(pregunta: str) -> bool:
    """Hace una pregunta de sí o no. Devuelve True solo si la respuesta es "s"."""
    return input(f"{pregunta} (s/n): ").strip().lower() == "s"


def main() -> int:
    """Pide los datos, los valida y guarda el Admin. Devuelve 0 si salió bien."""
    print("=== Crear administrador de FacturApp ===\n")

    # Paso 1: pedir y validar los datos.
    nombre = pedir_nombre()
    correo = pedir_correo()
    contrasena = pedir_contrasena()

    # Paso 2: cifrar la contraseña. Desde aquí solo se usa el hash;
    # la contraseña en texto normal nunca se guarda ni se muestra.
    contrasena_hash = cifrar_contrasena(contrasena)

    # Paso 3: guardar en la base de datos dentro de una transacción.
    with transaccion() as conexion:
        existente = usuarios_repo.buscar_por_correo(conexion, correo)

        if existente is None:
            # Correo nuevo: se crea el Admin. Su contraseña no es temporal,
            # porque la eligió el mismo administrador.
            usuario_id = usuarios_repo.crear(conexion, nombre, correo, contrasena_hash,
                                             rol="admin", debe_cambiar_contrasena=False)
            print(f"\nAdmin creado: {nombre} <{correo}> (id {usuario_id}).")
        else:
            # El correo ya existe (por ejemplo, el Admin de los datos de ejemplo).
            print(f"\nYa existe un usuario con el correo {correo} ({existente.nombre}, rol {existente.rol}).")
            if not preguntar_si("¿Desea reemplazar su contraseña y dejarlo como Admin activo?"):
                print("No se hizo ningún cambio.")
                return 1
            usuarios_repo.actualizar_como_admin(conexion, existente.id, nombre, contrasena_hash)
            print(f"Admin actualizado: {nombre} <{correo}> (id {existente.id}).")

    # Al salir del "with" se hizo COMMIT: los cambios ya están guardados.
    print("Ya puede iniciar sesión con ese correo y la contraseña que escribió.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        # Ctrl + C: la persona canceló; como no se llegó a guardar, no hay cambios.
        print("\nCancelado. No se guardó nada.")
        sys.exit(1)
