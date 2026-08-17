# importar flask
from flask import Flask, render_template, request, redirect, url_for

# crear una instancia de la aplicación Flask
app = Flask(__name__)

# definir las rutas de la aplicación principal
@app.route('/')
def home():
    # Flask leerá 'index.html' y automáticamente procesará todos los
    # {% include 'includes/archivo.html' %} uniendo tu página completa.
    return render_template('index.html')

# ruta de productos (si decides tener una vista separada para esto)
@app.route('/productos')
def productos():
    return render_template('productos.html')

# ruta de clientes (si decides tener una vista separada para esto)
@app.route('/clientes')
def clientes():
    return render_template('clientes.html')

if __name__ == '__main__':
    app.run(debug=True)