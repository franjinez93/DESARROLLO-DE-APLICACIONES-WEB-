from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, Optional


class ProveedorForm(FlaskForm):
    """
    Formulario para el registro o edición de un proveedor.
    El teléfono y el email son opcionales, pero si se ingresan
    deben cumplir un formato válido.
    """

    nombre = StringField(
        "Nombre / Empresa",
        validators=[
            DataRequired(message="El nombre o empresa es obligatorio."),
            Length(min=3, max=80, message="Debe tener entre 3 y 80 caracteres."),
        ],
    )

    producto = StringField(
        "Producto que provee",
        validators=[
            DataRequired(message="Indica el producto que provee."),
            Length(min=3, max=100, message="Debe tener entre 3 y 100 caracteres."),
        ],
    )

    telefono = StringField(
        "Teléfono",
        validators=[
            Optional(),
            Regexp(r"^\d{7,10}$", message="Ingresa un teléfono válido (7 a 10 dígitos)."),
        ],
    )

    email = StringField(
        "Email",
        validators=[
            Optional(),
            Email(message="Ingresa un correo electrónico válido."),
        ],
    )

    enviar = SubmitField("Registrar Proveedor")
