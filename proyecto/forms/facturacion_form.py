from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange


class PedidoForm(FlaskForm):
    """
    Formulario de registro manual de pedidos para el panel de facturación.
    El campo 'producto' se llena dinámicamente en la ruta con el
    catálogo de productos disponibles.
    """

    cliente = StringField(
        "Cliente",
        validators=[
            DataRequired(message="El nombre del cliente es obligatorio."),
            Length(min=3, max=80, message="Ingresa al menos 3 caracteres."),
        ],
    )

    producto = SelectField(
        "Producto",
        validators=[DataRequired(message="Selecciona un producto.")],
    )

    cantidad = IntegerField(
        "Cantidad",
        validators=[
            DataRequired(message="La cantidad es obligatoria."),
            NumberRange(min=1, max=99, message="La cantidad debe estar entre 1 y 99."),
        ],
    )

    metodo_pago = SelectField(
        "Método de pago",
        choices=[
            ("Efectivo", "Efectivo"),
            ("Tarjeta", "Tarjeta"),
            ("Transferencia", "Transferencia"),
        ],
        validators=[DataRequired(message="Selecciona un método de pago.")],
    )

    enviar = SubmitField("Registrar Pedido")
