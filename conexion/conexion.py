import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def obtener_conexion():
    """
    Devuelve una conexión nueva a PostgreSQL.
    Prioriza DATABASE_URL (Render) sobre credenciales individuales (local).
    """
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        # Render entrega postgres://, pero psycopg2 requiere postgresql://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(database_url, sslmode="require")

    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "farmacia_central"),
        port=os.getenv("DB_PORT", "5432"),
    )