# Sistema de Login, Registro y Roles — Farmacia Central

## 1. Instalar la librería que falta
```
pip install flask-login
```
(Flask-WTF, psycopg2 y Werkzeug ya los tienes instalados.)

## 2. Crear la tabla de usuarios en pgAdmin4
Abre el **Query Tool** sobre la base `farmacia_central` y ejecuta:
`sql/crear_tabla_usuarios.sql`

## 3. Crear tu primer usuario administrador
Desde la raíz de tu proyecto (donde está `app.py`):
```
python crear_admin.py
```
Te pedirá nombre, correo y contraseña, y te creará el único usuario con `rol='admin'`.
Cualquiera que se registre desde la web (`/registro`) queda automáticamente como `rol='cliente'`.

## 4. Copiar/reemplazar estos archivos en tu proyecto
- `app.py` → reemplaza el tuyo
- `database.py` → reemplaza el tuyo
- `forms/usuario_form.py` → archivo nuevo
- `templates/base.html` → reemplaza el tuyo (solo se quitó el modal de login falso)
- `templates/components/navbar.html` → reemplaza el tuyo
- `templates/login.html` → archivo nuevo
- `templates/registro.html` → archivo nuevo
- `templates/comprar.html` → archivo nuevo
- `static/js/script.js` → reemplaza el tuyo (se quitó el login simulado)
- `crear_admin.py` → archivo nuevo, en la raíz del proyecto
- `sql/crear_tabla_usuarios.sql` → solo para pgAdmin4

## 5. Qué cambió exactamente

**Login / Registro real**
- `/registro` crea la cuenta y guarda la contraseña **encriptada** (hash con Werkzeug/scrypt) en la tabla `usuarios`. Nunca se guarda en texto plano.
- `/login` verifica el hash con `check_password_hash`. Si es correcto, abre sesión con Flask-Login.
- `/logout` cierra la sesión.
- El modal falso de "Inicio de Sesión" (el que solo simulaba con JavaScript) fue eliminado de `base.html` y `script.js`. Ahora es 100% real.

**Roles y permisos**
- `admin_required` protege: `/clientes`, `/clientes/nuevo`, `/proveedores`, `/proveedores/nuevo`, `/facturacion`, `/facturacion/nuevo`. Si un usuario normal (o no logueado) intenta entrar, se le redirige con un mensaje.
- `/comprar` es la única acción que necesita un usuario **normal**: seleccionar producto, cantidad y método de pago. El nombre/correo se toman automáticamente de la sesión (no se pueden falsificar). Requiere `@login_required` (cualquier rol).
- El navbar (`navbar.html`) ahora muestra "Clientes / Proveedores / Facturación" **solo si `current_user.rol == 'admin'`**, y muestra "Comprar" para cualquier usuario logueado.

## 6. Puntos que quizás quieras revisar tú
- **`/clientes/nuevo`** (el formulario de "Enviar Consulta") ahora también quedó protegido como admin, porque forma parte del módulo "Clientes". Si en realidad quieres que **cualquier visitante** (sin cuenta) pueda enviarte una consulta de contacto, dímelo y te quito el `@admin_required` de esa ruta específica (dejando solo el listado protegido).
- **`/productos/nuevo`** (Registrar Producto) no lo protegí porque no lo mencionaste, pero normalmente también sería una acción de administrador. Puedo agregarle `@admin_required` si quieres.
- El carrito flotante (🛒 arriba a la derecha) sigue siendo una demo 100% en JavaScript (no guarda nada en PostgreSQL); es independiente de la nueva ruta `/comprar`, que sí es real y persiste en la base de datos. Si quieres que el carrito flotante también compre de verdad, es un cambio adicional que puedo hacer.
