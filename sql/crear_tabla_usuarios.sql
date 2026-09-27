-- ============================================================
--  Tabla de USUARIOS (login / registro / roles)
--  Ejecuta esto en pgAdmin4 -> Query Tool, sobre la base farmacia_central
-- ============================================================

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario      SERIAL PRIMARY KEY,
    nombre          VARCHAR(80)  NOT NULL,
    email           VARCHAR(120) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    rol             VARCHAR(20)  NOT NULL DEFAULT 'cliente'
                    CHECK (rol IN ('admin', 'cliente')),
    fecha_registro  TIMESTAMP    NOT NULL DEFAULT NOW()
);

-- NOTA: no insertes usuarios directamente aquí con INSERT normal,
-- porque la contraseña debe quedar encriptada con el mismo algoritmo
-- que usa Flask (Werkzeug). Para crear tu primer administrador,
-- usa el script "crear_admin.py" que se incluye junto a este archivo.
