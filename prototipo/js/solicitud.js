/* =====================================================================
   Archivo:  prototipo/js/solicitud.js
   Proyecto: FacturApp

   Qué hace (en solicitud-nueva.html y solicitud-editar.html):
     1. Agrega y quita filas de repuestos con "Agregar repuesto".
     2. Revisa los datos antes de guardar (HU-17):
          - equipo y contratista elegidos (RN-14);
          - fecha de entrega que no sea anterior a hoy (RN-14);
          - al menos un repuesto, sin repetir (RN-15);
          - cantidad mayor que cero y entera si el repuesto se cuenta
            en unidades (RN-11, RN-12).
        El error aparece junto al campo y no se guarda nada.
     3. Si todo está bien, deja un aviso y lleva a la lista de solicitudes.

   La solicitud NO muestra el stock: la Oficina radicadora no puede verlo
   (RN-02). Si no hay stock suficiente, lo que falta queda "En espera"
   (RN-33); eso lo calcula el sistema al guardar.

   Conceptos:
     - dataset.filasIniciales: lee el atributo data-filas-iniciales del
       formulario; en "Editar" trae las filas que ya tenía la solicitud.
     - JSON.parse: convierte ese texto en una lista de datos.
   ===================================================================== */

(function () {
  "use strict";

  // Catálogo de repuestos activos (datos de ejemplo de database/seed.sql).
  var REPUESTOS = [
    { id: 1, codigo: "COM-001", nombre: "Compresor hermético 1/2 HP R134a", unidad: "unidad" },
    { id: 2, codigo: "COM-002", nombre: "Compresor hermético 1/3 HP R600a", unidad: "unidad" },
    { id: 3, codigo: "VAL-001", nombre: "Válvula de expansión termostática", unidad: "unidad" },
    { id: 4, codigo: "VAL-002", nombre: "Válvula solenoide 1/4\"", unidad: "unidad" },
    { id: 7, codigo: "VAL-003", nombre: "Válvula de servicio 1/4\"", unidad: "unidad" },
    { id: 5, codigo: "MOT-001", nombre: "Motor ventilador condensador 9 W", unidad: "unidad" },
    { id: 6, codigo: "MOT-002", nombre: "Motor ventilador evaporador 5 W", unidad: "unidad" }
  ];

  var formulario = document.getElementById("form-solicitud");
  var cuerpoTabla = document.getElementById("filas-repuestos");
  var molde = document.getElementById("molde-fila");
  var errorFilas = document.getElementById("error-filas");
  var campoFecha = document.getElementById("fecha");
  var contador = 0;

  // Fecha de hoy en formato aaaa-mm-dd, el que usa <input type="date">.
  function hoy() {
    var fecha = new Date();
    var mes = String(fecha.getMonth() + 1).padStart(2, "0");
    var dia = String(fecha.getDate()).padStart(2, "0");
    return fecha.getFullYear() + "-" + mes + "-" + dia;
  }
  // El calendario no deja elegir días anteriores a hoy.
  campoFecha.min = hoy();

  function buscarRepuesto(id) {
    return REPUESTOS.filter(function (r) { return String(r.id) === String(id); })[0] || null;
  }

  // Pone o quita el error de un campo.
  function marcarError(campo, mensaje) {
    var contenedor = campo.closest(".ui-campo");
    contenedor.classList.toggle("ui-campo--error", mensaje !== "");
    contenedor.querySelector(".ui-campo__error").textContent = mensaje;
    campo.setAttribute("aria-invalid", mensaje !== "" ? "true" : "false");
  }

  // Un repuesto no se repite: en cada lista se deshabilitan los ya elegidos en otras filas.
  function actualizarOpciones() {
    var elegidos = [];
    cuerpoTabla.querySelectorAll("[data-repuesto]").forEach(function (s) { if (s.value) elegidos.push(s.value); });
    cuerpoTabla.querySelectorAll("[data-repuesto]").forEach(function (s) {
      s.querySelectorAll("option").forEach(function (o) {
        o.disabled = o.value !== "" && o.value !== s.value && elegidos.indexOf(o.value) !== -1;
      });
    });
  }

  // Agrega una fila; si se le pasan datos (al editar), la llena.
  function agregarFila(datos) {
    contador++;
    var fila = molde.content.firstElementChild.cloneNode(true);
    var select = fila.querySelector("[data-repuesto]");
    var cantidad = fila.querySelector("[data-cantidad]");
    select.id = "repuesto-" + contador;
    cantidad.id = "cantidad-" + contador;
    fila.querySelector("[data-etiqueta-repuesto]").setAttribute("for", select.id);
    fila.querySelector("[data-etiqueta-cantidad]").setAttribute("for", cantidad.id);

    REPUESTOS.forEach(function (r) {
      var opcion = document.createElement("option");
      opcion.value = r.id;
      opcion.textContent = r.codigo + " · " + r.nombre;
      select.appendChild(opcion);
    });

    if (datos) {
      select.value = datos.id;
      cantidad.value = datos.cantidad;
    }

    select.addEventListener("change", actualizarOpciones);
    fila.querySelector("[data-quitar]").addEventListener("click", function () {
      fila.remove();
      actualizarOpciones();
    });

    cuerpoTabla.appendChild(fila);
    if (window.etiquetarTablas) window.etiquetarTablas();
    // Lista de más de 5 repuestos: se le agrega el buscador (regla del proyecto).
    if (window.mejorarSelects) window.mejorarSelects(fila);
    actualizarOpciones();
    if (!datos) select.focus();
  }

  // Revisa todo el formulario; devuelve true si se puede guardar.
  function validar() {
    var bien = true;

    ["equipo", "contratista"].forEach(function (id) {
      var campo = document.getElementById(id);
      var mensaje = campo.value === "" ? (id === "equipo" ? "Seleccione el equipo." : "Seleccione el contratista.") : "";
      marcarError(campo, mensaje);
      if (mensaje) bien = false;
    });

    var mensajeFecha = "";
    if (campoFecha.value === "") mensajeFecha = "Escriba la fecha de entrega.";
    else if (campoFecha.value < hoy()) mensajeFecha = "La fecha de entrega no puede ser anterior a hoy.";
    marcarError(campoFecha, mensajeFecha);
    if (mensajeFecha) bien = false;

    var filas = cuerpoTabla.querySelectorAll("tr");
    errorFilas.textContent = filas.length === 0 ? "Agregue al menos un repuesto." : "";
    errorFilas.style.display = filas.length === 0 ? "block" : "none";
    if (filas.length === 0) bien = false;

    filas.forEach(function (fila) {
      var select = fila.querySelector("[data-repuesto]");
      var campoCantidad = fila.querySelector("[data-cantidad]");
      var repuesto = buscarRepuesto(select.value);
      var numero = Number(campoCantidad.value.trim().replace(",", "."));

      marcarError(select, repuesto ? "" : "Seleccione el repuesto.");
      if (!repuesto) bien = false;

      var mensaje = "";
      if (campoCantidad.value.trim() === "" || isNaN(numero) || numero <= 0) {
        mensaje = "La cantidad debe ser mayor que cero.";
      } else if (repuesto && repuesto.unidad === "unidad" && !Number.isInteger(numero)) {
        mensaje = "Este repuesto se maneja en unidades enteras. Escriba una cantidad sin decimales.";
      }
      marcarError(campoCantidad, mensaje);
      if (mensaje) bien = false;
    });

    return bien;
  }

  document.getElementById("agregar-repuesto").addEventListener("click", function () { agregarFila(); });

  formulario.addEventListener("submit", function (evento) {
    evento.preventDefault();
    if (!validar()) {
      var primero = formulario.querySelector("[aria-invalid='true']");
      if (primero) primero.focus();
      return;
    }
    try {
      sessionStorage.setItem("facturapp-aviso", formulario.dataset.mensaje);
    } catch (error) {
      // Sin sessionStorage la lista se abre sin aviso.
    }
    window.location.href = formulario.dataset.destino;
  });

  // Filas iniciales: las de la solicitud que se edita, o una vacía si es nueva.
  var iniciales = [];
  try {
    iniciales = JSON.parse(formulario.dataset.filasIniciales || "[]");
  } catch (error) {
    iniciales = [];
  }
  if (iniciales.length) {
    iniciales.forEach(function (datos) { agregarFila(datos); });
  } else {
    agregarFila();
  }
})();
