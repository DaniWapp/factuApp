/* =====================================================================
   Archivo:  prototipo/js/remision.js
   Proyecto: FacturApp

   Qué hace (solo en remision.html):
     1. Si se llegó desde "Nueva entrega", muestra los datos de esa
        entrega (guardados en sessionStorage) y el aviso "Entrega
        registrada". Si no, deja los datos de ejemplo de la remisión
        REM-000001.
     2. El botón "Imprimir" abre la ventana de impresión del navegador.
        Los estilos de impresión están en css/impresion.css.

   Conceptos:
     - JSON.parse: convierte el texto guardado otra vez en datos.
     - textContent: escribe texto en un elemento sin interpretar HTML,
       lo que evita que un dato con símbolos raros dañe la página.
     - window.print(): abre la ventana de impresión.
   ===================================================================== */

(function () {
  "use strict";

  // Botón "Imprimir".
  var botonImprimir = document.querySelector("[data-imprimir]");
  if (botonImprimir) {
    botonImprimir.addEventListener("click", function () {
      window.print();
    });
  }

  // Lee la entrega guardada por entrega-nueva.html, si existe.
  var entrega = null;
  try {
    var texto = sessionStorage.getItem("facturapp-entrega");
    if (texto) {
      entrega = JSON.parse(texto);
      // Se borra para que, al recargar, no vuelva a salir el aviso.
      sessionStorage.removeItem("facturapp-entrega");
    }
  } catch (error) {
    entrega = null;
  }

  if (!entrega) return; // sin entrega nueva: se quedan los datos de ejemplo

  // Llena los datos de la remisión.
  document.getElementById("rem-numero").textContent = entrega.numero;
  document.getElementById("rem-fecha").textContent = entrega.fecha;
  document.getElementById("rem-usuario").textContent = entrega.usuario;
  document.getElementById("rem-contratista").textContent = entrega.contratista;
  document.getElementById("rem-documento").textContent = entrega.documento;

  // Vuelve a armar la tabla con los repuestos de la entrega.
  var cuerpo = document.getElementById("rem-filas");
  cuerpo.textContent = "";
  entrega.repuestos.forEach(function (repuesto) {
    var fila = document.createElement("tr");
    [
      { texto: repuesto.codigo, clase: "ui-codigo" },
      { texto: repuesto.nombre, clase: "" },
      { texto: repuesto.unidad, clase: "" },
      { texto: repuesto.cantidad, clase: "ui-tabla__num" }
    ].forEach(function (dato) {
      var celda = document.createElement("td");
      celda.textContent = dato.texto;
      if (dato.clase) celda.className = dato.clase;
      fila.appendChild(celda);
    });
    cuerpo.appendChild(fila);
  });
  // Pone el nombre de cada columna en las celdas nuevas, para la vista de celular.
  if (window.etiquetarTablas) window.etiquetarTablas();

  // Aviso de éxito con el mensaje de HU-21.
  var aviso = document.getElementById("aviso-remision");
  aviso.innerHTML = "<strong>Entrega registrada.</strong> ";
  aviso.appendChild(document.createTextNode("Remisión " + entrega.numero + " generada."));
  aviso.hidden = false;
})();
