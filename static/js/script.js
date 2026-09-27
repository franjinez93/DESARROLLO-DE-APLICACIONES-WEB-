// ============================================================
//  FARMACIA CENTRAL - script.js
//  Estudiante: Edgar Francisco Jinez Montesdeoca
//
//  NOTA (Semana 14): se eliminó todo el catálogo, formulario de
//  selección y panel de pedidos que usaban datos FALSOS/hardcodeados
//  (catalogoPorCategoria, pedidosRegistrados, etc.). Ahora:
//  - Los productos que ves en /productos vienen 100% de PostgreSQL
//    (renderizados por Flask/Jinja2 en Productos.html).
//  - El botón "Agregar al carrito" de cada producto real dispara
//    agregarAlCarrito() usando los data-attributes de esa tarjeta.
//  - "Confirmar Pedido" ya NO es una simulación: envía el carrito al
//    backend (ruta /carrito/confirmar) y se guarda como pedido real
//    en la base de datos, asociado al usuario que inició sesión.
//  NOTA (ronda de ajustes): el carrito ahora se guarda en localStorage
//  (guardarCarrito / cargarCarritoGuardado) para que NO se vacíe al
//  cambiar de página. Antes vivía solo en la variable "carrito" y se
//  perdía en cada recarga, por eso el ícono flotante y "Comprar" a
//  veces se veían vacíos aunque ya hubieras agregado productos.
// ============================================================

const CARRITO_STORAGE_KEY = "farmacia_carrito";

let carrito = cargarCarritoGuardado();

function cargarCarritoGuardado() {
  try {
    const guardado = localStorage.getItem(CARRITO_STORAGE_KEY);
    const datos = guardado ? JSON.parse(guardado) : [];
    return Array.isArray(datos) ? datos : [];
  } catch (error) {
    return [];
  }
}

function guardarCarrito() {
  try {
    localStorage.setItem(CARRITO_STORAGE_KEY, JSON.stringify(carrito));
  } catch (error) {
    // Si el navegador bloquea localStorage (modo privado, etc.) el carrito
    // simplemente no persiste entre páginas, pero sigue funcionando en la actual.
  }
}

document.addEventListener("DOMContentLoaded", () => {
  // Efecto de navbar al hacer scroll
  const navbar = document.getElementById('mainNav');
  if (navbar) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 50) navbar.classList.add('scrolled');
      else navbar.classList.remove('scrolled');
    });
  }

  inicializarBotonesAgregarCarrito(); // productos REALES (desde PostgreSQL)
  inicializarCarrito();
  inicializarMetodoPago();
  actualizarBadgeCarrito(); // refleja de inmediato el carrito restaurado desde localStorage
});

// ============================================================
//  CATÁLOGO REAL (desde PostgreSQL, renderizado por Flask/Jinja2)
// ============================================================
function inicializarBotonesAgregarCarrito() {
  // Botones +/- de cada tarjeta: ajustan el número ANTES de agregar al carrito
  document.querySelectorAll(".btn-sumar-cantidad, .btn-restar-cantidad").forEach((boton) => {
    boton.addEventListener("click", () => {
      const card = boton.closest("[data-nombre]");
      const input = card?.querySelector(".cantidad-input");
      if (!input) return;
      input.value = ajustarCantidad(input, boton.classList.contains("btn-sumar-cantidad") ? 1 : -1);
    });
  });

  // Si el usuario escribe la cantidad a mano, también se limita entre 1 y el stock
  document.querySelectorAll(".cantidad-input").forEach((input) => {
    input.addEventListener("change", () => {
      input.value = ajustarCantidad(input, 0);
    });
  });

  document.querySelectorAll(".agregar-carrito").forEach((boton) => {
    boton.addEventListener("click", () => {
      const card = boton.closest("[data-nombre]");
      if (!card) return;

      const inputCantidad = card.querySelector(".cantidad-input");
      const cantidad = inputCantidad ? ajustarCantidad(inputCantidad, 0) : 1;

      const producto = {
        nombre: card.dataset.nombre,
        precio: parseFloat(card.dataset.precio),
        imagen: card.dataset.icono || "💊",
      };

      agregarAlCarrito(producto, cantidad);

      if (inputCantidad) inputCantidad.value = 1; // se reinicia para la próxima vez
    });
  });
}

// Lee el valor actual de un input de cantidad, le suma "delta" (0 = solo
// validar) y lo limita entre 1 y su "max" (el stock disponible del producto).
function ajustarCantidad(input, delta) {
  const max = parseInt(input.max, 10) || 99;
  let valor = (parseInt(input.value, 10) || 1) + delta;
  if (valor < 1) valor = 1;
  if (valor > max) valor = max;
  return valor;
}

// ============================================================
//  MÉTODO DE PAGO (muestra/oculta los campos de tarjeta)
// ============================================================
function inicializarMetodoPago() {
  const select = document.getElementById("carrito-metodo-pago");
  const camposTarjeta = document.getElementById("campos-tarjeta");
  if (!select || !camposTarjeta) return;

  const alternar = () => {
    camposTarjeta.classList.toggle("d-none", select.value !== "Tarjeta");
  };

  select.addEventListener("change", alternar);
  alternar(); // estado inicial (por si el modal se reabre con "Efectivo" ya elegido)
}

// Valida (solo en el navegador) que los campos de tarjeta simulados
// estén completos y con un formato razonable. Nunca se envían al
// backend: solo sirven para que el flujo se sienta completo.
function validarDatosTarjeta() {
  const numero = document.getElementById("tarjeta-numero")?.value.replace(/\s+/g, "") || "";
  const vencimiento = document.getElementById("tarjeta-vencimiento")?.value.trim() || "";
  const cvv = document.getElementById("tarjeta-cvv")?.value.trim() || "";
  const nombre = document.getElementById("tarjeta-nombre")?.value.trim() || "";

  if (numero.length < 13 || numero.length > 19 || !/^\d+$/.test(numero)) {
    return "Ingresa un número de tarjeta válido.";
  }
  if (!/^\d{2}\/\d{2}$/.test(vencimiento)) {
    return "El vencimiento debe tener el formato MM/AA.";
  }
  if (!/^\d{3,4}$/.test(cvv)) {
    return "El CVV debe tener 3 o 4 dígitos.";
  }
  if (nombre.length < 3) {
    return "Ingresa el nombre tal como aparece en la tarjeta.";
  }
  return null; // sin errores
}

// ============================================================
//  CARRITO DE COMPRAS (real: se guarda en PostgreSQL al confirmar)
// ============================================================
function inicializarCarrito() {
  const btnVaciar = document.getElementById("btn-vaciar-carrito");
  if (btnVaciar) {
    btnVaciar.addEventListener("click", () => {
      carrito = [];
      guardarCarrito();
      renderizarCarrito();
      actualizarBadgeCarrito();
    });
  }

  const btnConfirmar = document.getElementById("btn-confirmar-pedido");
  if (btnConfirmar) {
    btnConfirmar.addEventListener("click", () => confirmarPedido(btnConfirmar));
  }
}

function agregarAlCarrito(producto, cantidad = 1) {
  const existente = carrito.find((p) => p.nombre === producto.nombre);
  if (existente) existente.cantidad += cantidad;
  else carrito.push({ ...producto, cantidad });

  guardarCarrito();
  actualizarBadgeCarrito();
  mostrarToast(`${producto.imagen} <strong>${producto.nombre}</strong> (${cantidad}) al carrito`);
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
      guardarCarrito();
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
  renderizarCarrito();
}

// Envía el carrito al backend (ruta /carrito/confirmar). Requiere
// haber iniciado sesión: si no, el backend redirige y aquí detectamos
// esa redirección para avisarle al usuario que debe loguearse.
async function confirmarPedido(btnConfirmar) {
  if (carrito.length === 0) return;

  const spinner = document.getElementById("spinner-confirmar");
  const texto = document.getElementById("texto-confirmar");
  const metodoPago = document.getElementById("carrito-metodo-pago")?.value || "Efectivo";
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

  // Si el pago es con tarjeta, se validan los datos simulados ANTES de
  // llamar al backend. El número/vencimiento/CVV nunca se incluyen en
  // el fetch de abajo: solo se usan para esta validación en pantalla.
  if (metodoPago === "Tarjeta") {
    const errorTarjeta = validarDatosTarjeta();
    if (errorTarjeta) {
      mostrarMensaje("carrito-mensaje", `⚠️ ${errorTarjeta}`, "warning");
      return;
    }
  }

  btnConfirmar.disabled = true;
  if (spinner) spinner.classList.remove("d-none");
  if (texto) texto.textContent = " Procesando...";

  try {
    const respuesta = await fetch("/carrito/confirmar", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken || "",
      },
      body: JSON.stringify({
        items: carrito.map((item) => ({ nombre: item.nombre, cantidad: item.cantidad })),
        metodo_pago: metodoPago,
      }),
    });

    const esJson = respuesta.headers.get("content-type")?.includes("application/json");

    if (respuesta.redirected || !esJson) {
      mostrarMensaje("carrito-mensaje", "⚠️ Debes iniciar sesión para confirmar tu compra.", "warning");
      setTimeout(() => { window.location.href = "/login"; }, 1400);
      return;
    }

    const data = await respuesta.json();

    if (data.ok) {
      mostrarMensaje("carrito-mensaje", `✅ ${data.mensaje}`, "success");
      carrito = [];
      guardarCarrito();
      renderizarCarrito();
      actualizarBadgeCarrito();
      setTimeout(() => window.location.reload(), 1400);
    } else {
      mostrarMensaje("carrito-mensaje", `⚠️ ${data.mensaje}`, "danger");
    }
  } catch (error) {
    mostrarMensaje("carrito-mensaje", "❌ Ocurrió un error al procesar la compra.", "danger");
  } finally {
    btnConfirmar.disabled = false;
    if (spinner) spinner.classList.add("d-none");
    if (texto) texto.textContent = "Confirmar Pedido";
  }
}

// ============================================================
//  UTILIDADES DE INTERFAZ
// ============================================================
function mostrarMensaje(id, texto, tipo) {
  const contenedor = document.getElementById(id);
  if (!contenedor) return;
  contenedor.innerHTML = `<div class="alert alert-${tipo} alert-dismissible fade show mt-2">${texto}<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>`;
}

function mostrarToast(texto) {
  let contenedor = document.getElementById("toast-container");
  if (!contenedor) {
    contenedor = document.createElement("div");
    contenedor.id = "toast-container";
    contenedor.style.cssText = "position:fixed;bottom:20px;right:20px;z-index:9999;";
    document.body.appendChild(contenedor);
  }
  const toast = document.createElement("div");
  toast.className = "toast show align-items-center text-dark bg-brand-yellow border-0 mb-2";
  toast.innerHTML = `<div class="d-flex"><div class="toast-body fw-bold">${texto}</div><button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast"></button></div>`;
  contenedor.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 400);
  }, 3000);
}
