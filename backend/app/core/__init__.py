"""
Capa core: lo que usa toda la API.

Aquí irán (Entregable 06):
    config.py        Lee el archivo .env con pydantic-settings.
    seguridad.py     Cifra contraseñas (bcrypt) y crea y verifica tokens (JWT).
    dependencias.py  Obtiene el usuario actual desde el token y exige un rol.
    errores.py       Errores del negocio y su código HTTP (404, 409...).
"""
