"""
Archivo:  backend/app/repositories/catalogos_repo.py
Proyecto: FacturApp (backend)

Qué hace:
    Consultas SQL de los tres catálogos: categorías, repuestos y
    contratistas (capa repositories). Todas reciben una conexión abierta
    y usan parámetros %s (RNF-05).

Nota sobre nombres repetidos (RN-07):
    Las tablas usan la colación utf8mb4_unicode_ci, que compara sin
    distinguir mayúsculas ni tildes. Por eso "WHERE nombre = %s" con
    "valvulas" encuentra "Válvulas".
"""

from typing import Any

from app.repositories.tablas import Categoria, Contratista, Repuesto, desde_fila


def _filtro_activo(activo: bool | None) -> tuple[str, tuple]:
    """Arma el filtro opcional por estado: sin filtro, solo activos o solo inactivos."""
    if activo is None:
        return "", ()
    return " WHERE activo = %s", (int(activo),)


# ---------------------------------------------------------------- categorías

def listar_categorias(conexion: Any, activo: bool | None = None) -> list[dict[str, Any]]:
    """Categorías con la cantidad de repuestos activos de cada una."""
    filtro, parametros = _filtro_activo(activo)
    filtro = filtro.replace("activo", "c.activo")
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT c.id, c.nombre, c.activo, "
            "(SELECT COUNT(*) FROM repuestos r WHERE r.categoria_id = c.id AND r.activo = 1) AS repuestos_activos "
            f"FROM categorias c{filtro} ORDER BY c.nombre",
            parametros,
        )
        return cursor.fetchall()


def buscar_categoria(conexion: Any, categoria_id: int, bloquear: bool = False) -> Categoria | None:
    """Busca una categoría por id. bloquear=True la reserva hasta el final de la transacción."""
    with conexion.cursor() as cursor:
        cursor.execute("SELECT id, nombre, activo FROM categorias WHERE id = %s" + (" FOR UPDATE" if bloquear else ""),
                       (categoria_id,))
        fila = cursor.fetchone()
    return desde_fila(Categoria, fila) if fila else None


def buscar_categoria_por_nombre(conexion: Any, nombre: str) -> Categoria | None:
    """Busca una categoría por nombre, sin distinguir mayúsculas ni tildes."""
    with conexion.cursor() as cursor:
        cursor.execute("SELECT id, nombre, activo FROM categorias WHERE nombre = %s", (nombre,))
        fila = cursor.fetchone()
    return desde_fila(Categoria, fila) if fila else None


def crear_categoria(conexion: Any, nombre: str) -> int:
    """Guarda una categoría nueva (activa) y devuelve su id."""
    with conexion.cursor() as cursor:
        cursor.execute("INSERT INTO categorias (nombre) VALUES (%s)", (nombre,))
        return cursor.lastrowid


def actualizar_categoria(conexion: Any, categoria_id: int, nombre: str) -> None:
    """Cambia el nombre de una categoría."""
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE categorias SET nombre = %s WHERE id = %s", (nombre, categoria_id))


def cambiar_estado_categoria(conexion: Any, categoria_id: int, activo: bool) -> None:
    """Activa o desactiva una categoría."""
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE categorias SET activo = %s WHERE id = %s", (int(activo), categoria_id))


def contar_repuestos_activos(conexion: Any, categoria_id: int) -> int:
    """Cuántos repuestos activos tiene una categoría (RN-06)."""
    with conexion.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS total FROM repuestos WHERE categoria_id = %s AND activo = 1", (categoria_id,))
        return int(cursor.fetchone()["total"])


# ---------------------------------------------------------------- repuestos

COLUMNAS_REPUESTO = ("id, codigo, nombre, categoria_id, unidad_medida, stock_almacen, stock_apartado, "
                     "stock_minimo, activo")


def listar_repuestos(conexion: Any, activo: bool | None = None) -> list[dict[str, Any]]:
    """Repuestos con el nombre de su categoría, SIN datos de stock (RN-02: la Oficina no ve el stock)."""
    filtro, parametros = _filtro_activo(activo)
    filtro = filtro.replace("activo", "r.activo")
    with conexion.cursor() as cursor:
        cursor.execute(
            "SELECT r.id, r.codigo, r.nombre, r.categoria_id, c.nombre AS categoria, r.unidad_medida, r.activo "
            f"FROM repuestos r JOIN categorias c ON c.id = r.categoria_id{filtro} ORDER BY r.codigo",
            parametros,
        )
        return cursor.fetchall()


def buscar_repuesto(conexion: Any, repuesto_id: int, bloquear: bool = False) -> Repuesto | None:
    """Busca un repuesto por id. bloquear=True reserva la fila (FOR UPDATE)."""
    with conexion.cursor() as cursor:
        cursor.execute(f"SELECT {COLUMNAS_REPUESTO} FROM repuestos WHERE id = %s" + (" FOR UPDATE" if bloquear else ""),
                       (repuesto_id,))
        fila = cursor.fetchone()
    return desde_fila(Repuesto, fila) if fila else None


def buscar_repuesto_por(conexion: Any, columna: str, valor: str) -> Repuesto | None:
    """Busca un repuesto por "codigo" o por "nombre" (solo esas dos columnas)."""
    if columna not in ("codigo", "nombre"):
        raise ValueError("Columna no permitida")
    with conexion.cursor() as cursor:
        cursor.execute(f"SELECT {COLUMNAS_REPUESTO} FROM repuestos WHERE {columna} = %s", (valor,))
        fila = cursor.fetchone()
    return desde_fila(Repuesto, fila) if fila else None


def crear_repuesto(conexion: Any, codigo: str, nombre: str, categoria_id: int, unidad_medida: str) -> int:
    """Guarda un repuesto nuevo. El stock no se escribe: empieza en 0 (RN-09)."""
    with conexion.cursor() as cursor:
        cursor.execute("INSERT INTO repuestos (codigo, nombre, categoria_id, unidad_medida) VALUES (%s, %s, %s, %s)",
                       (codigo, nombre, categoria_id, unidad_medida))
        return cursor.lastrowid


def actualizar_repuesto(conexion: Any, repuesto_id: int, codigo: str, nombre: str, categoria_id: int,
                        unidad_medida: str) -> None:
    """Cambia los datos del catálogo. Nunca cambia el stock (RN-09)."""
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE repuestos SET codigo = %s, nombre = %s, categoria_id = %s, unidad_medida = %s "
                       "WHERE id = %s", (codigo, nombre, categoria_id, unidad_medida, repuesto_id))


def cambiar_estado_repuesto(conexion: Any, repuesto_id: int, activo: bool) -> None:
    """Activa o desactiva un repuesto."""
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE repuestos SET activo = %s WHERE id = %s", (int(activo), repuesto_id))


# ---------------------------------------------------------------- contratistas

COLUMNAS_CONTRATISTA = "id, documento, documento_normalizado, nombre, telefono, activo"


def listar_contratistas(conexion: Any, activo: bool | None = None) -> list[Contratista]:
    """Contratistas ordenados por nombre."""
    filtro, parametros = _filtro_activo(activo)
    with conexion.cursor() as cursor:
        cursor.execute(f"SELECT {COLUMNAS_CONTRATISTA} FROM contratistas{filtro} ORDER BY nombre", parametros)
        return [desde_fila(Contratista, fila) for fila in cursor.fetchall()]


def buscar_contratista(conexion: Any, contratista_id: int, bloquear: bool = False) -> Contratista | None:
    """Busca un contratista por id."""
    with conexion.cursor() as cursor:
        cursor.execute(f"SELECT {COLUMNAS_CONTRATISTA} FROM contratistas WHERE id = %s"
                       + (" FOR UPDATE" if bloquear else ""), (contratista_id,))
        fila = cursor.fetchone()
    return desde_fila(Contratista, fila) if fila else None


def buscar_contratista_por_documento(conexion: Any, documento_normalizado: str) -> Contratista | None:
    """Busca un contratista por su documento normalizado (solo dígitos, RN-08)."""
    with conexion.cursor() as cursor:
        cursor.execute(f"SELECT {COLUMNAS_CONTRATISTA} FROM contratistas WHERE documento_normalizado = %s",
                       (documento_normalizado,))
        fila = cursor.fetchone()
    return desde_fila(Contratista, fila) if fila else None


def crear_contratista(conexion: Any, documento: str, documento_normalizado: str, nombre: str,
                      telefono: str | None) -> int:
    """Guarda un contratista nuevo (activo) y devuelve su id."""
    with conexion.cursor() as cursor:
        cursor.execute("INSERT INTO contratistas (documento, documento_normalizado, nombre, telefono) "
                       "VALUES (%s, %s, %s, %s)", (documento, documento_normalizado, nombre, telefono))
        return cursor.lastrowid


def actualizar_contratista(conexion: Any, contratista_id: int, documento: str, documento_normalizado: str,
                           nombre: str, telefono: str | None) -> None:
    """Cambia los datos de un contratista."""
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE contratistas SET documento = %s, documento_normalizado = %s, nombre = %s, "
                       "telefono = %s WHERE id = %s",
                       (documento, documento_normalizado, nombre, telefono, contratista_id))


def cambiar_estado_contratista(conexion: Any, contratista_id: int, activo: bool) -> None:
    """Activa o desactiva un contratista."""
    with conexion.cursor() as cursor:
        cursor.execute("UPDATE contratistas SET activo = %s WHERE id = %s", (int(activo), contratista_id))
