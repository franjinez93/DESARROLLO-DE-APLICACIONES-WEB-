import os
from datetime import date
from functools import wraps

from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, current_user
)
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Cargar variables de entorno ANTES de usarlas
load_dotenv()

from models import Usuario
from forms.producto_form import ProductoForm
from forms.cliente_form import ClienteForm
from forms.proveedor_form import ProveedorForm
from forms.facturacion_form import PedidoForm
from forms.login_form import LoginForm
from forms.usuario_form import RegistroForm, CompraForm
from conexion.conexion import obtener_conexion

import database

app = Flask(__name__)

# =========================================================
#  CONFIGURACIÓN DE SEGURIDAD
# =========================================================
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "clave-secreta-farmacia-central-2026")
app.config["WTF_CSRF_TIME_LIMIT"] = None

csrf = CSRFProtect(app)

# =========================================================
#  PERSISTENCIA DE DATOS
# =========================================================
database.init_db()

# =========================================================
#  LOGIN / SESIONES (Flask-Login)
# =========================================================
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Debes iniciar sesión para acceder a esta sección."
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    fila = database.obtener_usuario_por_id(int(user_id))
    if not fila:
        return None
    return Usuario(fila["id_usuario"], fila["nombre"], fila["email"], fila["rol"])


def admin_required(vista):
    """Decorador para rutas que solo puede ver el administrador."""
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Debes iniciar sesión para acceder a esta sección.", "warning")
            return redirect(url_for("login", next=request.path))
        if not current_user.is_admin:
            flash("No tienes permisos de administrador para acceder a esta sección.", "danger")
            return redirect(url_for("index"))
        return vista(*args, **kwargs)
    return envoltura


# =========================================================
#  DATOS ESTÁTICOS (para la página pública)
# =========================================================
NOMBRE_FARMACIA = "Farmacia Central"

INFO_FARMACIA = {
    "anios_experiencia": 20,
    "horario_semana": "7:00 - 21:00",
    "horario_finde": "8:00 - 18:00",
    "promocion": "15% de descuento en genéricos los martes",
    "envio_disponible": True,
}

SERVICIOS = [
    {"icono": "💊", "nombre": "Medicamentos", "resumen": "Genéricos y de marca con garantía de calidad y a precios accesibles.",
     "detalle": "Contamos con más de 500 presentaciones registradas en ARCSA, provenientes de laboratorios certificados.",
     "disponible": True},
    {"icono": "🌿", "nombre": "Naturales", "resumen": "Suplementos vitamínicos y productos naturales para tu bienestar.",
     "detalle": "Línea de fitoterapia y suplementación avalada por nutricionistas asociados.",
     "disponible": True},
    {"icono": "🧴", "nombre": "Cuidado Personal", "resumen": "Artículos de cuidado personal e higiene de las mejores marcas.",
     "detalle": "Dermocosmética, higiene bucal, cuidado capilar y productos hipoalergénicos.",
     "disponible": True},
    {"icono": "🩺", "nombre": "Equipos Médicos", "resumen": "Tensiómetros, glucómetros y equipos para uso doméstico.",
     "detalle": "Venta y asesoría en el uso correcto de equipos de monitoreo en casa.",
     "disponible": True},
    {"icono": "👨‍⚕️", "nombre": "Atención Farmacéutica", "resumen": "Asesoría personalizada de nuestros farmacéuticos certificados.",
     "detalle": "Control de presión arterial y glucosa sin costo para clientes frecuentes.",
     "disponible": True},
    {"icono": "🚚", "nombre": "Domicilio", "resumen": "Entregas a domicilio disponibles en toda la ciudad rápido y seguro.",
     "detalle": "Tiempo estimado de entrega: 45 a 90 minutos según la zona.",
     "disponible": False},
]

EQUIPO = [
    {"nombre": "Q.F. Edgar Jinez", "cargo": "Director Técnico", "icono": "👨‍⚕️",
     "descripcion": "Químico Farmacéutico responsable, 12 años de experiencia."},
    {"nombre": "Lic. Paola Andrade", "cargo": "Atención al Cliente", "icono": "🧑‍💼",
     "descripcion": "Encargada de la asesoría y seguimiento a clientes frecuentes."},
    {"nombre": "Sr. Kevin Ruiz", "cargo": "Logística y Domicilios", "icono": "🚴",
     "descripcion": "Coordina las entregas a domicilio en toda la ciudad."},
]

VALORES = [
    {"icono": "🤝", "titulo": "Confianza", "descripcion": "Construimos relaciones duraderas basadas en la honestidad."},
    {"icono": "⏱️", "titulo": "Rapidez", "descripcion": "Atención ágil, tanto en tienda como en pedidos a domicilio."},
    {"icono": "🎓", "titulo": "Profesionalismo", "descripcion": "Personal capacitado y en constante actualización."},
    {"icono": "❤️", "titulo": "Cercanía", "descripcion": "Trato humano y personalizado con cada paciente."},
]

MISION = ("Brindar productos y servicios farmacéuticos de calidad, accesibles y con atención humana, "
          "contribuyendo al bienestar de nuestra comunidad.")
VISION = ("Ser la farmacia de referencia en la ciudad, reconocida por su servicio, innovación y "
          "compromiso con la salud de las familias.")


def calcular_resumen_facturacion(pedidos):
    """Calcula estadísticas simples a partir de la lista de pedidos."""
    total_pedidos = len(pedidos)
    total_facturado = sum(float(p["total"]) for p in pedidos if p["total"])
    pendientes = sum(1 for p in pedidos if p["estado"] == "Pendiente")
    entregados = sum(1 for p in pedidos if p["estado"] in ("Completado", "Entregado"))
    cancelados = sum(1 for p in pedidos if p["estado"] == "Cancelado")
    return {
        "total_pedidos": total_pedidos,
        "total_facturado": total_facturado,
        "pendientes": pendientes,
        "entregados": entregados,
        "cancelados": cancelados,
    }


# =========================================================
#  RUTAS DE AUTENTICACIÓN
# =========================================================
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = RegistroForm()
    if form.validate_on_submit():
        existente = database.obtener_usuario_por_email(form.email.data)
        if existente:
            flash("Ya existe una cuenta registrada con ese correo.", "danger")
        else:
            database.crear_usuario(form.nombre.data, form.email.data, form.password.data, rol="cliente")
            flash(f"Cuenta creada correctamente, {form.nombre.data}. Ahora puedes iniciar sesión.", "success")
            return redirect(url_for("login"))

    return render_template("registro.html", nombre_farmacia=NOMBRE_FARMACIA, form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        fila = database.obtener_usuario_por_email(form.email.data)
        if fila and check_password_hash(fila["password_hash"], form.password.data):
            usuario = Usuario(fila["id_usuario"], fila["nombre"], fila["email"], fila["rol"])
            login_user(usuario)
            flash(f"Bienvenido, {usuario.nombre}.", "success")
            siguiente = request.args.get("next")
            return redirect(siguiente or url_for("dashboard"))
        flash("Correo o contraseña incorrectos.", "danger")

    return render_template("login.html", nombre_farmacia=NOMBRE_FARMACIA, form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", nombre_farmacia=NOMBRE_FARMACIA)


# =========================================================
#  RUTAS DE VISUALIZACIÓN PÚBLICA
# =========================================================
@app.route("/")
def index():
    return render_template("index.html", nombre_farmacia=NOMBRE_FARMACIA, info=INFO_FARMACIA, servicios=SERVICIOS)


@app.route("/nosotros")
def nosotros():
    return render_template("nosotros.html", nombre_farmacia=NOMBRE_FARMACIA, info=INFO_FARMACIA,
                           mision=MISION, vision=VISION, valores=VALORES, equipo=EQUIPO)


@app.route("/servicios")
def servicios():
    return render_template("servicios.html", nombre_farmacia=NOMBRE_FARMACIA, servicios=SERVICIOS)


# =========================================================
#  MÓDULO PRODUCTOS — CRUD COMPLETO (Semana 13 y 15)
# =========================================================
@app.route("/productos")
@login_required
def productos():
    """LISTAR productos (SELECT con JOIN a categorías)."""
    conexion = obtener_conexion()
    cursor = conexion.cursor(cursor_factory=RealDictCursor)
    sql = """
        SELECT p.id_producto, p.nombre, p.precio, p.stock, p.descripcion, p.icono,
               c.nombre AS categoria
        FROM productos p
        JOIN categorias c ON p.id_categoria = c.id_categoria
        ORDER BY p.nombre
    """
    cursor.execute(sql)
    lista_productos = cursor.fetchall()
    cursor.close()
    conexion.close()

    return render_template("Productos.html", nombre_farmacia=NOMBRE_FARMACIA, productos=lista_productos)


@app.route("/productos/nuevo", methods=["GET", "POST"])
@admin_required
def nuevo_producto():
    """CREAR producto (INSERT)."""
    form = ProductoForm()
    if form.validate_on_submit():
        database.insertar_producto(
            nombre=form.nombre.data,
            categoria=form.categoria.data,
            descripcion=form.descripcion.data,
            precio=float(form.precio.data),
            stock=form.stock.data,
            icono="💊",
        )
        flash(f"Producto '{form.nombre.data}' registrado correctamente.", "success")
        return redirect(url_for("productos"))

    return render_template(
        "formulario_producto.html",
        nombre_farmacia=NOMBRE_FARMACIA,
        titulo_formulario="Registrar Producto",
        form=form,
    )


@app.route("/productos/editar/<int:id_producto>", methods=["GET", "POST"])
@admin_required
def editar_producto(id_producto):
    """ACTUALIZAR producto (UPDATE)."""
    producto = database.obtener_producto_por_id(id_producto)
    if not producto:
        flash("Producto no encontrado.", "danger")
        return redirect(url_for("productos"))

    form = ProductoForm(data=producto)

    if form.validate_on_submit():
        database.actualizar_producto(
            id_producto=id_producto,
            nombre=form.nombre.data,
            categoria=form.categoria.data,
            descripcion=form.descripcion.data,
            precio=float(form.precio.data),
            stock=form.stock.data,
        )
        flash(f"Producto '{form.nombre.data}' actualizado correctamente.", "success")
        return redirect(url_for("productos"))

    return render_template(
        "formulario_producto.html",
        nombre_farmacia=NOMBRE_FARMACIA,
        titulo_formulario="Editar Producto",
        form=form,
        producto=producto,
    )


@app.route("/productos/eliminar/<int:id_producto>", methods=["POST"])
@admin_required
def eliminar_producto(id_producto):
    """ELIMINAR producto (DELETE)."""
    exito = database.eliminar_producto(id_producto)
    if exito:
        flash("Producto eliminado correctamente.", "success")
    else:
        flash("No se pudo eliminar el producto (puede tener pedidos asociados).", "danger")
    return redirect(url_for("productos"))


# =========================================================
#  MÓDULO CLIENTES — CRUD COMPLETO
# =========================================================
@app.route("/clientes")
@admin_required
def clientes():
    """LISTAR clientes con sus consultas (LEFT JOIN)."""
    conexion = obtener_conexion()
    cursor = conexion.cursor(cursor_factory=RealDictCursor)
    sql = """
        SELECT c.id_cliente, c.nombre, c.email,
               co.tipo_consulta, co.asunto, co.mensaje
        FROM clientes c
        LEFT JOIN consultas_clientes co ON c.id_cliente = co.id_cliente
        ORDER BY c.id_cliente DESC
    """
    cursor.execute(sql)
    lista_clientes = cursor.fetchall()
    cursor.close()
    conexion.close()

    return render_template("Clientes.html", nombre_farmacia=NOMBRE_FARMACIA, clientes=lista_clientes)


@app.route("/clientes/nuevo", methods=["GET", "POST"])
@admin_required
def nuevo_cliente():
    """CREAR cliente (INSERT)."""
    form = ClienteForm()
    if form.validate_on_submit():
        database.insertar_cliente(
            nombre=form.nombre.data,
            email=form.email.data,
            tipo_consulta=form.tipo_consulta.data,
            asunto=form.asunto.data,
            mensaje=form.mensaje.data,
        )
        flash(f"Cliente '{form.nombre.data}' registrado correctamente.", "success")
        return redirect(url_for("clientes"))

    return render_template("formulario_cliente.html", nombre_farmacia=NOMBRE_FARMACIA, form=form)


@app.route("/clientes/editar/<int:id_cliente>", methods=["GET", "POST"])
@admin_required
def editar_cliente(id_cliente):
    """ACTUALIZAR cliente (UPDATE)."""
    cliente = database.obtener_cliente_por_id(id_cliente)
    if not cliente:
        flash("Cliente no encontrado.", "danger")
        return redirect(url_for("clientes"))

    form = ClienteForm(data=cliente)

    # Rellenar valores por defecto si vienen vacíos
    if not form.tipo_consulta.data:
        form.tipo_consulta.data = "General"
    if not form.asunto.data:
        form.asunto.data = "Actualización de datos"
    if not form.mensaje.data:
        form.mensaje.data = "Actualización de datos del cliente."

    if form.validate_on_submit():
        database.actualizar_cliente(
            id_cliente=id_cliente,
            nombre=form.nombre.data,
            email=form.email.data,
        )
        flash(f"Cliente '{form.nombre.data}' actualizado correctamente.", "success")
        return redirect(url_for("clientes"))

    return render_template(
        "formulario_cliente.html",
        nombre_farmacia=NOMBRE_FARMACIA,
        form=form,
        cliente=cliente,
    )


@app.route("/clientes/eliminar/<int:id_cliente>", methods=["POST"])
@admin_required
def eliminar_cliente(id_cliente):
    """ELIMINAR cliente (DELETE)."""
    exito = database.eliminar_cliente(id_cliente)
    if exito:
        flash("Cliente eliminado correctamente.", "success")
    else:
        flash("No se pudo eliminar el cliente.", "danger")
    return redirect(url_for("clientes"))


# =========================================================
#  MÓDULO PROVEEDORES — CRUD COMPLETO
# =========================================================
@app.route("/proveedores")
@admin_required
def proveedores():
    """LISTAR proveedores."""
    conexion = obtener_conexion()
    cursor = conexion.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT id_proveedor, nombre, telefono, email FROM proveedores ORDER BY id_proveedor DESC")
    lista_proveedores = cursor.fetchall()
    cursor.close()
    conexion.close()

    return render_template("Proveedores.html", nombre_farmacia=NOMBRE_FARMACIA, proveedores=lista_proveedores)


@app.route("/proveedores/nuevo", methods=["GET", "POST"])
@admin_required
def nuevo_proveedor():
    """CREAR proveedor (INSERT)."""
    form = ProveedorForm()
    if form.validate_on_submit():
        database.insertar_proveedor(
            nombre=form.nombre.data,
            producto=form.producto.data,
            telefono=form.telefono.data,
            email=form.email.data,
        )
        flash(f"Proveedor '{form.nombre.data}' registrado correctamente.", "success")
        return redirect(url_for("proveedores"))

    return render_template("formulario_proveedor.html", nombre_farmacia=NOMBRE_FARMACIA, form=form)


@app.route("/proveedores/editar/<int:id_proveedor>", methods=["GET", "POST"])
@admin_required
def editar_proveedor(id_proveedor):
    """ACTUALIZAR proveedor (UPDATE)."""
    proveedor = database.obtener_proveedor_por_id(id_proveedor)
    if not proveedor:
        flash("Proveedor no encontrado.", "danger")
        return redirect(url_for("proveedores"))

    form = ProveedorForm(data=proveedor)

    if form.validate_on_submit():
        database.actualizar_proveedor(
            id_proveedor=id_proveedor,
            nombre=form.nombre.data,
            telefono=form.telefono.data,
            email=form.email.data,
        )
        flash(f"Proveedor '{form.nombre.data}' actualizado correctamente.", "success")
        return redirect(url_for("proveedores"))

    return render_template(
        "formulario_proveedor.html",
        nombre_farmacia=NOMBRE_FARMACIA,
        form=form,
        proveedor=proveedor,
    )


@app.route("/proveedores/eliminar/<int:id_proveedor>", methods=["POST"])
@admin_required
def eliminar_proveedor(id_proveedor):
    """ELIMINAR proveedor (DELETE)."""
    exito = database.eliminar_proveedor(id_proveedor)
    if exito:
        flash("Proveedor eliminado correctamente.", "success")
    else:
        flash("No se pudo eliminar el proveedor.", "danger")
    return redirect(url_for("proveedores"))


# =========================================================
#  MÓDULO FACTURACIÓN (solo admin)
# =========================================================
@app.route("/facturacion")
@admin_required
def facturacion():
    """LISTAR pedidos con JOIN a clientes, productos y detalle."""
    conexion = obtener_conexion()
    cursor = conexion.cursor(cursor_factory=RealDictCursor)
    sql = """
        SELECT p.id_pedido, c.nombre AS cliente, pr.nombre AS producto,
               dp.cantidad, p.fecha, p.estado, p.metodo_pago, p.total
        FROM pedidos p
        JOIN clientes c ON p.id_cliente = c.id_cliente
        LEFT JOIN detalle_pedidos dp ON p.id_pedido = dp.id_pedido
        LEFT JOIN productos pr ON dp.id_producto = pr.id_producto
        ORDER BY p.id_pedido DESC
    """
    cursor.execute(sql)
    lista_pedidos = cursor.fetchall()
    cursor.close()
    conexion.close()

    resumen = calcular_resumen_facturacion(lista_pedidos)
    return render_template("Facturacion.html", nombre_farmacia=NOMBRE_FARMACIA,
                           pedidos=lista_pedidos, resumen=resumen)


@app.route("/facturacion/nuevo", methods=["GET", "POST"])
@admin_required
def nuevo_pedido():
    """Registro MANUAL de pedidos (INSERT)."""
    form = PedidoForm()
    conexion = obtener_conexion()
    cursor = conexion.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT nombre, precio FROM productos")
    productos_bd = cursor.fetchall()
    cursor.close()
    conexion.close()

    form.producto.choices = [(p["nombre"], p["nombre"]) for p in productos_bd]

    if form.validate_on_submit():
        producto_info = next((p for p in productos_bd if p["nombre"] == form.producto.data), None)
        precio_unitario = float(producto_info["precio"]) if producto_info else 0
        total = round(precio_unitario * form.cantidad.data, 2)

        database.insertar_pedido(
            cliente=form.cliente.data,
            producto=form.producto.data,
            cantidad=form.cantidad.data,
            total=total,
            estado="Pendiente",
            fecha=date.today().isoformat(),
            metodo_pago=form.metodo_pago.data,
        )
        flash(f"Pedido de '{form.cliente.data}' registrado correctamente.", "success")
        return redirect(url_for("facturacion"))

    return render_template("formulario_facturacion.html", nombre_farmacia=NOMBRE_FARMACIA, form=form)


# =========================================================
#  COMPRA (usuarios autenticados)
# =========================================================
@app.route("/comprar", methods=["GET", "POST"])
@login_required
def comprar():
    """Compra de un solo producto (formulario tradicional)."""
    form = CompraForm()
    conexion = obtener_conexion()
    cursor = conexion.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT nombre, precio FROM productos WHERE stock > 0")
    productos_bd = cursor.fetchall()
    cursor.close()
    conexion.close()

    form.producto.choices = [(p["nombre"], p["nombre"]) for p in productos_bd]

    if form.validate_on_submit():
        producto_info = next((p for p in productos_bd if p["nombre"] == form.producto.data), None)
        precio_unitario = float(producto_info["precio"]) if producto_info else 0
        total = round(precio_unitario * form.cantidad.data, 2)

        database.insertar_pedido(
            cliente=current_user.nombre,
            producto=form.producto.data,
            cantidad=form.cantidad.data,
            total=total,
            estado="Pendiente",
            fecha=date.today().isoformat(),
            metodo_pago=form.metodo_pago.data,
            email_cliente=current_user.email,
        )
        flash("¡Compra registrada correctamente! Pronto la procesaremos.", "success")
        return redirect(url_for("productos"))

    return render_template("comprar.html", nombre_farmacia=NOMBRE_FARMACIA, form=form)


@app.route("/carrito/confirmar", methods=["POST"])
@login_required
def confirmar_carrito():
    """Recibe el carrito (JSON) y registra un pedido por cada ítem."""
    datos = request.get_json(silent=True) or {}
    items = datos.get("items", [])
    metodo_pago = datos.get("metodo_pago", "Efectivo")

    if not items:
        return jsonify({"ok": False, "mensaje": "El carrito está vacío."}), 400

    conexion = obtener_conexion()
    cursor = conexion.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT nombre, precio, stock FROM productos")
    productos_bd = {p["nombre"]: p for p in cursor.fetchall()}
    cursor.close()
    conexion.close()

    errores = []
    registrados = 0
    for item in items:
        nombre = (item.get("nombre") or "").strip()
        try:
            cantidad = int(item.get("cantidad", 0))
        except (TypeError, ValueError):
            cantidad = 0

        info = productos_bd.get(nombre)
        if not info or cantidad < 1:
            errores.append(f"'{nombre}' ya no está disponible.")
            continue
        if cantidad > info["stock"]:
            errores.append(f"Stock insuficiente para '{nombre}'.")
            continue

        total = round(float(info["precio"]) * cantidad, 2)
        database.insertar_pedido(
            cliente=current_user.nombre,
            producto=nombre,
            cantidad=cantidad,
            total=total,
            estado="Pendiente",
            fecha=date.today().isoformat(),
            metodo_pago=metodo_pago,
            email_cliente=current_user.email,
        )
        registrados += 1

    if errores and registrados == 0:
        return jsonify({"ok": False, "mensaje": " ".join(errores)}), 400

    mensaje = "¡Compra registrada correctamente!"
    if errores:
        mensaje += " (Algunos productos no se pudieron procesar: " + " ".join(errores) + ")"

    return jsonify({"ok": True, "mensaje": mensaje})


if __name__ == "__main__":
    app.run(debug=True)