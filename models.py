"""
models.py
Modelo de datos de Usuario, usado por Flask-Login para representar
al usuario autenticado dentro de la sesión.
"""

from flask_login import UserMixin


class Usuario(UserMixin):
    """
    Envoltorio compatible con Flask-Login (UserMixin) alrededor de la
    fila 'usuarios' de PostgreSQL. No contiene el password_hash: eso
    solo se usa una vez, al validar el login (ver database.py y app.py).
    """

    def __init__(self, id_usuario, nombre, email, rol):
        self.id = id_usuario
        self.nombre = nombre
        self.email = email
        self.rol = rol

    @property
    def is_admin(self):
        return self.rol == "admin"
