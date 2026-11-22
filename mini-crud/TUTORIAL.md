# Tutorial: Mini CRUD de usuarios desde cero

Guía para construir y probar, paso a paso, un servidor muy sencillo con FastAPI y MySQL que permite **crear, listar, ver, editar y borrar** usuarios (un "CRUD"), y demostrarlo con **Postman**.

Cada paso tiene:

- **Qué vamos a hacer**, en pocas palabras.
- **El comando o el código** para copiar, en un bloque aparte.
- **Cómo saber que salió bien**.

Los comandos son para **PowerShell** en Windows, salvo que se diga otra cosa.

---

## Etapas

1. **Base de datos:** crear la base `mini_crud`, la tabla `usuarios` y un usuario de MySQL para el proyecto.
2. **Servidor:** el código de FastAPI con los endpoints *(se completará en la siguiente etapa)*.
3. **Postman:** importar la colección y probar los endpoints *(pendiente)*.
4. **Pruebas automáticas y exposición** *(pendiente)*.

---

## Antes de empezar

Necesita tener instalado:

| Programa | Para qué | Cómo comprobarlo |
|---|---|---|
| **MySQL** (de AppServ o de XAMPP) | Guardar los datos | Ver el paso 1.1 |
| **Python 3.12** | Ejecutar el servidor | `py -3.12 --version` |
| **Postman** | Probar los endpoints | Descarga: [postman.com/downloads](https://www.postman.com/downloads/) |
| **VS Code** (opcional) | Escribir el código | — |

Comprobar Python:

```
py -3.12 --version
```

Debe responder algo como `Python 3.12.10`.

---

## Etapa 1: Base de datos

### 1.1 Encender MySQL

**Qué hacemos:** el servidor de MySQL debe estar encendido para poder crear la base y para que el servidor de Python se conecte.

**Con AppServ:** abra una ventana de PowerShell **nueva**, pegue este comando y **deje la ventana abierta** mientras trabaja:

```
& "C:\AppServ\MySQL\bin\mysqld.exe" --defaults-file="C:\AppServ\MySQL\my.ini" --console
```

**Con XAMPP:** abra el panel de XAMPP y pulse **Start** en la fila de **MySQL**.

**Salió bien si:** aparece una línea con `ready for connections` y `port: 3306` (AppServ), o MySQL se pone en verde (XAMPP).

> Para apagarlo bien en AppServ (en otra ventana), en lugar de cerrar la ventana:
> ```
> & "C:\AppServ\MySQL\bin\mysqladmin.exe" -u root shutdown
> ```

### 1.2 Crear la carpeta del proyecto

**Qué hacemos:** una carpeta para todos los archivos del mini proyecto.

```
New-Item -ItemType Directory -Force C:\AppServ\www\facturApp\mini-crud
cd C:\AppServ\www\facturApp\mini-crud
```

**Salió bien si:** la terminal queda en la carpeta `mini-crud`.

### 1.3 Crear el archivo `database.sql`

**Qué hacemos:** un archivo con las instrucciones SQL que crean la base, la tabla y 3 usuarios de ejemplo.

**Conceptos:**

- **Base de datos:** el "archivador" donde se guardan las tablas.
- **Tabla:** como una hoja de cálculo: columnas (los datos) y filas (cada usuario).
- **PRIMARY KEY:** la columna que identifica cada fila; no se repite.
- **AUTO_INCREMENT:** MySQL numera solo (1, 2, 3...).
- **UNIQUE:** el valor no se repite (dos usuarios no pueden tener el mismo correo).
- **NOT NULL:** el dato es obligatorio.

Cree el archivo `database.sql` dentro de `mini-crud` con este contenido:

```sql
-- Crea la base de datos si no existe. utf8mb4 guarda bien tildes y ñ.
CREATE DATABASE IF NOT EXISTS mini_crud
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE mini_crud;

-- Borra la tabla si ya existía, para poder ejecutar el archivo varias veces.
DROP TABLE IF EXISTS usuarios;

CREATE TABLE usuarios (
    id        INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nombre    VARCHAR(100) NOT NULL,
    correo    VARCHAR(150) NOT NULL,
    creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_usuarios PRIMARY KEY (id),
    CONSTRAINT uq_usuarios_correo UNIQUE (correo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Datos de ejemplo para la demostración.
INSERT INTO usuarios (nombre, correo) VALUES
    ('Laura Gómez',  'laura.gomez@ejemplo.test'),
    ('Andrés Muñoz', 'andres.munoz@ejemplo.test'),
    ('Marta Rincón', 'marta.rincon@ejemplo.test');

-- Comprobación: debe mostrar los 3 usuarios.
SELECT id, nombre, correo, creado_en FROM usuarios;
```

> El archivo del proyecto (`mini-crud/database.sql`) tiene además comentarios explicando cada línea.

### 1.4 Ejecutar `database.sql`

**Qué hacemos:** le pedimos a MySQL que ejecute el archivo. Usamos el usuario `root`, el administrador de MySQL.

PowerShell no acepta el símbolo `<`, por eso se usa `cmd /c`:

```
cmd /c "C:\AppServ\MySQL\bin\mysql.exe -u root -t --default-character-set=utf8mb4 < database.sql"
```

- Con **XAMPP**, cambie la ruta por `C:\xampp\mysql\bin\mysql.exe`.
- Si su `root` tiene contraseña, agregue `-p` después de `-u root` y escríbala cuando la pida.
- `--default-character-set=utf8mb4` evita que las tildes se guarden dañadas.

**Salió bien si:** aparece una tabla con Laura Gómez, Andrés Muñoz y Marta Rincón.

> Otra forma: en **phpMyAdmin**, pestaña **Importar**, elegir `database.sql` y pulsar **Continuar**.

### 1.5 Crear un usuario de MySQL para el proyecto

**Qué hacemos:** en lugar de usar `root` (que puede hacer todo en todas las bases), creamos un usuario `mini_crud` que **solo** puede trabajar en la base `mini_crud`. Es una buena práctica de seguridad: si alguien conoce esa contraseña, no puede tocar otras bases.

1. Elija una contraseña (letras y números, sin comillas). En el ejemplo se llama `MiClaveSegura2026`: **cámbiela por la suya**.
2. Abra la consola de MySQL:

```
& "C:\AppServ\MySQL\bin\mysql.exe" -u root
```

3. Dentro de la consola (`mysql>`), pegue esto **con su contraseña**:

```sql
CREATE USER 'mini_crud'@'localhost' IDENTIFIED WITH mysql_native_password BY 'MiClaveSegura2026';
CREATE USER 'mini_crud'@'127.0.0.1' IDENTIFIED WITH mysql_native_password BY 'MiClaveSegura2026';
GRANT ALL PRIVILEGES ON mini_crud.* TO 'mini_crud'@'localhost';
GRANT ALL PRIVILEGES ON mini_crud.* TO 'mini_crud'@'127.0.0.1';
FLUSH PRIVILEGES;
EXIT;
```

**Conceptos:**

- `'mini_crud'@'localhost'` y `'mini_crud'@'127.0.0.1'`: el mismo usuario, para las dos formas en que un programa se conecta desde este equipo.
- `mysql_native_password`: el tipo de contraseña que entienden PyMySQL y phpMyAdmin sin configuración extra.
- `GRANT ALL PRIVILEGES ON mini_crud.*`: todos los permisos, pero **solo** en la base `mini_crud`.

**Salió bien si:** cada línea responde `Query OK`.

### 1.6 Crear los archivos `.env.example` y `.env`

**Qué hacemos:** los datos de conexión (y sobre todo la contraseña) **nunca** se escriben dentro del código. Se guardan en un archivo `.env`, que **no se sube a GitHub**. Y se sube una plantilla, `.env.example`, sin la contraseña real.

Cree `.env.example` con este contenido:

```
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=mini_crud
DB_USER=mini_crud
DB_PASSWORD=cambia-esto
```

Cree una copia llamada `.env`:

```
Copy-Item .env.example .env
```

Abra `.env` y cambie `cambia-esto` por la contraseña que eligió en el paso 1.5.

**Muy importante:** el archivo `.gitignore` del repositorio debe tener la línea `.env` (o `**/.env`) para que Git nunca lo suba. Compruébelo desde la carpeta del repositorio:

```
git check-ignore -v mini-crud/.env
```

**Salió bien si:** la respuesta menciona `.gitignore` (eso significa que Git lo ignora).

### 1.7 Comprobar que el usuario del proyecto puede entrar

**Qué hacemos:** nos conectamos con el usuario `mini_crud` (no con `root`) y contamos los usuarios de la tabla.

```
& "C:\AppServ\MySQL\bin\mysql.exe" -u mini_crud -p -h 127.0.0.1 -e "SHOW DATABASES; SELECT COUNT(*) FROM mini_crud.usuarios;"
```

Escriba la contraseña cuando la pida (no se ve mientras se escribe).

**Salió bien si:** solo aparecen las bases `information_schema` y `mini_crud` (no ve las demás) y el conteo es `3`.

### Fin de la etapa 1

Ya tiene:

- La base `mini_crud` con la tabla `usuarios` y 3 usuarios de ejemplo.
- Un usuario de MySQL con permisos solo sobre esa base.
- Los archivos `database.sql`, `.env.example` y `.env` (este último sin subir a GitHub).

**Siguiente etapa:** el servidor con FastAPI.
