/* =====================================================================
   Archivo:  prototipo/js/entrega.js
   Proyecto: FacturApp

   Qué hace (solo en entrega-nueva.html):
     1. Agrega y quita filas de repuestos con el botón "Agregar repuesto".
     2. Muestra el stock disponible del repuesto elegido en cada fila.
     3. Revisa los datos antes de confirmar:
          - que haya un contratista (HU-17);
          - que haya al menos un repuesto con cantidad (RN-15);
          - que la cantidad sea mayor que cero (RN-11) y entera si el
            repuesto se cuenta en unidades (RN-12);
          - que la cantidad no supere el stock disponible (RN-10).
        Si algo falla, muestra el error junto al campo y no deja confirmar.
     4. Si todo está bien, pide confirmación y lleva a remision.html con
        los datos de la entrega.

   Conceptos:
     - <template>: un molde de HTML que no se ve; se copia con cloneNode.
     - sessionStorage: una pequeña memoria del navegador que dura mientras
       la pestaña esté abierta. Aquí pasa los datos a remision.html.
       En el sistema real, esos datos los guarda la API en la base de datos.
     - Number(): convierte un texto en número.
   ===================================================================== */

(function () {
  "use strict";

  // Repuestos de ejemplo (database/seed.sql). "disponible" = stock en
  // almacén menos lo apartado para otras solicitudes.
  var REPUESTOS = [
    { id: 1, codigo: "COM-001", nombre: "Compresor hermético 1/2 HP R134a", unidad: "unidad", disponible: 9 },
    { id: 2, codigo: "COM-002", nombre: "Compresor hermético 1/3 HP R600a", unidad: "unidad", disponible: 6 },
    { id: 3, codigo: "VAL-001", nombre: "Válvula de expansión termostática", unidad: "unidad", disponible: 23 },
    { id: 4, codigo: "VAL-002", nombre: "Válvula solenoide 1/4\"", unidad: "unidad", disponible: 10 },
    { id: 7, codigo: "VAL-003", nombre: "Válvula de servicio 1/4\"", unidad: "unidad", disponible: 0 },
    { id: 5, codigo: "MOT-001", nombre: "Motor ventilador condensador 9 W", unidad: "unidad", disponible: 12 },
    { id: 6, codigo: "MOT-002", nombre: "Motor ventilador evaporador 5 W", unidad: "unidad", disponible: 15 }
  ];

  // Elementos de la página que vamos a usar.
  var formulario = document.getElementById("form-entrega");
  var cuerpoTabla = document.getElementById("filas-repuestos");
  var molde = document.getElementById("molde-fila");
  var botonAgregar = document.getElementById("agregar-repuesto");
  var selectContratista = document.getElementById("contratista");
  var errorFilas = document.getElementById("error-filas");
  var dialogo = document.getElementById("dialogo-entrega");
  var contadorFilas = 0; // sirve para dar un id distinto a cada campo

  // Busca un repuesto de la lista por su id.
  function buscarRepuesto(id) {
    for (var i = 0; i < REPUESTOS.length; i++) {
      if (String(REPUESTOS[i].id) === String(id)) return REPUESTOS[i];
    }
    return null;
  }

  // Pone o quita el mensaje de error de un campo (.ui-campo).
  function marcarError(campo, mensaje) {
    var contenedor = campo.closest(".ui-campo");
    var error = contenedor.querySelector(".ui-campo__error");
    contenedor.classList.toggle("ui-campo--error", mensaje !== "");
    error.textContent = mensaje;
    campo.setAttribute("aria-invalid", mensaje !== "" ? "true" : "false");
  }

  // En cada fila, deshabilita los repuestos ya elegidos en otras filas,
  // para que un repuesto no se repita en la misma entrega.
  function actualizarOpciones() {
    var elegidos = [];
    cuerpoTabla.querySelectorAll("[data-repuesto]").forEach(function (select) {
      if (select.value) elegidos.push(select.value);
    });
    cuerpoTabla.querySelectorAll("[data-repuesto]").forEach(function (select) {
      select.querySelectorAll("option").forEach(function (opcion) {
        opcion.disabled = opcion.value !== "" && opcion.value !== select.value && elegidos.indexOf(opcion.value) !== -1;
      });
    });
  }

  // Crea una fila nueva a partir del molde.
  function agregarFila() {
    contadorFilas++;
    // content.firstElementChild es el <tr> del molde; true = copiar todo su interior.
    var fila = molde.content.firstElementChild.cloneNode(true);
    var select = fila.querySelector("[data-repuesto]");
    var cantidad = fila.querySelector("[data-cantidad]");

    // Cada campo necesita un id único para conectar su etiqueta (RNF-11).
    select.id = "repuesto-" + contadorFilas;
    cantidad.id = "cantidad-" + contadorFilas;
    fila.querySelector("[data-etiqueta-repuesto]").setAttribute("for", select.id);
    fila.querySelector("[data-etiqueta-cantidad]").setAttribute("for", cantidad.id);

    // Llena la lista de repuestos.
    REPUESTOS.forEach(function (repuesto) {
      var opcion = document.createElement("option");
      opcion.value = repuesto.id;
      opcion.textContent = repuesto.codigo + " · " + repuesto.nombre;
      select.appendChild(opcion);
    });

    // Al elegir un repuesto se muestra su stock disponible.
    select.addEventListener("change", function () {
      var repuesto = buscarRepuesto(select.value);
      fila.querySelector("[data-stock]").textContent = repuesto ? repuesto.disponible : "—";
      actualizarOpciones();
      if (select.getAttribute("aria-invalid") === "true") validarFila(fila);
    });

    // Al escribir la cantidad, si ya había un error, se vuelve a revisar.
    cantidad.addEventListener("input", function () {
      if (cantidad.getAttribute("aria-invalid") === "true") validarFila(fila);
    });

    // Botón "Quitar": borra la fila de la tabla.
    fila.querySelector("[data-quitar]").addEventListener("click", function () {
      fila.remove();
      actualizarOpciones();
    });

    cuerpoTabla.appendChild(fila);
    // Pone el nombre de cada columna en las celdas nuevas, para la vista de celular.
    if (window.etiquetarTablas) window.etiquetarTablas();
    actualizarOpciones();
    select.focus();
  }

  // Revisa una fila y devuelve true si está bien.
  function validarFila(fila) {
    var select = fila.querySelector("[data-repuesto]");
    var campoCantidad = fila.querySelector("[data-cantidad]");
    var repuesto = buscarRepuesto(select.value);
    var texto = campoCantidad.value.trim().replace(",", "."); // acepta 2,5 o 2.5
    var numero = Number(texto);
    var bien = true;

    if (!repuesto) {
      marcarError(select, "Seleccione el repuesto.");
      bien = false;
    } else {
      marcarError(select, "");
    }

    var mensaje = "";
    if (texto === "" || isNaN(numero) || numero <= 0) {
      mensaje = "La cantidad debe ser mayor que cero.";
    } else if (repuesto && repuesto.unidad === "unidad" && !Number.isInteger(numero)) {
      mensaje = "Este repuesto se maneja en unidades enteras. Escriba una cantidad sin decimales.";
    } else if (repuesto && numero > repuesto.disponible) {
      mensaje = "No hay stock suficiente de " + repuesto.codigo + ". Disponible: " + repuesto.disponible + ".";
    }
    marcarError(campoCantidad, mensaje);
    if (mensaje !== "") bien = false;

    return bien;
  }

  // Revisa todo el formulario y devuelve true si se puede confirmar.
  function validarTodo() {
    var bien = true;

    marcarError(selectContratista, selectContratista.value === "" ? "Seleccione el contratista." : "");
    if (selectContratista.value === "") bien = false;

    var filas = cuerpoTabla.querySelectorAll("tr");
    if (filas.length === 0) {
      errorFilas.textContent = "Indique la cantidad a entregar de al menos un repuesto.";
      errorFilas.style.display = "block";
      bien = false;
    } else {
      errorFilas.textContent = "";
      errorFilas.style.display = "none";
    }

    filas.forEach(function (fila) {
      if (!validarFila(fila)) bien = false;
    });

    return bien;
  }

  // Al quitar el error del contratista cuando se elige uno.
  selectContratista.addEventListener("change", function () {
    if (selectContratista.getAttribute("aria-invalid") === "true") {
      marcarError(selectContratista, selectContratista.value === "" ? "Seleccione el contratista." : "");
    }
  });

  botonAgregar.addEventListener("click", agregarFila);

  // "Confirmar entrega": si hay errores, se queda en la página; si no, pide confirmación.
  formulario.addEventListener("submit", function (evento) {
    evento.preventDefault();
    if (!validarTodo()) {
      // Lleva el foco al primer campo con error, para que se vea.
      var primerError = formulario.querySelector("[aria-invalid='true']");
      if (primerError) primerError.focus();
      return;
    }
    var total = cuerpoTabla.querySelectorAll("tr").length;
    var nombreContratista = selectContratista.options[selectContratista.selectedIndex].text.split(" · ")[0];
    document.getElementById("resumen-entrega").textContent =
      (total === 1 ? "Se entregará 1 repuesto" : "Se entregarán " + total + " repuestos distintos") +
      " a " + nombreContratista + ".";
    dialogo.showModal();
  });

  // Botón del diálogo: guarda los datos y va a la remisión.
  document.getElementById("confirmar-entrega").addEventListener("click", function () {
    var opcion = selectContratista.options[selectContratista.selectedIndex];
    var entrega = {
      numero: "REM-000003", // la siguiente remisión según los datos de ejemplo
      fecha: new Date().toLocaleString("es-CO", { dateStyle: "short", timeStyle: "short" }),
      contratista: opcion.text.split(" · ")[0],
      documento: opcion.dataset.documento,
      usuario: "Administrador del sistema",
      repuestos: []
    };
    cuerpoTabla.querySelectorAll("tr").forEach(function (fila) {
      var repuesto = buscarRepuesto(fila.querySelector("[data-repuesto]").value);
      entrega.repuestos.push({
        codigo: repuesto.codigo,
        nombre: repuesto.nombre,
        unidad: repuesto.unidad,
        cantidad: fila.querySelector("[data-cantidad]").value.trim()
      });
    });

    // try/catch: si el navegador no deja usar sessionStorage, la remisión
    // muestra sus datos de ejemplo y el prototipo sigue funcionando.
    try {
      sessionStorage.setItem("facturapp-entrega", JSON.stringify(entrega));
    } catch (error) {
      // No se pudo guardar; no pasa nada.
    }
    window.location.href = "remision.html";
  });

  // La página empieza con una fila lista para llenar.
  agregarFila();
  // El foco inicial va al contratista, el primer campo del formulario.
  selectContratista.focus();
})();
