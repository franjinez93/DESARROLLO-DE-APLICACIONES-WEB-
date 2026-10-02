-- =========================================================
-- Esquema relacional Normalizado (3FN) - Farmacia Central
-- Motor: PostgreSQL
-- Incluye: tabla 'usuarios' para autenticación (Semana 14)
-- =========================================================

-- 1. ELIMINACIÓN DE TABLAS (En orden inverso a las dependencias)
DROP TABLE IF EXISTS detalle_pedidos;
DROP TABLE IF EXISTS pedidos;
DROP TABLE IF EXISTS consultas_clientes;
DROP TABLE IF EXISTS productos;
DROP TABLE IF EXISTS categorias;
DROP TABLE IF EXISTS proveedores;
DROP TABLE IF EXISTS clientes;
DROP TABLE IF EXISTS usuarios;

-- =================== 1. TABLAS CATÁLOGO ===================

CREATE TABLE categorias (
    id_categoria SERIAL PRIMARY KEY,
    nombre       VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE proveedores (
    id_proveedor SERIAL PRIMARY KEY,
    nombre       VARCHAR(80) NOT NULL,
    telefono     VARCHAR(20),
    email        VARCHAR(120)
);

CREATE TABLE clientes (
    id_cliente SERIAL PRIMARY KEY,
    nombre     VARCHAR(60) NOT NULL,
    email      VARCHAR(120) NOT NULL UNIQUE
);

-- =================== 2. TABLAS PRINCIPALES ===================

CREATE TABLE productos (
    id_producto  SERIAL PRIMARY KEY,
    nombre       VARCHAR(80)   NOT NULL,
    id_categoria INTEGER       NOT NULL REFERENCES categorias(id_categoria),
    descripcion  VARCHAR(200)  NOT NULL,
    precio       NUMERIC(10,2) NOT NULL CHECK (precio > 0),
    stock        INTEGER       NOT NULL CHECK (stock >= 0),
    icono        VARCHAR(10),
    id_proveedor INTEGER       REFERENCES proveedores(id_proveedor)
);

CREATE TABLE consultas_clientes (
    id_consulta   SERIAL PRIMARY KEY,
    id_cliente    INTEGER      NOT NULL REFERENCES clientes(id_cliente),
    tipo_consulta VARCHAR(30)  NOT NULL,
    asunto        VARCHAR(100) NOT NULL,
    mensaje       TEXT         NOT NULL,
    fecha_envio   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- =================== 3. TRANSACCIONES (CABECERA Y DETALLE) ===================

CREATE TABLE pedidos (
    id_pedido   SERIAL PRIMARY KEY,
    id_cliente  INTEGER       NOT NULL REFERENCES clientes(id_cliente),
    fecha       TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,
    estado      VARCHAR(20)   NOT NULL DEFAULT 'Pendiente',
    metodo_pago VARCHAR(20)   NOT NULL,
    total       NUMERIC(10,2) DEFAULT 0 CHECK (total >= 0)
);

CREATE TABLE detalle_pedidos (
    id_pedido       INTEGER       NOT NULL REFERENCES pedidos(id_pedido) ON DELETE CASCADE,
    id_producto     INTEGER       NOT NULL REFERENCES productos(id_producto),
    cantidad        INTEGER       NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMERIC(10,2) NOT NULL CHECK (precio_unitario > 0),
    subtotal        NUMERIC(10,2) NOT NULL CHECK (subtotal >= 0),
    PRIMARY KEY (id_pedido, id_producto)
);

-- =================== 4. AUTENTICACIÓN (Semana 14) ===================

CREATE TABLE usuarios (
    id_usuario      SERIAL PRIMARY KEY,
    nombre          VARCHAR(80)  NOT NULL,
    email           VARCHAR(120) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    rol             VARCHAR(20)  NOT NULL DEFAULT 'cliente'
                    CHECK (rol IN ('admin', 'cliente')),
    fecha_registro  TIMESTAMP    NOT NULL DEFAULT NOW(),
    id_cliente      INTEGER      UNIQUE
                                 REFERENCES clientes(id_cliente)
                                 ON DELETE CASCADE
);
-- NOTA: no insertes filas aquí con INSERT normal. La contraseña debe
-- quedar encriptada con el mismo algoritmo que usa Flask (Werkzeug),
-- así que los usuarios se crean SIEMPRE desde la aplicación:
--   - el primer administrador -> ejecutando "python crear_admin.py"
--   - el resto de usuarios     -> registrándose en /registro

-- =========================================================
-- =================== INSERTS DE PRUEBA ===================
-- =========================================================

-- Poblar 10 Categorías
INSERT INTO categorias (nombre) VALUES
('Analgésicos'),
('Antibióticos'),
('Vitaminas y Suplementos'),
('Cuidado Personal'),
('Primeros Auxilios'),
('Dermocosmética'),
('Equipos Médicos'),
('Salud Infantil'),
('Higiene Bucal'),
('Cuidado Femenino');

-- Poblar 10 Proveedores
INSERT INTO proveedores (nombre, telefono, email) VALUES
('Bayer S.A.', '0991234567', 'ventas@bayer.com'),
('Pfizer Ecuador', '0992345678', 'contacto@pfizer.com'),
('Roche', '0993456789', 'distribucion@roche.com'),
('Novartis', '0994567890', 'pedidos@novartis.com'),
('Sanofi', '0995678901', 'info@sanofi.com'),
('Genfar', '0996789012', 'ventas@genfar.com'),
('Johnson & Johnson', '0997890123', 'contacto@jnj.com'),
('Abbott', '0998901234', 'salud@abbott.com'),
('Merck', '0999012345', 'info@merck.com'),
('AstraZeneca', '0990123456', 'soporte@astrazeneca.com');

-- Poblar 10 Clientes
INSERT INTO clientes (nombre, email) VALUES
('Juan Pérez', 'juan.perez@email.com'),
('María Caiza', 'maria.caiza@email.com'),
('Carlos López', 'clopez@email.com'),
('Ana Martínez', 'ana.martinez@email.com'),
('Luis García', 'lgarcia.88@email.com'),
('Elena Fernández', 'elena.fer@email.com'),
('Jorge Torres', 'jorge.torres_99@email.com'),
('Carmen Ruiz', 'carmen.ruiz@email.com'),
('Raúl Silva', 'rsilva_dev@email.com'),
('Patricia Vega', 'patty.vega@email.com');

-- Poblar 10 Productos
INSERT INTO productos (nombre, id_categoria, descripcion, precio, stock, icono, id_proveedor) VALUES
('Aspirina 500mg', 1, 'Analgésico y antipirético x 100 tabletas.', 0.50, 200, '💊', 1),
('Amoxicilina 500mg', 2, 'Antibiótico de amplio espectro x 50 cápsulas.', 3.50, 150, '💊', 6),
('Vitamina C 1000mg', 3, 'Suplemento vitamínico efervescente.', 5.00, 100, '🍋', 1),
('Shampoo Neutro', 4, 'Shampoo para cuero cabelludo sensible 400ml.', 6.50, 80, '🧴', 7),
('Alcohol Antiséptico', 5, 'Alcohol al 70% frasco de 500ml.', 2.50, 300, '🧪', 6),
('Protector Solar SPF 50', 6, 'Protección alta para rostro y cuerpo.', 18.00, 50, '☀️', 4),
('Tensiómetro Digital', 7, 'Monitor de presión arterial de brazo.', 45.00, 20, '🩺', 3),
('Pañales Etapa 3', 8, 'Pañales para bebé paquete x 50 unidades.', 12.00, 60, '👶', 7),
('Pasta Dental Sensitive', 9, 'Alivio rápido para dientes sensibles.', 4.00, 120, '🪥', 8),
('Toallas Femeninas', 10, 'Paquete x 10 unidades con alas nocturnas.', 3.20, 150, '🩸', 7);

-- Poblar 10 Consultas de Clientes
INSERT INTO consultas_clientes (id_cliente, tipo_consulta, asunto, mensaje) VALUES
(1, 'General', 'Horarios', '¿Están abiertos los domingos?'),
(2, 'Disponibilidad', 'Tensiómetro', '¿Tienen stock del tensiómetro digital?'),
(3, 'Reclamo', 'Producto dañado', 'El envase del alcohol vino roto.'),
(4, 'General', 'Ubicación', '¿Tienen sucursales en el sur?'),
(5, 'Cotización', 'Vitaminas', 'Necesito cotizar 10 cajas de vitamina C.'),
(6, 'General', 'Métodos de pago', '¿Aceptan tarjetas de crédito?'),
(7, 'Disponibilidad', 'Antibiótico', '¿Necesito receta para la Amoxicilina?'),
(8, 'Soporte', 'Facturación', 'Por favor envíen la factura electrónica de mi última compra.'),
(9, 'General', 'Promociones', '¿Cuáles son los descuentos de este mes?'),
(10, 'Reclamo', 'Demora en entrega', 'Mi pedido a domicilio lleva 1 hora de retraso.');

-- Poblar 10 Pedidos (Cabeceras)
-- Los totales ya están pre-calculados basados en el detalle de la siguiente tabla
INSERT INTO pedidos (id_cliente, estado, metodo_pago, total) VALUES
(1, 'Completado', 'Efectivo', 5.00),     -- 10 Aspirinas (10 * 0.50)
(2, 'Pendiente', 'Transferencia', 7.00),  -- 2 Amoxicilinas (2 * 3.50)
(3, 'Completado', 'Tarjeta', 5.00),       -- 1 Vitamina C (1 * 5.00)
(4, 'En Ruta', 'Efectivo', 13.00),        -- 2 Shampoos (2 * 6.50)
(5, 'Completado', 'Transferencia', 7.50), -- 3 Alcoholes (3 * 2.50)
(6, 'Cancelado', 'Tarjeta', 18.00),       -- 1 Protector Solar (1 * 18.00)
(7, 'Pendiente', 'Efectivo', 45.00),      -- 1 Tensiómetro (1 * 45.00)
(8, 'Completado', 'Tarjeta', 24.00),      -- 2 Pañales (2 * 12.00)
(9, 'En Ruta', 'Transferencia', 8.00),    -- 2 Pastas dentales (2 * 4.00)
(10, 'Completado', 'Efectivo', 9.60);     -- 3 Toallas femeninas (3 * 3.20)

-- Poblar 10 Detalles de Pedidos (Líneas de factura)
INSERT INTO detalle_pedidos (id_pedido, id_producto, cantidad, precio_unitario, subtotal) VALUES
(1, 1, 10, 0.50, 5.00),   -- Pedido 1: Aspirina
(2, 2, 2, 3.50, 7.00),    -- Pedido 2: Amoxicilina
(3, 3, 1, 5.00, 5.00),    -- Pedido 3: Vitamina C
(4, 4, 2, 6.50, 13.00),   -- Pedido 4: Shampoo
(5, 5, 3, 2.50, 7.50),    -- Pedido 5: Alcohol
(6, 6, 1, 18.00, 18.00),  -- Pedido 6: Protector Solar
(7, 7, 1, 45.00, 45.00),  -- Pedido 7: Tensiómetro
(8, 8, 2, 12.00, 24.00),  -- Pedido 8: Pañales
(9, 9, 2, 4.00, 8.00),    -- Pedido 9: Pasta dental
(10, 10, 3, 3.20, 9.60);  -- Pedido 10: Toallas Femeninas

-- Índices para mejorar consultas con JOIN
CREATE INDEX IF NOT EXISTS idx_productos_categoria ON productos(id_categoria);
CREATE INDEX IF NOT EXISTS idx_pedidos_cliente ON pedidos(id_cliente);
CREATE INDEX IF NOT EXISTS idx_detalle_pedido ON detalle_pedidos(id_pedido);