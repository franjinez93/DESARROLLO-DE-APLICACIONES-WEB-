// ============================================================
//  FARMACIA CENTRAL - script.js
//  Fundamentos de JavaScript: manipulación del DOM y eventos
//  Estudiante: Edgar Francisco Jinez Montesdeoca
//  Asignatura: Desarrollo de Aplicaciones Web | Año: 2026
//  Subtema 2.1.1 - UEA
// ============================================================

// =====================
//  VARIABLES GLOBALES
// =====================
let totalProductos = 0;
let carrito = [];

// =====================
//  CATÁLOGO POR CATEGORÍA
// =====================
const catalogoPorCategoria = {
  "Medicamentos": [
    { nombre: "Paracetamol 500mg x20",    descripcion: "Analgésico y antipirético de uso común.",            precio: 2.50,  imagen: "💊" },
    { nombre: "Ibuprofeno 400mg x12",      descripcion: "Antiinflamatorio para dolor muscular y fiebre.",     precio: 3.20,  imagen: "💊" },
    { nombre: "Amoxicilina 500mg x21",     descripcion: "Antibiótico de amplio espectro.",                    precio: 6.80,  imagen: "💊" },
    { nombre: "Loratadina 10mg x10",       descripcion: "Antihistamínico para alergias estacionales.",        precio: 2.10,  imagen: "💊" },
    { nombre: "Omeprazol 20mg x14",        descripcion: "Protector gástrico para acidez y reflujo.",          precio: 4.50,  imagen: "💊" },
    { nombre: "Metformina 850mg x30",      descripcion: "Control de glucosa en diabetes tipo 2.",             precio: 5.90,  imagen: "💊" },
  ],
  "Naturales": [
    { nombre: "Vitamina C 1000mg x30",     descripcion: "Suplemento para reforzar el sistema inmune.",       precio: 5.80,  imagen: "🌿" },
    { nombre: "Omega 3 1000mg x60",        descripcion: "Ácidos grasos esenciales para el corazón.",         precio: 9.50,  imagen: "🌿" },
    { nombre: "Magnesio 400mg x60",        descripcion: "Minerales para músculos y sistema nervioso.",       precio: 7.20,  imagen: "🌿" },
    { nombre: "Zinc 50mg x30",             descripcion: "Fortalece el sistema inmunitario y la piel.",        precio: 4.10,  imagen: "🌿" },
    { nombre: "Valeriana Extracto x30",    descripcion: "Natural para relajación y sueño reparador.",         precio: 6.00,  imagen: "🌿" },
  ],
  "Cuidado Personal": [
    { nombre: "Gel Antibacterial 250ml",   descripcion: "Higiene personal con 70% de alcohol.",              precio: 3.20,  imagen: "🧴" },
    { nombre: "Mascarillas KN95 x10",      descripcion: "Protección respiratoria de alta eficiencia.",       precio: 4.80,  imagen: "🧴" },
    { nombre: "Termómetro Digital",        descripcion: "Lectura rápida en 10 segundos, sin mercurio.",      precio: 8.50,  imagen: "🧴" },
    { nombre: "Alcohol Antiséptico 500ml", descripcion: "Desinfectante para heridas y superficies.",         precio: 2.90,  imagen: "🧴" },
    { nombre: "Crema Hidratante SPF50",    descripcion: "Protección solar y cuidado de la piel.",            precio: 11.00, imagen: "🧴" },
  ],
  "Equipos Médicos": [
    { nombre: "Tensiómetro Digital",       descripcion: "Medición precisa de presión arterial doméstica.",   precio: 35.00, imagen: "🩺" },
    { nombre: "Glucómetro + 50 tiras",     descripcion: "Control de glucosa en sangre, fácil de usar.",     precio: 28.50, imagen: "🩺" },
    { nombre: "Oxímetro de Pulso",         descripcion: "Mide saturación de oxígeno y frecuencia cardíaca.",precio: 18.00, imagen: "🩺" },
    { nombre: "Nebulizador Ultrasónico",   descripcion: "Tratamiento respiratorio silencioso y eficiente.",  precio: 45.00, imagen: "🩺" },
    { nombre: "Silla de Ruedas Plegable",  descripcion: "Movilidad y comodidad, estructura de aluminio.",   precio: 95.00, imagen: "🩺" },
  ],
};

// Productos destacados para el catálogo visual superior
const productosDestacados = [
  catalogoPorCategoria["Medicamentos"][0],
  catalogoPorCategoria["Naturales"][0],
  catalogoPorCategoria["Cuidado Personal"][0],
  catalogoPorCategoria["Equipos Médicos"][0],
];

// =====================
//  INICIALIZACIÓN
// =====================
document.addEventListener("DOMContentLoaded", () => {
  inicializarCatalogo();
  inicializarFormularioSeleccion();
  inicializarCarrito();
  inicializarFormularioContacto();
  actualizarContador();
});

// ============================================================
//  1. CATÁLOGO DESTACADO (generado con createElement/appendChild)
// ============================================================
function inicializarCatalogo() {
  const contenedor = document.getElementById("catalogo-dinamico");
  if (!contenedor) return;
  productosDestacados.forEach((producto) => {
    contenedor.appendChild(crearTarjetaProducto(producto));
  });
}

function crearTarjetaProducto(producto) {
  const col = document.createElement("div");
  col.classList.add("col-12", "col-sm-6", "col-md-3", "mb-3");
  col.innerHTML = `
    <div class="card h-100 p-2 text-center producto-card">
      <div class="card-body d-flex flex-column">
        <div class="fs-1 mb-2">${producto.imagen}</div>
        <h6 class="card-title text-primary fw-bold">${producto.nombre}</h6>
        <p class="card-text small text-muted flex-grow-1">${producto.descripcion}</p>
        <p class="fw-bold text-success mb-2">$${producto.precio.toFixed(2)}</p>
        <button class="btn btn-primary btn-sm agregar-carrito">🛒 Agregar al carrito</button>
      </div>
    </div>`;
  col.querySelector(".agregar-carrito").addEventListener("click", () => {
    agregarAlCarrito(producto);
  });
  return col;
}

// ============================================================
//  2. FORMULARIO DE SELECCIÓN DE MEDICAMENTOS POR EL CLIENTE
// ============================================================
function inicializarFormularioSeleccion() {
  const form        = document.getElementById("form-producto");
  const selectCat   = document.getElementById("prod-categoria");
  const selectProd  = document.getElementById("prod-nombre");
  const inputCant   = document.getElementById("prod-cantidad");
  if (!form) return;

  // Evento change en categoría → carga los productos del select de medicamentos
  selectCat.addEventListener("change", () => {
    const categoria = selectCat.value;
    selectProd.innerHTML = '<option value="">-- Selecciona un producto --</option>';
    selectProd.disabled = true;
    ocultarPreview();

    if (!categoria) return;

    const productos = catalogoPorCategoria[categoria] || [];
    productos.forEach((p, i) => {
      const opt = document.createElement("option");
      opt.value = i;
      opt.textContent = `${p.imagen} ${p.nombre} — $${p.precio.toFixed(2)}`;
      selectProd.appendChild(opt);
    });
    selectProd.disabled = false;
    selectCat.classList.remove("is-invalid");
    selectCat.classList.add("is-valid");
  });

  // Evento change en producto → muestra preview con información
  selectProd.addEventListener("change", () => {
    const categoria = selectCat.value;
    const idx = selectProd.value;
    if (idx === "" || !categoria) { ocultarPreview(); return; }
    const producto = catalogoPorCategoria[categoria][parseInt(idx)];
    mostrarPreview(producto);
    selectProd.classList.remove("is-invalid");
    selectProd.classList.add("is-valid");
  });

  // Evento submit → valida y agrega al carrito + crea tarjeta en la lista
  form.addEventListener("submit", (event) => {
    event.preventDefault(); // preventDefault: evita recarga

    const categoria = selectCat.value;
    const idx       = selectProd.value;
    const cantidad  = parseInt(inputCant.value);

    // Validación de campos
    let valido = true;
    if (!categoria) { selectCat.classList.add("is-invalid"); valido = false; }
    if (idx === "") { selectProd.classList.add("is-invalid"); valido = false; }
    if (!cantidad || cantidad < 1) { inputCant.classList.add("is-invalid"); valido = false; }

    if (!valido) {
      mostrarMensaje("form-mensaje", "⚠️ Por favor completa todos los campos antes de continuar.", "danger");
      return;
    }

    const producto = catalogoPorCategoria[categoria][parseInt(idx)];

    // Agregar al carrito con la cantidad indicada
    for (let i = 0; i < cantidad; i++) {
      agregarAlCarrito(producto);
    }

    // Crear tarjeta de resumen en la lista inferior (createElement + appendChild)
    agregarTarjetaSeleccionada(producto, cantidad);

    // Limpiar formulario
    form.reset();
    selectProd.innerHTML = '<option value="">-- Primero elige categoría --</option>';
    selectProd.disabled = true;
    ocultarPreview();
    [selectCat, selectProd, inputCant].forEach(el => el.classList.remove("is-valid", "is-invalid"));

    mostrarMensaje("form-mensaje", `✅ <strong>${cantidad} × ${producto.nombre}</strong> agregado al carrito.`, "success");
    actualizarContador();
  });

  // Validación en tiempo real de cantidad
  inputCant.addEventListener("input", () => {
    if (parseInt(inputCant.value) >= 1) {
      inputCant.classList.remove("is-invalid");
      inputCant.classList.add("is-valid");
    } else {
      inputCant.classList.remove("is-valid");
      inputCant.classList.add("is-invalid");
    }
  });
}

function mostrarPreview(producto) {
  const preview = document.getElementById("preview-producto");
  if (!preview) return;
  document.getElementById("preview-icono").textContent    = producto.imagen;
  document.getElementById("preview-nombre-txt").textContent = producto.nombre;
  document.getElementById("preview-desc-txt").textContent   = producto.descripcion;
  document.getElementById("preview-precio-txt").textContent = `Precio: $${producto.precio.toFixed(2)}`;
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
    <div class="card h-100 shadow-sm border-0 producto-card">
      <div class="card-body d-flex flex-column">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <span class="fs-2">${producto.imagen}</span>
          <span class="badge bg-primary">x${cantidad}</span>
        </div>
        <h6 class="card-title fw-bold text-primary mb-1">${producto.nombre}</h6>
        <p class="card-text small text-muted flex-grow-1">${producto.descripcion}</p>
        <div class="d-flex justify-content-between align-items-center mt-2">
          <span class="fw-bold text-success">$${(producto.precio * cantidad).toFixed(2)}</span>
          <button class="btn btn-outline-danger btn-sm btn-eliminar" title="Quitar selección">🗑️ Quitar</button>
        </div>
      </div>
    </div>`;

  // Evento click para eliminar la tarjeta de la lista
  col.querySelector(".btn-eliminar").addEventListener("click", () => {
    col.style.transition = "opacity 0.3s";
    col.style.opacity = "0";
    setTimeout(() => {
      col.remove();
      totalProductos = Math.max(0, totalProductos - 1);
      actualizarContador();
    }, 300);
  });

  contenedor.appendChild(col);
}

// ============================================================
//  3. CARRITO DE COMPRAS
// ============================================================
function inicializarCarrito() {
  const btnVaciar = document.getElementById("btn-vaciar-carrito");
  if (btnVaciar) {
    btnVaciar.addEventListener("click", () => {
      carrito = [];
      renderizarCarrito();
      actualizarBadgeCarrito();
      mostrarMensaje("carrito-mensaje", "🛒 Carrito vaciado.", "info");
    });
  }

  const btnConfirmar = document.getElementById("btn-confirmar-pedido");
  if (btnConfirmar) {
    btnConfirmar.addEventListener("click", () => {
      if (carrito.length === 0) {
        mostrarMensaje("carrito-mensaje", "⚠️ Tu carrito está vacío.", "warning");
        return;
      }
      carrito = [];
      renderizarCarrito();
      actualizarBadgeCarrito();
      mostrarMensaje("carrito-mensaje", "✅ ¡Pedido confirmado! Nos contactaremos contigo pronto.", "success");
    });
  }

  // Renderizar cada vez que se abre el modal
  document.getElementById("modalCarrito")?.addEventListener("show.bs.modal", () => {
    renderizarCarrito();
  });
}

function agregarAlCarrito(producto) {
  const existente = carrito.find(p => p.nombre === producto.nombre);
  if (existente) {
    existente.cantidad++;
  } else {
    carrito.push({ ...producto, cantidad: 1 });
  }
  actualizarBadgeCarrito();
  mostrarToast(`${producto.imagen} <strong>${producto.nombre}</strong> agregado al carrito`);
}

function renderizarCarrito() {
  const lista   = document.getElementById("lista-carrito");
  const totalEl = document.getElementById("total-carrito");
  if (!lista) return;

  lista.innerHTML = "";
  if (carrito.length === 0) {
    lista.innerHTML = `<p class="text-center text-muted py-3">🛒 Tu carrito está vacío.<br>¡Selecciona un producto para comenzar!</p>`;
    if (totalEl) totalEl.textContent = "$0.00";
    return;
  }

  let total = 0;
  carrito.forEach((item, index) => {
    const subtotal = item.precio * item.cantidad;
    total += subtotal;

    const fila = document.createElement("div");
    fila.classList.add("d-flex", "justify-content-between", "align-items-center", "border-bottom", "py-2");
    fila.innerHTML = `
      <div class="d-flex align-items-center gap-2">
        <span class="fs-5">${item.imagen}</span>
        <div>
          <div class="fw-semibold small">${item.nombre}</div>
          <div class="text-muted small">$${item.precio.toFixed(2)} × ${item.cantidad}</div>
        </div>
      </div>
      <div class="d-flex align-items-center gap-2">
        <span class="fw-bold text-success">$${subtotal.toFixed(2)}</span>
        <button class="btn btn-outline-danger btn-sm btn-quitar" data-index="${index}" title="Quitar">✕</button>
      </div>`;

    fila.querySelector(".btn-quitar").addEventListener("click", (e) => {
      const idx = parseInt(e.currentTarget.dataset.index);
      if (carrito[idx].cantidad > 1) {
        carrito[idx].cantidad--;
      } else {
        carrito.splice(idx, 1);
      }
      renderizarCarrito();
      actualizarBadgeCarrito();
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

// ============================================================
//  4. FORMULARIO DE CONTACTO CON VALIDACIÓN JS
// ============================================================
function inicializarFormularioContacto() {
  const btnEnviar = document.querySelector("#contacto .btn-primary");
  if (!btnEnviar) return;

  btnEnviar.addEventListener("click", (e) => {
    e.preventDefault();
    const campos = [
      { id: "nombre",  val: document.getElementById("nombre")?.value.trim() },
      { id: "email",   val: document.getElementById("email")?.value.trim() },
      { id: "asunto",  val: document.getElementById("asunto")?.value.trim() },
      { id: "mensaje", val: document.getElementById("mensaje")?.value.trim() },
    ];
    let valido = true;
    campos.forEach(({ id, val }) => {
      const el = document.getElementById(id);
      if (!el) return;
      if (!val) { el.classList.add("is-invalid"); el.classList.remove("is-valid"); valido = false; }
      else { el.classList.remove("is-invalid"); el.classList.add("is-valid"); }
    });
    if (!valido) {
      mostrarMensaje("contacto-mensaje", "⚠️ Por favor completa todos los campos del formulario.", "danger");
      return;
    }
    const nombre = document.getElementById("nombre").value.trim();
    mostrarMensaje("contacto-mensaje", `✅ Mensaje enviado. ¡Gracias, ${nombre}! Te responderemos pronto.`, "success");
    campos.forEach(({ id }) => {
      const el = document.getElementById(id);
      if (el) { el.value = ""; el.classList.remove("is-valid"); }
    });
  });
}

// ============================================================
//  5. UTILIDADES
// ============================================================
function actualizarContador() {
  const el = document.getElementById("contador-productos");
  if (el) el.textContent = totalProductos;
}

function mostrarMensaje(contenedorId, texto, tipo) {
  let contenedor = document.getElementById(contenedorId);
  if (!contenedor) return;
  contenedor.innerHTML = `
    <div class="alert alert-${tipo} alert-dismissible fade show py-2 mt-2" role="alert">
      ${texto}
      <button type="button" class="btn-close btn-sm" data-bs-dismiss="alert"></button>
    </div>`;
  setTimeout(() => {
    const alerta = contenedor.querySelector(".alert");
    if (alerta) { alerta.classList.remove("show"); setTimeout(() => alerta.remove(), 300); }
  }, 4000);
}

function mostrarToast(htmlTexto) {
  let contenedor = document.getElementById("toast-container");
  if (!contenedor) {
    contenedor = document.createElement("div");
    contenedor.id = "toast-container";
    contenedor.style.cssText = "position:fixed;bottom:20px;right:20px;z-index:9999;";
    document.body.appendChild(contenedor);
  }
  const toast = document.createElement("div");
  toast.classList.add("toast", "show", "align-items-center", "text-white", "bg-success", "border-0", "mb-2");
  toast.setAttribute("role", "alert");
  toast.innerHTML = `<div class="d-flex">
    <div class="toast-body">${htmlTexto}</div>
    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
  </div>`;
  contenedor.appendChild(toast);
  setTimeout(() => {
    toast.style.transition = "opacity 0.4s";
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 400);
  }, 3000);
}
