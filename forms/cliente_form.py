from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email


class ClienteForm(FlaskForm):
    """
    Formulario de contacto / registro de clientes.
    Permite capturar los datos de consulta enviados por el cliente
    y validarlos del lado del servidor antes de procesarlos.
    """

    nombre = StringField(
        "Nombre",
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(min=3, max=60, message="El nombre debe tener entre 3 y 60 caracteres."),
        ],
    )

    email = StringField(
        "Email",
        validators=[
            DataRequired(message="El correo es obligatorio."),
            Email(message="Ingresa un correo electrónico válido."),
        ],
    )

    tipo_consulta = SelectField(
        "Tipo de consulta",
        choices=[
            ("", "-- Selecciona --"),
            ("General", "Consulta General"),
            ("Soporte", "Soporte Técnico"),
        ],
        validators=[DataRequired(message="Selecciona un tipo de consulta.")],
    )

    asunto = StringField(
        "Asunto",
        validators=[
            DataRequired(message="El asunto es obligatorio."),
            Length(min=3, max=100, message="El asunto debe tener entre 3 y 100 caracteres."),
        ],
    )

    mensaje = TextAreaField(
        "Mensaje",
        validators=[
            DataRequired(message="El mensaje es obligatorio."),
            Length(min=10, max=500, message="El mensaje debe tener entre 10 y 500 caracteres."),
        ],
    )

    enviar = SubmitField("Enviar Mensaje")
