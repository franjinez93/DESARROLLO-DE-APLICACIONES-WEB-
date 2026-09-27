# Farmacia Central — Semana 14: Login funcional + Carrito real

## 1. Instalar dependencias nuevas
```
pip install flask-login python-dotenv
pip freeze > requirements.txt
```
(Flask-WTF, psycopg2 y Werkzeug ya los tenías.)

## 2. Variables de entorno (.env)
1. Copia `.env.example` a `.env`.
2. Ábrelo y coloca tu contraseña real de PostgreSQL (ya viene precargada con `145678`,
   que es la que tenías en tu `conexion.py` original — cámbiala si corresponde).
3. **`.env` NUNCA debe subirse a GitHub** (ya está en `.gitignore`). Solo `.env.example`
   (sin datos reales) va al repositorio.

## 3. Base de datos
Ejecuta en pgAdmin4 (Query Tool, sobre `farmacia_central`):
```
sql/crear_tabla_usuarios.sql
```
Luego crea tu primer administrador:
```
python crear_admin.py
```

## 4. Copiar estos archivos a tu proyecto
- `app.py` → reemplaza el tuyo
- `models.py` → **archivo nuevo** (clase `Usuario`, separada de `app.py`)
- `database.py` → reemplaza el tuyo (sin cambios respecto a la entrega anterior)
- `conexion/conexion.py` → reemplaza el tuyo (ahora lee `.env`, no tiene credenciales)
- `.env`, `.env.example`, `.gitignore` → nuevos, en la raíz del proyecto
- `forms/login_form.py` → **archivo nuevo** (antes estaba dentro de `usuario_form.py`)
- `forms/usuario_form.py` → reemplaza el tuyo (ya no incluye `LoginForm`)
- `templates/base.html` → reemplaza el tuyo (token CSRF + selector de método de pago en el carrito)
- `templates/components/navbar.html` → reemplaza el tuyo (enlace a "Panel")
- `templates/dashboard.html` → **archivo nuevo**
- `templates/Productos.html` → reemplaza el tuyo (usa datos reales + botón "Agregar al carrito")
- `static/js/script.js` → reemplaza el tuyo (sin datos falsos; carrito real)
- `crear_admin.py`, `sql/crear_tabla_usuarios.sql` → de la entrega anterior, sin cambios

## 5. Qué se resolvió en esta ronda

### a) Cumplimiento literal de la tarea (Semana 14)
- **`/productos` ahora requiere `@login_required`**, tal como pide el enunciado
  ("proteja las rutas de administración relacionadas con Productos, Clientes,
  Proveedores o Facturación"). Cualquier usuario logueado (cliente o admin) puede
  entrar y comprar; solo un visitante sin cuenta es redirigido a `/login`.
- `models.py` separa la clase `Usuario` de `app.py`.
- `forms/login_form.py` separa `LoginForm` de `forms/usuario_form.py`.
- `templates/dashboard.html` + ruta `/dashboard`: panel post-login con accesos
  según el rol (todos ven "Comprar"; solo admin ve Clientes/Proveedores/Facturación).
  El login ahora redirige aquí por defecto.

### b) Seguridad de credenciales
- `conexion.py` ya **no tiene la contraseña de PostgreSQL escrita en el código**:
  la lee desde `.env` con `python-dotenv`. `SECRET_KEY` también se movió a `.env`.
- Se agregó `.gitignore` para que `.env` nunca se suba al repositorio.

### c) Catálogo y carrito: se eliminaron TODOS los datos falsos
- **`script.js` quedó limpio**: se borraron `catalogoPorCategoria`,
  `productosDestacados`, `pedidosRegistrados` y todas las funciones que
  simulaban un catálogo/formulario/panel de pedidos con datos inventados
  (`inicializarCatalogo`, `inicializarFormularioSeleccion`,
  `inicializarPanelPedidos`, `renderizarTablaPedidos`, etc.).
  ⚠️ Esto también arreglaba un **bug real**: `renderizarTablaPedidos()` borraba
  la tabla de pedidos reales en `/facturacion` apenas cargaba la página,
  reemplazándola por un arreglo vacío en JavaScript.
- **`Productos.html`** ahora arma cada tarjeta con los datos reales de la
  consulta a PostgreSQL (`nombre`, `precio`, `stock`, `descripcion`, `icono`,
  `categoria` vía JOIN con `categorias`) y cada producto **con stock** tiene un
  botón real de **"Agregar al carrito"**.
- **El carrito ahora es real**: al presionar "Confirmar Pedido", `script.js`
  envía los productos (con `fetch` + token CSRF) a la nueva ruta
  `POST /carrito/confirmar`, que:
  - exige sesión iniciada (si no, te manda a `/login`),
  - valida stock disponible,
  - registra un pedido en PostgreSQL por cada producto, asociado a tu cuenta
    (`current_user.nombre` / `current_user.email`),
  - descuenta el stock (reutiliza `database.insertar_pedido`, ya probado).
- No quedan clientes, proveedores ni usuarios de prueba hardcodeados en el
  código: `Clientes.html` y `Proveedores.html` ya renderizaban solo datos de
  PostgreSQL desde antes; si ves registros de prueba ahí, están en tu base de
  datos y se borran directamente desde pgAdmin4 (`DELETE FROM clientes ...`,
  `DELETE FROM proveedores ...`, `DELETE FROM usuarios WHERE ...`), no desde el código.

## 6. Pendiente / decisión tuya
- Dejé `/productos/nuevo` (Registrar Producto) protegido con `@admin_required`
  y el botón correspondiente solo visible para admin en `Productos.html`, ya
  que ahora tiene más sentido con el resto del esquema de roles. Si lo querías
  público, dímelo y lo destapo.
- El formulario `/comprar` (compra de un solo producto vía formulario clásico)
  se mantiene tal cual, como alternativa al carrito.
