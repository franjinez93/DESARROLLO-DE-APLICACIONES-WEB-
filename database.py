import sqlite3
import os

DB_FOLDER = "data"
DB_PATH = os.path.join(DB_FOLDER, "farmacia.db")


def get_connection():
    """Crea la carpeta data/ si no existe y devuelve una conexión a SQLite."""
    os.makedirs(DB_FOLDER, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # permite acceder a las columnas por nombre
    return conn


def init_db():
    """Crea las tablas en farmacia.db si no existen. La base inicia vacía:
    no se siembra ningún dato de ejemplo."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL,
            icono TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL,
            tipo_consulta TEXT NOT NULL,
            asunto TEXT NOT NULL,
            mensaje TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            producto TEXT NOT NULL,
            telefono TEXT,
            email TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            producto TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            total REAL NOT NULL,
            estado TEXT NOT NULL,
            fecha TEXT NOT NULL,
            metodo_pago TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    # Nota: la base de datos inicia completamente vacía a propósito.
    # No se siembra ningún dato de ejemplo; todos los registros se
    # agregan desde cero mediante los formularios Flask-WTF de la app.


# ================= PRODUCTOS =================
def obtener_productos():
    conn = get_connection()
    filas = conn.execute("SELECT * FROM productos").fetchall()
    conn.close()
    return [dict(f) for f in filas]


def insertar_producto(nombre, categoria, descripcion, precio, stock, icono="💊"):
    conn = get_connection()
    conn.execute(
        "INSERT INTO productos (nombre, categoria, descripcion, precio, stock, icono) VALUES (?, ?, ?, ?, ?, ?)",
        (nombre, categoria, descripcion, precio, stock, icono),
    )
    conn.commit()
    conn.close()


# ================= CLIENTES =================
def obtener_clientes():
    conn = get_connection()
    filas = conn.execute("SELECT * FROM clientes").fetchall()
    conn.close()
    return [dict(f) for f in filas]


def insertar_cliente(nombre, email, tipo_consulta, asunto, mensaje):
    conn = get_connection()
    conn.execute(
        "INSERT INTO clientes (nombre, email, tipo_consulta, asunto, mensaje) VALUES (?, ?, ?, ?, ?)",
        (nombre, email, tipo_consulta, asunto, mensaje),
    )
    conn.commit()
    conn.close()


# ================= PROVEEDORES =================
def obtener_proveedores():
    conn = get_connection()
    filas = conn.execute("SELECT * FROM proveedores").fetchall()
    conn.close()
    return [dict(f) for f in filas]


def insertar_proveedor(nombre, producto, telefono, email):
    conn = get_connection()
    conn.execute(
        "INSERT INTO proveedores (nombre, producto, telefono, email) VALUES (?, ?, ?, ?)",
        (nombre, producto, telefono, email),
    )
    conn.commit()
    conn.close()


# ================= PEDIDOS / FACTURACIÓN =================
def obtener_pedidos():
    conn = get_connection()
    filas = conn.execute("SELECT * FROM pedidos").fetchall()
    conn.close()
    return [dict(f) for f in filas]


def insertar_pedido(cliente, producto, cantidad, total, estado, fecha, metodo_pago):
    conn = get_connection()
    conn.execute(
        "INSERT INTO pedidos (cliente, producto, cantidad, total, estado, fecha, metodo_pago) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (cliente, producto, cantidad, total, estado, fecha, metodo_pago),
    )
    conn.commit()
    conn.close()
