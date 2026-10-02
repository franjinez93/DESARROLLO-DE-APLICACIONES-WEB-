"""
database.py
Funciones de acceso a datos contra PostgreSQL (base 'farmacia_central').

Incluye:
  - Usuarios (login, registro) vinculados a clientes por FK (id_cliente)
  - Productos: CRUD completo
  - Clientes: CRUD completo con borrado en cascada
  - Proveedores: CRUD completo
  - Pedidos: inserción con detalle y actualización de stock
"""

from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash
from conexion.conexion import obtener_conexion


def init_db():
    """Verifica que la conexión a PostgreSQL funcione."""
    try:
        conexion = obtener_conexion()
        conexion.close()
        print("Conexión a PostgreSQL (farmacia_central) verificada correctamente.")
    except Exception as error:
        print("No se pudo conectar a PostgreSQL:", error)


# =========================================================
#  USUARIOS (con FK opcional a clientes)
# =========================================================
def obtener_usuario_por_email(email):
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
    Crea un usuario nuevo. Si el rol es 'cliente':
      - Busca o crea su fila en la tabla clientes (por email)
      - Vincula usuarios.id_cliente con la FK
    Los admins se crean con id_cliente = NULL.
    """
    password_hash = generate_password_hash(password_plano)
    email_limpio = email.strip().lower()

    conexion = obtener_conexion()
    cursor = conexion.cursor(cursor_factory=RealDictCursor)
    try:
        id_cliente = None

        if rol == "cliente":
            # Buscar si ya existe el cliente con ese email
            cursor.execute(
                "SELECT id_cliente FROM clientes WHERE email = %s",
                (email_limpio,),
            )
            fila = cursor.fetchone()
            if fila:
                id_cliente = fila["id_cliente"]
            else:
                # Crear la fila en clientes
                cursor.execute(
                    "INSERT INTO clientes (nombre, email) VALUES (%s, %s) RETURNING id_cliente",
                    (nombre.strip(), email_limpio),
                )
                id_cliente = cursor.fetchone()["id_cliente"]

        cursor.execute(
            """
            INSERT INTO usuarios (nombre, email, password_hash, rol, id_cliente)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_usuario
            """,
            (nombre.strip(), email_limpio, password_hash, rol, id_cliente),
        )
        id_usuario = cursor.fetchone()["id_usuario"]
        conexion.commit()
        return id_usuario
    finally:
        cursor.close()
        conexion.close()


# =========================================================
#  PRODUCTOS - CRUD COMPLETO
# =========================================================
def _obtener_o_crear_categoria(cursor, nombre_categoria):
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


def obtener_producto_por_id(id_producto):
    """SELECT de un producto por su PK (para cargar el formulario de edición)."""
    conexion = obtener_conexion()
    cursor = conexion.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            """
            SELECT p.id_producto, p.nombre, p.precio, p.stock, p.descripcion,
                   p.icono, c.nombre AS categoria
            FROM productos p
            JOIN categorias c ON p.id_categoria = c.id_categoria
            WHERE p.id_producto = %s
            """,
            (id_producto,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conexion.close()


def actualizar_producto(id_producto, nombre, categoria, descripcion, precio, stock):
    """UPDATE parametrizado con WHERE por PK."""
    conexion = obtener_conexion()
    cursor = conexion.cursor(cursor_factory=RealDictCursor)
    try:
        id_categoria = _obtener_o_crear_categoria(cursor, categoria)
        cursor.execute(
            """
            UPDATE productos
            SET nombre = %s,
                id_categoria = %s,
                descripcion = %s,
                precio = %s,
                stock = %s
            WHERE id_producto = %s
            """,
            (nombre, id_categoria, descripcion, precio, stock, id_producto),
        )
        conexion.commit()
    finally:
        cursor.close()
        conexion.close()


def eliminar_producto(id_producto):
    """
    DELETE parametrizado con WHERE por PK.
    Devuelve True si eliminó, False si hubo error (FK en uso).
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id_producto,))
        conexion.commit()
        return cursor.rowcount > 0
    except Exception as error:
        conexion.rollback()
        print("Error al eliminar producto:", error)
        return False
    finally:
        cursor.close()
        conexion.close()


# =========================================================
#  CLIENTES - CRUD COMPLETO
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


def obtener_cliente_por_id(id_cliente):
    conexion = obtener_conexion()
    cursor = conexion.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            "SELECT id_cliente, nombre, email FROM clientes WHERE id_cliente = %s",
            (id_cliente,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conexion.close()


def actualizar_cliente(id_cliente, nombre, email):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute(
            "UPDATE clientes SET nombre = %s, email = %s WHERE id_cliente = %s",
            (nombre, email, id_cliente),
        )
        conexion.commit()
    finally:
        cursor.close()
        conexion.close()


def eliminar_cliente(id_cliente):
    """
    DELETE con cascada:
      1. Borra detalle_pedidos de los pedidos del cliente
      2. Borra pedidos del cliente
      3. Borra consultas_clientes del cliente
      4. Borra el cliente
      5. PostgreSQL borra AUTOMÁTICAMENTE los usuarios asociados
         (FK usuarios.id_cliente → clientes.id_cliente con ON DELETE CASCADE)

    Si aún no agregaste la FK a la BD, esta función también funciona
    porque fuerza el DELETE de usuarios huérfanos por email.
    """
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        # 1. Detalles de pedidos del cliente
        cursor.execute("""
            DELETE FROM detalle_pedidos
            WHERE id_pedido IN (SELECT id_pedido FROM pedidos WHERE id_cliente = %s)
        """, (id_cliente,))

        # 2. Pedidos del cliente
        cursor.execute("DELETE FROM pedidos WHERE id_cliente = %s", (id_cliente,))

        # 3. Consultas del cliente
        cursor.execute("DELETE FROM consultas_clientes WHERE id_cliente = %s", (id_cliente,))

        # 4. Cliente (PostgreSQL borra usuarios en cascada SI la FK existe)
        cursor.execute("DELETE FROM clientes WHERE id_cliente = %s", (id_cliente,))

        conexion.commit()
        print(f"✅ Cliente {id_cliente} eliminado correctamente (con cascada).")
        return cursor.rowcount > 0
    except Exception as error:
        conexion.rollback()
        print(f"❌ Error al eliminar cliente {id_cliente}: {error}")
        return False
    finally:
        cursor.close()
        conexion.close()


# =========================================================
#  PROVEEDORES - CRUD COMPLETO
# =========================================================
def insertar_proveedor(nombre, producto, telefono, email):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute(
            "INSERT INTO proveedores (nombre, telefono, email) VALUES (%s, %s, %s)",
            (nombre, telefono, email),
        )
        conexion.commit()
    finally:
        cursor.close()
        conexion.close()


def obtener_proveedor_por_id(id_proveedor):
    conexion = obtener_conexion()
    cursor = conexion.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            "SELECT id_proveedor, nombre, telefono, email FROM proveedores WHERE id_proveedor = %s",
            (id_proveedor,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conexion.close()


def actualizar_proveedor(id_proveedor, nombre, telefono, email):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute(
            "UPDATE proveedores SET nombre = %s, telefono = %s, email = %s WHERE id_proveedor = %s",
            (nombre, telefono, email, id_proveedor),
        )
        conexion.commit()
    finally:
        cursor.close()
        conexion.close()


def eliminar_proveedor(id_proveedor):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        # Desvincula productos que lo referencian
        cursor.execute(
            "UPDATE productos SET id_proveedor = NULL WHERE id_proveedor = %s",
            (id_proveedor,),
        )
        cursor.execute("DELETE FROM proveedores WHERE id_proveedor = %s", (id_proveedor,))
        conexion.commit()
        return cursor.rowcount > 0
    except Exception as error:
        conexion.rollback()
        print("Error al eliminar proveedor:", error)
        return False
    finally:
        cursor.close()
        conexion.close()


# =========================================================
#  PEDIDOS
# =========================================================
def _obtener_id_cliente_por_nombre(cursor, nombre_cliente):
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

        # Descuenta el stock vendido (sin bajar de 0)
        cursor.execute(
            "UPDATE productos SET stock = GREATEST(stock - %s, 0) WHERE id_producto = %s",
            (cantidad, id_producto),
        )

        conexion.commit()
    finally:
        cursor.close()
        conexion.close()