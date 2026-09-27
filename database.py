"""
database.py
Funciones de acceso a datos contra PostgreSQL (base 'farmacia_central').

Reemplaza cualquier versión anterior basada en SQLite. El esquema
(categorias, proveedores, clientes, productos, consultas_clientes,
pedidos, detalle_pedidos, usuarios) debe existir ya en pgAdmin4 --
créalo corriendo tus scripts .sql desde el Query Tool antes de usar
esta app (ver sql/crear_tabla_usuarios.sql para la tabla nueva).
"""

from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash
from conexion.conexion import obtener_conexion


def init_db():
    """
    El esquema ya vive en PostgreSQL (creado desde pgAdmin4), así que
    aquí solo verificamos que la conexión funcione. Se conserva la
    función para no romper el 'database.init_db()' que llama app.py.
    """
    try:
        conexion = obtener_conexion()
        conexion.close()
        print("Conexión a PostgreSQL (farmacia_central) verificada correctamente.")
    except Exception as error:
        print("No se pudo conectar a PostgreSQL:", error)


# =========================================================
#  USUARIOS  (login, registro, contraseñas encriptadas)
# =========================================================

def obtener_usuario_por_email(email):
    """Devuelve la fila del usuario (con password_hash) o None si no existe."""
    conexion = obtener_conexion()
    cursor = conexion.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            "SELECT id_usuario, nombre, email, password_hash, rol FROM usuarios WHERE email = %s",
            (email.strip().lower(),),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conexion.close()


def obtener_usuario_por_id(id_usuario):
    """Devuelve la fila del usuario por id (usada por Flask-Login para recargar la sesión)."""
    conexion = obtener_conexion()
    cursor = conexion.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            "SELECT id_usuario, nombre, email, rol FROM usuarios WHERE id_usuario = %s",
            (id_usuario,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conexion.close()


def crear_usuario(nombre, email, password_plano, rol="cliente"):
    """
    Crea un usuario nuevo. La contraseña NUNCA se guarda en texto plano:
    se convierte a un hash irreversible (Werkzeug/scrypt) antes del INSERT.
    Por defecto el rol es 'cliente'; el rol 'admin' se asigna manualmente
    (ver crear_admin.py), nunca desde el formulario público de registro.
    """
    password_hash = generate_password_hash(password_plano)

    conexion = obtener_conexion()
    cursor = conexion.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            """
            INSERT INTO usuarios (nombre, email, password_hash, rol)
            VALUES (%s, %s, %s, %s)
            RETURNING id_usuario
            """,
            (nombre.strip(), email.strip().lower(), password_hash, rol),
        )
        id_usuario = cursor.fetchone()["id_usuario"]
        conexion.commit()
        return id_usuario
    finally:
        cursor.close()
        conexion.close()


# =========================================================
#  PRODUCTOS
# =========================================================

def _obtener_o_crear_categoria(cursor, nombre_categoria):
    """Devuelve id_categoria; si la categoría no existe, la crea."""
    cursor.execute(
        "SELECT id_categoria FROM categorias WHERE LOWER(nombre) = LOWER(%s)",
        (nombre_categoria,),
    )
    fila = cursor.fetchone()
    if fila:
        return fila["id_categoria"]

    cursor.execute(
        "INSERT INTO categorias (nombre) VALUES (%s) RETURNING id_categoria",
        (nombre_categoria,),
    )
    return cursor.fetchone()["id_categoria"]


def insertar_producto(nombre, categoria, descripcion, precio, stock,
                       icono="💊", id_proveedor=None):
    """
    'categoria' llega como texto desde el formulario; se busca (o crea)
    su id_categoria porque productos.id_categoria es una FK obligatoria.
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor(cursor_factory=RealDictCursor)
    try:
        id_categoria = _obtener_o_crear_categoria(cursor, categoria)
        cursor.execute(
            """
            INSERT INTO productos
                (nombre, id_categoria, descripcion, precio, stock, icono, id_proveedor)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (nombre, id_categoria, descripcion, precio, stock, icono, id_proveedor),
        )
        conexion.commit()
    finally:
        cursor.close()
        conexion.close()


# =========================================================
#  CLIENTES  (tabla clientes + tabla consultas_clientes)
# =========================================================

def _obtener_o_crear_cliente(cursor, nombre, email):
    cursor.execute("SELECT id_cliente FROM clientes WHERE email = %s", (email,))
    fila = cursor.fetchone()
    if fila:
        return fila["id_cliente"]

    cursor.execute(
        "INSERT INTO clientes (nombre, email) VALUES (%s, %s) RETURNING id_cliente",
        (nombre, email),
    )
    return cursor.fetchone()["id_cliente"]


def insertar_cliente(nombre, email, tipo_consulta, asunto, mensaje):
    """
    La tabla 'clientes' solo guarda nombre/email. El resto del
    formulario (tipo_consulta, asunto, mensaje) es una CONSULTA y se
    guarda en 'consultas_clientes', enlazada por id_cliente.
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor(cursor_factory=RealDictCursor)
    try:
        id_cliente = _obtener_o_crear_cliente(cursor, nombre, email)
        cursor.execute(
            """
            INSERT INTO consultas_clientes (id_cliente, tipo_consulta, asunto, mensaje)
            VALUES (%s, %s, %s, %s)
            """,
            (id_cliente, tipo_consulta, asunto, mensaje),
        )
        conexion.commit()
    finally:
        cursor.close()
        conexion.close()


# =========================================================
#  PROVEEDORES
# =========================================================

def insertar_proveedor(nombre, producto, telefono, email):
    """
    OJO: la tabla 'proveedores' de tu esquema NO tiene columna
    'producto', así que ese dato del formulario no se guarda con este
    esquema. Si lo necesitas, agrega la columna con:

        ALTER TABLE proveedores ADD COLUMN producto VARCHAR(80);

    y descomenta la versión de abajo que sí la inserta.
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute(
            "INSERT INTO proveedores (nombre, telefono, email) VALUES (%s, %s, %s)",
            (nombre, telefono, email),
        )
        # Si agregas la columna 'producto', usa en su lugar:
        # cursor.execute(
        #     "INSERT INTO proveedores (nombre, telefono, email, producto) VALUES (%s, %s, %s, %s)",
        #     (nombre, telefono, email, producto),
        # )
        conexion.commit()
    finally:
        cursor.close()
        conexion.close()


# =========================================================
#  PEDIDOS  (tabla pedidos + tabla detalle_pedidos)
# =========================================================

def _obtener_id_cliente_por_nombre(cursor, nombre_cliente):
    """
    Usado por el formulario ADMINISTRATIVO de pedidos (formulario_facturacion.html),
    donde el nombre del cliente se escribe como texto libre. Buscamos por
    nombre y, si no existe, lo creamos con un email provisional.
    """
    cursor.execute(
        "SELECT id_cliente FROM clientes WHERE nombre = %s LIMIT 1", (nombre_cliente,)
    )
    fila = cursor.fetchone()
    if fila:
        return fila["id_cliente"]

    email_provisional = f"{nombre_cliente.strip().replace(' ', '.').lower()}@sin-correo.com"
    cursor.execute(
        "INSERT INTO clientes (nombre, email) VALUES (%s, %s) RETURNING id_cliente",
        (nombre_cliente, email_provisional),
    )
    return cursor.fetchone()["id_cliente"]


def insertar_pedido(cliente, producto, cantidad, total, estado, fecha, metodo_pago,
                     email_cliente=None):
    """
    Registra un pedido.

    - email_cliente=None  -> flujo ADMINISTRATIVO (formulario_facturacion.html):
      el cliente es texto libre, se busca/crea por nombre.
    - email_cliente="..."  -> flujo de COMPRA de un usuario autenticado
      (ruta /comprar): se busca/crea el cliente por su email real, que es
      más confiable y evita duplicar el mismo cliente con nombres distintos.
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor(cursor_factory=RealDictCursor)
    try:
        if email_cliente:
            id_cliente = _obtener_o_crear_cliente(cursor, cliente, email_cliente)
        else:
            id_cliente = _obtener_id_cliente_por_nombre(cursor, cliente)

        cursor.execute(
            "SELECT id_producto, precio FROM productos WHERE nombre = %s LIMIT 1",
            (producto,),
        )
        fila_producto = cursor.fetchone()
        if not fila_producto:
            raise ValueError(f"El producto '{producto}' no existe en la base de datos.")

        id_producto = fila_producto["id_producto"]
        precio_unitario = float(fila_producto["precio"])
        subtotal = round(precio_unitario * cantidad, 2)

        cursor.execute(
            """
            INSERT INTO pedidos (id_cliente, fecha, estado, metodo_pago, total)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_pedido
            """,
            (id_cliente, fecha, estado, metodo_pago, total),
        )
        id_pedido = cursor.fetchone()["id_pedido"]

        cursor.execute(
            """
            INSERT INTO detalle_pedidos (id_pedido, id_producto, cantidad, precio_unitario, subtotal)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (id_pedido, id_producto, cantidad, precio_unitario, subtotal),
        )

        # Descuenta el stock vendido
        cursor.execute(
            "UPDATE productos SET stock = stock - %s WHERE id_producto = %s",
            (cantidad, id_producto),
        )

        conexion.commit()
    finally:
        cursor.close()
        conexion.close()
