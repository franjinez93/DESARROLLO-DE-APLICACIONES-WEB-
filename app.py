from flask import Flask, render_template, redirect, url_for, flash

from forms.producto_form import ProductoForm
from forms.cliente_form import ClienteForm
from forms.proveedor_form import ProveedorForm
from forms.facturacion_form import PedidoForm

app = Flask(__name__)

# =========================================================
#  CONFIGURACIÓN DE SEGURIDAD (Semana 11)
#  La SECRET_KEY es obligatoria para que Flask-WTF pueda
#  generar y verificar los tokens de protección CSRF.
# =========================================================
app.config["SECRET_KEY"] = "clave-secreta-farmacia-central-2026"

# =========================================================
#  DATOS DE EJEMPLO (temporales, sin base de datos - Semana 10)
#  Se mantienen íntegros los datos y estructuras desarrolladas
#  en la semana anterior.
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

PRODUCTOS_DESTACADOS = [
    {"nombre": "Paracetamol 500mg", "categoria": "Medicamentos", "precio": 2.50, "stock": 25,
     "icono": "💊", "descripcion": "Analgésico y antipirético de uso común."},
    {"nombre": "Ibuprofeno 400mg", "categoria": "Medicamentos", "precio": 3.20, "stock": 0,
     "icono": "💊", "descripcion": "Antiinflamatorio no esteroideo."},
    {"nombre": "Vitamina C 1000mg", "categoria": "Naturales", "precio": 5.75, "stock": 40,
     "icono": "🌿", "descripcion": "Suplemento para reforzar el sistema inmune."},
    {"nombre": "Alcohol Antiséptico", "categoria": "Cuidado Personal", "precio": 1.80, "stock": 15,
     "icono": "🧴", "descripcion": "Desinfectante de uso tópico."},
    {"nombre": "Tensiómetro Digital", "categoria": "Equipos Médicos", "precio": 28.99, "stock": 0,
     "icono": "🩺", "descripcion": "Medición de presión arterial en casa."},
    {"nombre": "Guantes de Nitrilo (Caja)", "categoria": "Cuidado Personal", "precio": 6.50, "stock": 30,
     "icono": "🧴", "descripcion": "Caja de 100 unidades, uso médico y doméstico."},
]

PROVEEDORES = [
    {"nombre": "Distribuidora FarmaEcuador", "producto": "Medicamentos genéricos",
     "telefono": "0991234567", "email": "ventas@farmaecuador.com"},
    {"nombre": "NaturLife S.A.", "producto": "Suplementos naturales",
     "telefono": "0987654321", "email": "contacto@naturlife.com"},
]

PEDIDOS = [
    {"cliente": "María Pérez", "producto": "Paracetamol 500mg", "cantidad": 2, "total": 5.00,
     "estado": "Entregado", "fecha": "2026-08-10", "metodo_pago": "Efectivo"},
    {"cliente": "Juan Torres", "producto": "Vitamina C 1000mg", "cantidad": 1, "total": 5.75,
     "estado": "Pendiente", "fecha": "2026-08-15", "metodo_pago": "Tarjeta"},
    {"cliente": "Ana Suárez", "producto": "Tensiómetro Digital", "cantidad": 1, "total": 28.99,
     "estado": "Cancelado", "fecha": "2026-08-16", "metodo_pago": "Transferencia"},
    {"cliente": "Luis Andrade", "producto": "Guantes de Nitrilo (Caja)", "cantidad": 3, "total": 19.50,
     "estado": "Entregado", "fecha": "2026-08-18", "metodo_pago": "Tarjeta"},
    {"cliente": "Sofía Mendoza", "producto": "Alcohol Antiséptico", "cantidad": 4, "total": 7.20,
     "estado": "Pendiente", "fecha": "2026-08-20", "metodo_pago": "Efectivo"},
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
    total_facturado = sum(p["total"] for p in pedidos)
    pendientes = sum(1 for p in pedidos if p["estado"] == "Pendiente")
    entregados = sum(1 for p in pedidos if p["estado"] == "Entregado")
    cancelados = sum(1 for p in pedidos if p["estado"] == "Cancelado")
    return {
        "total_pedidos": total_pedidos,
        "total_facturado": total_facturado,
        "pendientes": pendientes,
        "entregados": entregados,
        "cancelados": cancelados,
    }


# =========================================================
#  RUTAS EXISTENTES (Semana 10) - Se mantienen sin cambios
# =========================================================

@app.route("/")
def index():
    """Página principal: hero, resumen de nosotros y servicios."""
    return render_template(
        "index.html",
        nombre_farmacia=NOMBRE_FARMACIA,
        info=INFO_FARMACIA,
        servicios=SERVICIOS,
    )


@app.route("/nosotros")
def nosotros():
    """Quiénes somos: misión, visión, valores y equipo."""
    return render_template(
        "nosotros.html",
        nombre_farmacia=NOMBRE_FARMACIA,
        info=INFO_FARMACIA,
        mision=MISION,
        vision=VISION,
        valores=VALORES,
        equipo=EQUIPO,
    )


@app.route("/servicios")
def servicios():
    """Detalle de todos los servicios que ofrece la farmacia."""
    return render_template(
        "servicios.html",
        nombre_farmacia=NOMBRE_FARMACIA,
        servicios=SERVICIOS,
    )


@app.route("/productos")
def productos():
    """Tienda online: catálogo destacado, selección y carrito."""
    return render_template(
        "Productos.html",
        nombre_farmacia=NOMBRE_FARMACIA,
        productos=PRODUCTOS_DESTACADOS,
    )


@app.route("/clientes")
def clientes():
    """Registro / contacto de clientes (vista de información de contacto)."""
    return render_template("Clientes.html", nombre_farmacia=NOMBRE_FARMACIA)


@app.route("/proveedores")
def proveedores():
    """Listado de proveedores registrados."""
    return render_template(
        "Proveedores.html",
        nombre_farmacia=NOMBRE_FARMACIA,
        proveedores=PROVEEDORES,
    )


@app.route("/facturacion")
def facturacion():
    """Panel de pedidos / facturación (visible tras login simulado)."""
    resumen = calcular_resumen_facturacion(PEDIDOS)
    return render_template(
        "Facturacion.html",
        nombre_farmacia=NOMBRE_FARMACIA,
        pedidos=PEDIDOS,
        resumen=resumen,
    )


# =========================================================
#  RUTAS NUEVAS (Semana 11) - Formularios con Flask-WTF
#  Cada ruta acepta GET (mostrar el formulario) y POST
#  (procesar los datos). Los datos solo se procesan cuando
#  form.validate_on_submit() retorna True.
# =========================================================

@app.route("/productos/nuevo", methods=["GET", "POST"])
def nuevo_producto():
    """Registro de un nuevo producto mediante ProductoForm."""
    form = ProductoForm()

    if form.validate_on_submit():
        nuevo = {
            "nombre": form.nombre.data,
            "categoria": form.categoria.data,
            "descripcion": form.descripcion.data,
            "precio": float(form.precio.data),
            "stock": form.stock.data,
            "icono": "💊",
        }
        PRODUCTOS_DESTACADOS.append(nuevo)
        flash(f"Producto '{nuevo['nombre']}' registrado correctamente.", "success")
        return redirect(url_for("productos"))

    return render_template(
        "formulario_producto.html",
        nombre_farmacia=NOMBRE_FARMACIA,
        titulo_formulario="Registrar Producto",
        form=form,
    )


@app.route("/clientes/nuevo", methods=["GET", "POST"])
def nuevo_cliente():
    """Formulario de contacto de clientes mediante ClienteForm."""
    form = ClienteForm()

    if form.validate_on_submit():
        flash(f"Gracias {form.nombre.data}, hemos recibido tu consulta.", "success")
        return redirect(url_for("clientes"))

    return render_template(
        "formulario_cliente.html",
        nombre_farmacia=NOMBRE_FARMACIA,
        form=form,
    )


@app.route("/proveedores/nuevo", methods=["GET", "POST"])
def nuevo_proveedor():
    """Registro de un nuevo proveedor mediante ProveedorForm."""
    form = ProveedorForm()

    if form.validate_on_submit():
        nuevo = {
            "nombre": form.nombre.data,
            "producto": form.producto.data,
            "telefono": form.telefono.data,
            "email": form.email.data,
        }
        PROVEEDORES.append(nuevo)
        flash(f"Proveedor '{nuevo['nombre']}' registrado correctamente.", "success")
        return redirect(url_for("proveedores"))

    return render_template(
        "formulario_proveedor.html",
        nombre_farmacia=NOMBRE_FARMACIA,
        form=form,
    )


@app.route("/facturacion/nuevo", methods=["GET", "POST"])
def nuevo_pedido():
    """Registro manual de un nuevo pedido mediante PedidoForm."""
    form = PedidoForm()
    # Las opciones del SelectField se cargan dinámicamente desde el catálogo.
    form.producto.choices = [(p["nombre"], p["nombre"]) for p in PRODUCTOS_DESTACADOS]

    if form.validate_on_submit():
        producto_info = next(
            (p for p in PRODUCTOS_DESTACADOS if p["nombre"] == form.producto.data), None
        )
        precio_unitario = producto_info["precio"] if producto_info else 0
        nuevo = {
            "cliente": form.cliente.data,
            "producto": form.producto.data,
            "cantidad": form.cantidad.data,
            "total": round(precio_unitario * form.cantidad.data, 2),
            "estado": "Pendiente",
            "fecha": "2026-08-28",
            "metodo_pago": form.metodo_pago.data,
        }
        PEDIDOS.append(nuevo)
        flash(f"Pedido de '{nuevo['cliente']}' registrado correctamente.", "success")
        return redirect(url_for("facturacion"))

    return render_template(
        "formulario_facturacion.html",
        nombre_farmacia=NOMBRE_FARMACIA,
        form=form,
    )


if __name__ == "__main__":
    app.run(debug=True)
