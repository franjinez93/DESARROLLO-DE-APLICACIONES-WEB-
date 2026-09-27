// ============================================================
//  FARMACIA CENTRAL - script.js
//  Fundamentos de JavaScript: manipulación del DOM y eventos
//  Estudiante: Edgar Francisco Jinez Montesdeoca
// ============================================================

let totalProductos = 0;
let carrito = [];
let pedidosRegistrados = [];
let contadorIdPedido = 1;

const catalogoPorCategoria = {
  "Medicamentos": [
    { nombre: "Paracetamol 500mg x20", descripcion: "Analgésico y antipirético.", precio: 2.50, imagen: "💊" },
    { nombre: "Ibuprofeno 400mg x12", descripcion: "Antiinflamatorio para dolor muscular.", precio: 3.20, imagen: "💊" },
    { nombre: "Amoxicilina 500mg x21", descripcion: "Antibiótico de amplio espectro.", precio: 6.80, imagen: "💊" },
    { nombre: "Omeprazol 20mg x14", descripcion: "Protector gástrico.", precio: 4.50, imagen: "💊" }
  ],
  "Naturales": [
    { nombre: "Vitamina C 1000mg x30", descripcion: "Refuerza el sistema inmune.", precio: 5.80, imagen: "🌿" },
    { nombre: "Omega 3 1000mg x60", descripcion: "Ácidos grasos para el corazón.", precio: 9.50, imagen: "🌿" },
    { nombre: "Valeriana Extracto x30", descripcion: "Relajación y sueño reparador.", precio: 6.00, imagen: "🌿" }
  ],
  "Cuidado Personal": [
    { nombre: "Gel Antibacterial 250ml", descripcion: "Higiene personal con 70% alcohol.", precio: 3.20, imagen: "🧴" },
    { nombre: "Mascarillas KN95 x10", descripcion: "Protección respiratoria.", precio: 4.80, imagen: "🧴" },
    { nombre: "Crema Hidratante SPF50", descripcion: "Protección solar y cuidado de la piel.", precio: 11.00, imagen: "🧴" }
  ],
  "Equipos Médicos": [
    { nombre: "Tensiómetro Digital", descripcion: "Medición de presión arterial.", precio: 35.00, imagen: "🩺" },
    { nombre: "Glucómetro + 50 tiras", descripcion: "Control de glucosa en sangre.", precio: 28.50, imagen: "🩺" },
    { nombre: "Oxímetro de Pulso", descripcion: "Mide saturación de oxígeno.", precio: 18.00, imagen: "🩺" }
  ]
};

const productosDestacados = [
  catalogoPorCategoria["Medicamentos"][0],
  catalogoPorCategoria["Naturales"][0],
  catalogoPorCategoria["Cuidado Personal"][0],
  catalogoPorCategoria["Equipos Médicos"][0]
];

document.addEventListener("DOMContentLoaded", () => {
  // Navbar scroll
  const navbar = document.getElementById('mainNav');
  if (navbar) {
      window.addEventListener('scroll', () => {
          if (window.scrollY > 50) navbar.classList.add('scrolled');
          else navbar.classList.remove('scrolled');
      });
  }

  inicializarCatalogo();
  inicializarFormularioSeleccion();
  inicializarCarrito();
  inicializarPanelPedidos();
  inicializarFormularioContacto();
  inicializarLogin(); // <--- NUEVA FUNCIÓN
  actualizarContador();
});

// ============================================================
//  LÓGICA DEL LOGIN SIMULADO
// ============================================================
function inicializarLogin() {
  const formLogin = document.getElementById("form-login");
  if (!formLogin) return;

  formLogin.addEventListener("submit", (e) => {
    e.preventDefault();
    const user = document.getElementById("login-user");
    const pass = document.getElementById("login-pass");

    if (!user.value || !pass.value) {
      mostrarMensaje("login-mensaje", "⚠️ Por favor, ingresa usuario y contraseña.", "danger");
      return;
    }

    // Simular carga exitosa
    mostrarMensaje("login-mensaje", "✅ Acceso concedido...", "success");

    setTimeout(() => {
      // 1. Cerrar el modal
      bootstrap.Modal.getInstance(document.getElementById("modalLogin")).hide();

      // 2. Cambiar la apariencia del botón en la barra de navegación
      const btnNav = document.getElementById("btn-nav-login");
      if (btnNav) {
        btnNav.innerHTML = `<i class="fa-solid fa-user-check"></i> Hola, ${user.value}`;
        btnNav.classList.remove("text-brand-yellow");
        btnNav.classList.add("text-success");
        // Quitar eventos del modal para que no se abra de nuevo
        btnNav.removeAttribute("data-bs-toggle");
        btnNav.removeAttribute("data-bs-target");
      }

      // 3. Desbloquear (hacer visible) el Panel de Pedidos
      const panel = document.getElementById("panel-pedidos");
      if (panel) {
        panel.classList.remove("d-none"); // Quitar ocultamiento
        panel.scrollIntoView({ behavior: 'smooth' }); // Llevar al usuario a la sección
      }

      formLogin.reset();
    }, 1200);
  });
}

// ============================================================
//  RESTO DE LA LÓGICA DEL PROYECTO
// ============================================================
function inicializarCatalogo() {
  const contenedor = document.getElementById("catalogo-dinamico");
  const spinner = document.getElementById("spinner-catalogo");
  if (!contenedor) return;

  setTimeout(() => {
    productosDestacados.forEach((producto) => {
      contenedor.appendChild(crearTarjetaProducto(producto));
    });
    if (spinner) spinner.classList.add("d-none");
    contenedor.classList.remove("d-none");
  }, 900);
}

function crearTarjetaProducto(producto) {
  const col = document.createElement("div");
  col.classList.add("col-12", "col-sm-6", "col-md-3", "mb-3");
  col.innerHTML = `
    <div class="card h-100 p-3 text-center card-hover">
      <div class="card-body d-flex flex-column">
        <div class="display-5 mb-2">${producto.imagen}</div>
        <h6 class="card-title text-white fw-bold">${producto.nombre}</h6>
        <p class="card-text small text-muted flex-grow-1">${producto.descripcion}</p>
        <p class="fw-bold text-brand-yellow fs-5 mb-3">$${producto.precio.toFixed(2)}</p>
        <button class="btn btn-outline-light btn-sm agregar-carrito mt-auto">Agregar al carrito</button>
      </div>
    </div>`;
  col.querySelector(".agregar-carrito").addEventListener("click", () => agregarAlCarrito(producto));
  return col;
}

function inicializarFormularioSeleccion() {
  const form = document.getElementById("form-producto");
  const selectCat = document.getElementById("prod-categoria");
  const selectProd = document.getElementById("prod-nombre");
  const inputCant = document.getElementById("prod-cantidad");
  if (!form) return;

  selectCat.addEventListener("change", () => {
    const categoria = selectCat.value;
    selectProd.innerHTML = '<option value="">-- Selecciona un producto --</option>';
    selectProd.disabled = true;
    ocultarPreview();
    limpiarValidacion(selectProd);

    if (!categoria) { marcarInvalido(selectCat, "Selecciona una categoría."); return; }

    const productos = catalogoPorCategoria[categoria] || [];
    productos.forEach((p, i) => {
      const opt = document.createElement("option");
      opt.value = i;
      opt.textContent = `${p.imagen} ${p.nombre} — $${p.precio.toFixed(2)}`;
      selectProd.appendChild(opt);
    });
    selectProd.disabled = false;
    marcarValido(selectCat);
  });

  selectProd.addEventListener("change", () => {
    const categoria = selectCat.value;
    const idx = selectProd.value;
    if (idx === "" || !categoria) { ocultarPreview(); marcarInvalido(selectProd, "Selecciona un producto."); return; }
    mostrarPreview(catalogoPorCategoria[categoria][parseInt(idx)]);
    marcarValido(selectProd);
  });

  inputCant.addEventListener("input", () => validarNumero(inputCant, 1, 99));

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const categoriaValida = validarSeleccion(selectCat, "Selecciona una categoría.");
    const productoValido = validarSeleccion(selectProd, "Selecciona un producto.");
    const cantidadValida = validarNumero(inputCant, 1, 99);

    if (!(categoriaValida && productoValido && cantidadValida)) {
      mostrarMensaje("form-mensaje", "⚠️ Completa los campos en rojo.", "danger");
      return;
    }

    const producto = catalogoPorCategoria[selectCat.value][parseInt(selectProd.value)];
    const cantidad = parseInt(inputCant.value);

    for (let i = 0; i < cantidad; i++) agregarAlCarrito(producto);
    agregarTarjetaSeleccionada(producto, cantidad);

    form.reset();
    selectProd.innerHTML = '<option value="">-- Primero elige categoría --</option>';
    selectProd.disabled = true;
    ocultarPreview();
    [selectCat, selectProd, inputCant].forEach(limpiarValidacion);
    mostrarMensaje("form-mensaje", `✅ <strong>${cantidad} × ${producto.nombre}</strong> agregado.`, "success");
    actualizarContador();
  });
}

function mostrarPreview(producto) {
  const preview = document.getElementById("preview-producto");
  if (!preview) return;
  document.getElementById("preview-icono").textContent = producto.imagen;
  document.getElementById("preview-nombre-txt").textContent = producto.nombre;
  document.getElementById("preview-desc-txt").textContent = producto.descripcion;
  document.getElementById("preview-precio-txt").textContent = `$${producto.precio.toFixed(2)}`;
  preview.classList.remove("d-none");
}

function ocultarPreview() {
  const preview = document.getElementById("preview-producto");
  if (preview) preview.classList.add("d-none");
}

function agregarTarjetaSeleccionada(producto, cantidad) {
  const contenedor = document.getElementById("lista-productos");
  if (!contenedor) return;
  totalProductos++;

  const col = document.createElement("div");
  col.classList.add("col-12", "col-sm-6", "col-md-4", "mb-3", "producto-item");
  col.innerHTML = `
    <div class="card h-100 border-secondary card-hover bg-dark">
      <div class="card-body d-flex flex-column">
        <div class="d-flex justify-content-between mb-2">
          <span class="fs-4">${producto.imagen}</span>
          <span class="badge bg-secondary">x${cantidad}</span>
        </div>
        <h6 class="text-white mb-1">${producto.nombre}</h6>
        <div class="d-flex justify-content-between align-items-center mt-auto pt-2">
          <span class="fw-bold text-brand-yellow">$${(producto.precio * cantidad).toFixed(2)}</span>
          <button class="btn btn-outline-danger btn-sm btn-eliminar">Quitar</button>
        </div>
      </div>
    </div>`;

  col.querySelector(".btn-eliminar").addEventListener("click", () => {
    col.remove();
    totalProductos = Math.max(0, totalProductos - 1);
    actualizarContador();
  });
  contenedor.appendChild(col);
}

function inicializarCarrito() {
  const btnVaciar = document.getElementById("btn-vaciar-carrito");
  if (btnVaciar) btnVaciar.addEventListener("click", () => { carrito = []; renderizarCarrito(); actualizarBadgeCarrito(); });

  const btnConfirmar = document.getElementById("btn-confirmar-pedido");
  if (btnConfirmar) {
    btnConfirmar.addEventListener("click", () => {
      if (carrito.length === 0) return;
      btnConfirmar.disabled = true;
      document.getElementById("spinner-confirmar").classList.remove("d-none");
      document.getElementById("texto-confirmar").textContent = " Procesando...";

      setTimeout(() => {
        carrito.forEach((item) => {
          pedidosRegistrados.push({
            id: contadorIdPedido++, cliente: "Cliente Web", producto: item.nombre,
            cantidad: item.cantidad, total: item.precio * item.cantidad, estado: "Confirmado"
          });
        });
        renderizarTablaPedidos();
        carrito = []; renderizarCarrito(); actualizarBadgeCarrito();
        btnConfirmar.disabled = false;
        document.getElementById("spinner-confirmar").classList.add("d-none");
        document.getElementById("texto-confirmar").textContent = "Confirmar Pedido";
        bootstrap.Modal.getInstance(document.getElementById("modalCarrito")).hide();
      }, 1000);
    });
  }
}

function agregarAlCarrito(producto) {
  const existente = carrito.find(p => p.nombre === producto.nombre);
  if (existente) existente.cantidad++; else carrito.push({ ...producto, cantidad: 1 });
  actualizarBadgeCarrito();
  mostrarToast(`${producto.imagen} <strong>${producto.nombre}</strong> al carrito`);
}

function renderizarCarrito() {
  const lista = document.getElementById("lista-carrito");
  const totalEl = document.getElementById("total-carrito");
  if (!lista) return;

  if (carrito.length === 0) {
    lista.innerHTML = `<p class="text-center text-muted py-3">Tu carrito está vacío.</p>`;
    if (totalEl) totalEl.textContent = "$0.00";
    return;
  }

  let total = 0;
  lista.innerHTML = "";
  carrito.forEach((item, index) => {
    total += item.precio * item.cantidad;
    const fila = document.createElement("div");
    fila.className = "d-flex justify-content-between align-items-center border-bottom border-secondary py-2";
    fila.innerHTML = `
      <div><div class="fw-semibold text-white">${item.nombre}</div><small class="text-muted">${item.cantidad} x $${item.precio.toFixed(2)}</small></div>
      <div class="d-flex align-items-center gap-2"><span class="text-brand-yellow fw-bold">$${(item.precio * item.cantidad).toFixed(2)}</span><button class="btn btn-outline-danger btn-sm btn-quitar" data-index="${index}">X</button></div>`;
    fila.querySelector(".btn-quitar").addEventListener("click", () => {
      carrito[index].cantidad > 1 ? carrito[index].cantidad-- : carrito.splice(index, 1);
      renderizarCarrito(); actualizarBadgeCarrito();
    });
    lista.appendChild(fila);
  });
  if (totalEl) totalEl.textContent = `$${total.toFixed(2)}`;
}

function actualizarBadgeCarrito() {
  const badge = document.getElementById("badge-carrito");
  if (!badge) return;
  const totalItems = carrito.reduce((acc, p) => acc + p.cantidad, 0);
  badge.textContent = totalItems;
  badge.style.display = totalItems > 0 ? "inline-block" : "none";
}

function inicializarPanelPedidos() {
  const form = document.getElementById("form-pedido");
  const selectProducto = document.getElementById("pedido-producto");
  if (!form || !selectProducto) return;

  Object.keys(catalogoPorCategoria).forEach((categoria) => {
    const grupo = document.createElement("optgroup");
    grupo.label = categoria;
    catalogoPorCategoria[categoria].forEach((p) => {
      const opt = document.createElement("option");
      opt.value = p.nombre; opt.dataset.precio = p.precio;
      opt.textContent = `${p.nombre} — $${p.precio.toFixed(2)}`;
      grupo.appendChild(opt);
    });
    selectProducto.appendChild(grupo);
  });

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const campoC = document.getElementById("pedido-cliente");
    const campoCant = document.getElementById("pedido-cantidad");
    
    if (!(validarTexto(campoC, 3) && validarSeleccion(selectProducto, "") && validarNumero(campoCant, 1, 99))) return;

    pedidosRegistrados.push({
      id: contadorIdPedido++, cliente: campoC.value.trim(), producto: selectProducto.value,
      cantidad: parseInt(campoCant.value), total: parseFloat(selectProducto.options[selectProducto.selectedIndex].dataset.precio) * parseInt(campoCant.value),
      estado: "Pendiente"
    });
    
    renderizarTablaPedidos();
    form.reset(); campoCant.value = 1;
    [campoC, selectProducto, campoCant].forEach(limpiarValidacion);
  });
  renderizarTablaPedidos();
}

function renderizarTablaPedidos() {
  const tbody = document.getElementById("tabla-pedidos");
  const aviso = document.getElementById("pedidos-vacio");
  if (!tbody) return;

  if (pedidosRegistrados.length === 0) {
    tbody.innerHTML = "";
    if (aviso) aviso.classList.remove("d-none");
    document.getElementById("contador-pedidos").textContent = "0";
    return;
  }
  
  if (aviso) aviso.classList.add("d-none");
  tbody.innerHTML = "";
  
  pedidosRegistrados.forEach((pedido, i) => {
    const claseBadge = pedido.estado === "Confirmado" ? "badge-estado-confirmado" : "badge-estado-pendiente";
    const tr = document.createElement("tr");
    tr.className = "fila-pedido";
    tr.innerHTML = `<td>${i + 1}</td><td>${pedido.cliente}</td><td>${pedido.producto}</td><td>${pedido.cantidad}</td>
      <td class="text-brand-yellow fw-bold">$${pedido.total.toFixed(2)}</td>
      <td><span class="badge ${claseBadge}">${pedido.estado}</span></td>
      <td><button class="btn btn-outline-danger btn-sm">🗑️</button></td>`;
    tr.querySelector("button").addEventListener("click", () => { pedidosRegistrados.splice(i, 1); renderizarTablaPedidos(); });
    tbody.appendChild(tr);
  });
  document.getElementById("contador-pedidos").textContent = pedidosRegistrados.length;
}

function inicializarFormularioContacto() {
  const f = document.getElementById("form-contacto");
  if (!f) return;
  f.addEventListener("submit", (e) => {
    e.preventDefault();
    mostrarMensaje("contacto-mensaje", "✅ Mensaje enviado con éxito.", "success");
    f.reset();
  });
}

// VALIDACIONES ORIGINALES
function marcarValido(e) { e.classList.remove("is-invalid"); e.classList.add("is-valid"); }
function marcarInvalido(e, m) { e.classList.remove("is-valid"); e.classList.add("is-invalid"); const f = e.parentElement.querySelector(".invalid-feedback"); if (f && m) f.textContent = m; }
function limpiarValidacion(e) { e.classList.remove("is-valid", "is-invalid"); }
function validarTexto(e, min) { const v = e.value.trim(); if (v.length < min) { marcarInvalido(e); return false; } marcarValido(e); return true; }
function validarSeleccion(e) { if (!e.value) { marcarInvalido(e); return false; } marcarValido(e); return true; }
function validarNumero(e, min, max) { const v = parseInt(e.value); if (isNaN(v) || v < min || v > max) { marcarInvalido(e); return false; } marcarValido(e); return true; }

function actualizarContador() { const el = document.getElementById("contador-productos"); if (el) el.textContent = totalProductos; }
function mostrarMensaje(id, t, tipo) {
  const c = document.getElementById(id); if (!c) return;
  c.innerHTML = `<div class="alert alert-${tipo} alert-dismissible fade show mt-2">${t}<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>`;
}
function mostrarToast(txt) {
  let c = document.getElementById("toast-container");
  if (!c) { c = document.createElement("div"); c.id = "toast-container"; c.style.cssText = "position:fixed;bottom:20px;right:20px;z-index:9999;"; document.body.appendChild(c); }
  const t = document.createElement("div");
  t.className = "toast show align-items-center text-dark bg-brand-yellow border-0 mb-2";
  t.innerHTML = `<div class="d-flex"><div class="toast-body fw-bold">${txt}</div><button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast"></button></div>`;
  c.appendChild(t);
  setTimeout(() => { t.style.opacity = "0"; setTimeout(() => t.remove(), 400); }, 3000);
}