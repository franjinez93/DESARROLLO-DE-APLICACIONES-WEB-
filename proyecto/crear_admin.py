"""
crear_admin.py
--------------
Script de UN SOLO USO para crear el primer usuario administrador.
Ejecútalo una vez desde la raíz de tu proyecto Flask:

    python crear_admin.py

Te pedirá nombre, correo y contraseña, y guardará la contraseña ya
encriptada (hash) en la tabla 'usuarios' de PostgreSQL, con rol='admin'.

Requisito previo: haber ejecutado sql/crear_tabla_usuarios.sql en pgAdmin4.
"""

from werkzeug.security import generate_password_hash
from conexion.conexion import obtener_conexion

nombre = input("Nombre del administrador: ").strip()
email = input("Email del administrador: ").strip().lower()
password = input("Contraseña: ").strip()

if not nombre or not email or not password:
    print("❌ Todos los campos son obligatorios. Intenta de nuevo.")
    raise SystemExit(1)

password_hash = generate_password_hash(password)

conexion = obtener_conexion()
cursor = conexion.cursor()
try:
    cursor.execute(
        "INSERT INTO usuarios (nombre, email, password_hash, rol) VALUES (%s, %s, %s, 'admin')",
        (nombre, email, password_hash),
    )
    conexion.commit()
    print(f"✅ Usuario administrador '{email}' creado correctamente.")
except Exception as error:
    conexion.rollback()
    print("❌ No se pudo crear el usuario:", error)
finally:
    cursor.close()
    conexion.close()
