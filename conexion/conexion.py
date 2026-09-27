import os
import psycopg2
from dotenv import load_dotenv

# Carga las variables definidas en el archivo .env (en la raíz del proyecto).
# Así, host/usuario/contraseña de PostgreSQL NUNCA quedan escritos
# directamente en el código fuente que se sube a GitHub.
load_dotenv()


def obtener_conexion():
    """
    Abre una conexión a la base de datos 'farmacia_central' en PostgreSQL,
    usando las credenciales del archivo .env (que NO se sube al repositorio).

    IMPORTANTE:
    - Copia .env.example a .env y coloca ahí tus credenciales reales.
    - .env está en .gitignore: nunca debe subirse a un repositorio público.
    """
    conexion = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "farmacia_central"),
        port=os.getenv("DB_PORT", "5432"),
    )
    return conexion
