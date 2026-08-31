from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, DecimalField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange


class ProductoForm(FlaskForm):
    """
    Formulario para registrar o editar un producto del catálogo.
    Se reutiliza tanto para el alta (registro) como para la edición
    de un producto, ya que WTForms permite precargar los valores
    mediante 'obj=' o pasando los datos existentes al instanciar.
    """

    nombre = StringField(
        "Nombre del producto",
        validators=[
            DataRequired(message="El nombre del producto es obligatorio."),
            Length(min=3, max=80, message="El nombre debe tener entre 3 y 80 caracteres."),
        ],
    )

    categoria = SelectField(
        "Categoría",
        choices=[
            ("", "-- Selecciona categoría --"),
            ("Medicamentos", "💊 Medicamentos"),
            ("Naturales", "🌿 Naturales y Suplementos"),
            ("Cuidado Personal", "🧴 Cuidado Personal"),
            ("Equipos Médicos", "🩺 Equipos Médicos"),
        ],
        validators=[DataRequired(message="Selecciona una categoría.")],
    )

    descripcion = TextAreaField(
        "Descripción",
        validators=[
            DataRequired(message="La descripción es obligatoria."),
            Length(max=200, message="Máximo 200 caracteres."),
        ],
    )

    precio = DecimalField(
        "Precio ($)",
        places=2,
        validators=[
            DataRequired(message="El precio es obligatorio."),
            NumberRange(min=0.01, message="El precio debe ser mayor a 0."),
        ],
    )

    stock = IntegerField(
        "Stock disponible",
        validators=[
            DataRequired(message="El stock es obligatorio."),
            NumberRange(min=0, max=9999, message="Ingresa un stock válido (0 - 9999)."),
        ],
    )

    enviar = SubmitField("Guardar Producto")
