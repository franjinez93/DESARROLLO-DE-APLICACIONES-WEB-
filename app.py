from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    """Página principal: hero, quiénes somos y servicios."""
    return render_template("index.html")


@app.route("/productos")
def productos():
    """Tienda online: catálogo destacado, selección y carrito."""
    return render_template("productos.html")


@app.route("/clientes")
def clientes():
    """Registro / contacto de clientes."""
    return render_template("clientes.html")


@app.route("/proveedores")
def proveedores():
    """Registro de proveedores."""
    return render_template("proveedores.html")


@app.route("/facturacion")
def facturacion():
    """Panel de pedidos / facturación (visible tras login simulado)."""
    return render_template("facturacion.html")


if __name__ == "__main__":
    app.run(debug=True)