from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange


class RegistroForm(FlaskForm):
    """Formulario para que un visitante cree su cuenta de cliente."""

    nombre = StringField(
        "Nombre completo",
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(min=3, max=80, message="Debe tener entre 3 y 80 caracteres."),
        ],
    )

    email = StringField(
        "Correo electrónico",
        validators=[
            DataRequired(message="El correo es obligatorio."),
            Email(message="Ingresa un correo electrónico válido."),
        ],
    )

    password = PasswordField(
        "Contraseña",
        validators=[
            DataRequired(message="La contraseña es obligatoria."),
            Length(min=6, message="Debe tener al menos 6 caracteres."),
        ],
    )

    confirmar_password = PasswordField(
        "Confirmar contraseña",
        validators=[
            DataRequired(message="Confirma tu contraseña."),
            EqualTo("password", message="Las contraseñas no coinciden."),
        ],
    )

    enviar = SubmitField("Crear cuenta")


class LoginForm(FlaskForm):
    """Formulario de inicio de sesión."""

    email = StringField(
        "Correo electrónico",
        validators=[
            DataRequired(message="El correo es obligatorio."),
            Email(message="Ingresa un correo electrónico válido."),
        ],
    )

    password = PasswordField(
        "Contraseña",
        validators=[DataRequired(message="La contraseña es obligatoria.")],
    )

    enviar = SubmitField("Ingresar")


class CompraForm(FlaskForm):
    """
    Formulario de compra para usuarios normales ya autenticados.
    A diferencia de PedidoForm (uso administrativo), este NO pide el
    nombre del cliente: se toma automáticamente de la sesión (current_user).
    """

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

    enviar = SubmitField("Confirmar Compra")
