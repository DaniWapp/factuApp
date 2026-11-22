/* =====================================================================
   Archivo:  prototipo/js/prototipo.js
   Proyecto: FacturApp

   Qué es:
     El JavaScript común de las páginas del prototipo. Hace que funcionen:
       1. El botón "Menú" que abre la barra lateral en el celular.
       2. El menú del usuario ("Mi cuenta", "Cerrar sesión").
       3. El interruptor "Vista de usuario" del Admin.
       4. Los diálogos (ventanas de confirmación).
       5. El botón "Copiar" de la contraseña temporal.
       6. El inicio de sesión de prueba.
       7. Las acciones Activar y Desactivar de la tabla de usuarios.
       8. El buscador de las tablas.
       9. El formulario para cambiar la contraseña.

   Cómo se usa:
     Se carga al final de cada página:
       <script src="js/prototipo.js"></script>
     El HTML "pide" cada comportamiento con atributos data-, por ejemplo
     data-abrir-dialogo="dialogo-desactivar". Así este archivo sirve
     para todas las páginas sin cambiarlo.

   Por qué no es un módulo (type="module"):
     El prototipo se abre con doble clic (file://) y los navegadores no
     permiten módulos así. En el sistema real, que lo sirve Flask, sí se
     usarán módulos (ES modules), como dice CLAUDE.md.

   Conceptos:
     - document.querySelector / querySelectorAll: buscan elementos del HTML.
     - addEventListener("click", función): ejecuta la función al hacer clic.
     - dataset: lee los atributos data- (data-fila se lee como dataset.fila).
     - <dialog>: ventana del navegador; showModal() la abre y close() la cierra.
   ===================================================================== */

// Todo va dentro de una función que se ejecuta sola, para que las
// variables de este archivo no choquen con las de otros archivos.
(function () {
  "use strict";

  /* -------------------------------------------------------------------
     1. Menú lateral en el celular
     El botón con data-abrir-menu agrega o quita la clase
     ui-app--menu-abierto, que hace visible la barra lateral (ver ui.css).
     ------------------------------------------------------------------- */
  var app = document.querySelector(".ui-app");
  var botonMenu = document.querySelector("[data-abrir-menu]");

  // Abre o cierra el menú y avisa su estado a los lectores de pantalla.
  function cambiarMenu(abrir) {
    if (!app || !botonMenu) return;
    app.classList.toggle("ui-app--menu-abierto", abrir);
    botonMenu.setAttribute("aria-expanded", abrir ? "true" : "false");
  }

  if (botonMenu) {
    botonMenu.addEventListener("click", function () {
      var estaAbierto = app.classList.contains("ui-app--menu-abierto");
      cambiarMenu(!estaAbierto);
    });
  }

  // La tecla Esc cierra el menú lateral y el menú del usuario.
  document.addEventListener("keydown", function (evento) {
    if (evento.key === "Escape") {
      cambiarMenu(false);
      cerrarDesplegables();
    }
  });

  /* -------------------------------------------------------------------
     2. Menú del usuario (<details class="ui-desplegable">)
     El navegador lo abre y lo cierra solo; aquí solo se cierra cuando
     se hace clic fuera de él.
     ------------------------------------------------------------------- */
  function cerrarDesplegables() {
    document.querySelectorAll(".ui-desplegable[open]").forEach(function (menu) {
      menu.removeAttribute("open");
    });
  }

  document.addEventListener("click", function (evento) {
    // closest() busca si el clic fue dentro de un menú desplegable.
    if (!evento.target.closest(".ui-desplegable")) {
      cerrarDesplegables();
    }
  });

  /* -------------------------------------------------------------------
     3. Interruptor "Vista de usuario" (solo en las páginas del Admin)
     Al encenderlo se ocultan las opciones con data-solo-admin y aparece
     el aviso "Está viendo el sistema como Oficina radicadora" (HU-06).
     ------------------------------------------------------------------- */
  var interruptor = document.querySelector("[data-vista-usuario]");
  var avisoVista = document.getElementById("aviso-vista");

  function cambiarVista(comoUsuario) {
    interruptor.setAttribute("aria-checked", comoUsuario ? "true" : "false");
    document.querySelectorAll("[data-solo-admin]").forEach(function (elemento) {
      elemento.hidden = comoUsuario;
    });
    if (avisoVista) avisoVista.hidden = !comoUsuario;
  }

  if (interruptor) {
    interruptor.addEventListener("click", function () {
      var encendido = interruptor.getAttribute("aria-checked") === "true";
      cambiarVista(!encendido);
    });
    // El botón "Volver a la vista de Admin" del aviso también apaga el interruptor.
    document.querySelectorAll("[data-volver-admin]").forEach(function (boton) {
      boton.addEventListener("click", function () { cambiarVista(false); });
    });
  }

  /* -------------------------------------------------------------------
     4. Diálogos
     Un botón con data-abrir-dialogo="id" abre el <dialog> con ese id.
     Un botón con data-cerrar-dialogo cierra el diálogo donde está.
     ------------------------------------------------------------------- */
  document.querySelectorAll("[data-abrir-dialogo]").forEach(function (boton) {
    boton.addEventListener("click", function () {
      var dialogo = document.getElementById(boton.dataset.abrirDialogo);
      if (!dialogo) return;
      // Guardamos qué botón abrió el diálogo, para saber sobre qué fila actuar.
      dialogo.botonQueAbrio = boton;
      // Si el botón trae un nombre (data-nombre), se escribe en el diálogo.
      dialogo.querySelectorAll("[data-nombre-destino]").forEach(function (espacio) {
        espacio.textContent = boton.dataset.nombre || "";
      });
      dialogo.showModal();
    });
  });

  document.querySelectorAll("[data-cerrar-dialogo]").forEach(function (boton) {
    boton.addEventListener("click", function () {
      boton.closest("dialog").close();
    });
  });

  /* -------------------------------------------------------------------
     5. Botón "Copiar"
     Copia el texto del elemento cuyo id indica data-copiar. Si el
     navegador no deja copiar, selecciona el texto para usar Ctrl + C.
     ------------------------------------------------------------------- */
  document.querySelectorAll("[data-copiar]").forEach(function (boton) {
    boton.addEventListener("click", function () {
      var texto = document.getElementById(boton.dataset.copiar);
      var textoOriginal = boton.textContent;

      function avisar(mensaje) {
        boton.textContent = mensaje;
        setTimeout(function () { boton.textContent = textoOriginal; }, 2000);
      }

      function seleccionar() {
        var rango = document.createRange();
        rango.selectNodeContents(texto);
        var seleccion = window.getSelection();
        seleccion.removeAllRanges();
        seleccion.addRange(rango);
        avisar("Pulse Ctrl + C");
      }

      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(texto.textContent).then(function () {
          avisar("Copiada");
        }, seleccionar);
      } else {
        seleccionar();
      }
    });
  });

  /* -------------------------------------------------------------------
     6. Inicio de sesión de prueba (login.html)
     No hay servidor: si faltan datos se muestra el error de HU-01; si el
     correo contiene "oficina" entra como Oficina radicadora, y si no,
     como Admin.
     ------------------------------------------------------------------- */
  var formularioLogin = document.querySelector("[data-login]");

  if (formularioLogin) {
    formularioLogin.addEventListener("submit", function (evento) {
      // preventDefault() evita que el formulario recargue la página.
      evento.preventDefault();
      var correo = formularioLogin.correo.value.trim();
      var clave = formularioLogin.contrasena.value;
      var avisoError = document.getElementById("error-login");

      if (correo === "" || clave === "") {
        avisoError.innerHTML = "<strong>No se pudo entrar.</strong> Escriba su correo y su contraseña.";
        avisoError.hidden = false;
        return;
      }
      // indexOf devuelve -1 cuando el texto no contiene la palabra buscada.
      var destino = correo.toLowerCase().indexOf("oficina") !== -1 ? "panel-usuario.html" : "panel-admin.html";
      window.location.href = destino;
    });
  }

  /* -------------------------------------------------------------------
     7. Activar y desactivar usuarios (usuarios.html)
     El botón "Desactivar" abre el diálogo de confirmación; al confirmar,
     la fila cambia a "Inactivo" y su acción pasa a ser "Activar".
     "Activar" cambia la fila directamente.
     ------------------------------------------------------------------- */
  // Cambia la insignia y el botón de una fila de la tabla de usuarios.
  function cambiarEstadoFila(fila, activo) {
    var insignia = fila.querySelector(".ui-insignia");
    var boton = fila.querySelector("[data-accion-estado]");
    insignia.textContent = activo ? "Activo" : "Inactivo";
    insignia.className = "ui-insignia " + (activo ? "ui-insignia--exito" : "ui-insignia--neutra");
    boton.textContent = activo ? "Desactivar" : "Activar";
    boton.classList.toggle("ui-boton--peligro", activo);
  }

  // Botón "Desactivar" del diálogo: confirma la acción.
  var confirmarDesactivar = document.querySelector("[data-confirmar-desactivar]");
  if (confirmarDesactivar) {
    confirmarDesactivar.addEventListener("click", function () {
      var dialogo = confirmarDesactivar.closest("dialog");
      var fila = dialogo.botonQueAbrio.closest("tr");
      cambiarEstadoFila(fila, false);
      dialogo.close();
      mostrarAviso("<strong>Usuario desactivado.</strong> Ya no puede iniciar sesión.");
    });
  }

  // Botón de estado de cada fila: "Activar" cambia la fila de inmediato;
  // "Desactivar" primero abre el diálogo de confirmación.
  document.querySelectorAll("[data-accion-estado]").forEach(function (boton) {
    boton.addEventListener("click", function () {
      if (boton.textContent.trim() === "Activar") {
        cambiarEstadoFila(boton.closest("tr"), true);
        mostrarAviso("<strong>Usuario activado.</strong> Ya puede iniciar sesión.");
        return;
      }
      var dialogo = document.getElementById("dialogo-desactivar");
      dialogo.botonQueAbrio = boton;
      dialogo.querySelectorAll("[data-nombre-destino]").forEach(function (espacio) {
        espacio.textContent = boton.dataset.nombre || "";
      });
      dialogo.showModal();
    });
  });

  // Muestra un aviso de éxito en el espacio con id "aviso-pagina".
  function mostrarAviso(html) {
    var aviso = document.getElementById("aviso-pagina");
    if (!aviso) return;
    aviso.innerHTML = html;
    aviso.hidden = false;
  }

  /* -------------------------------------------------------------------
     8. Buscador de tablas (repuestos.html)
     Un campo con data-filtrar="id-de-la-tabla" oculta las filas que no
     contienen el texto escrito. Sin mayúsculas ni tildes: "valvula"
     encuentra "Válvula".
     ------------------------------------------------------------------- */
  // Quita tildes y pasa a minúsculas para comparar textos.
  function normalizar(texto) {
    return texto.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  }

  document.querySelectorAll("[data-filtrar]").forEach(function (campo) {
    campo.addEventListener("input", function () {
      var buscado = normalizar(campo.value.trim());
      var tabla = document.getElementById(campo.dataset.filtrar);
      tabla.querySelectorAll("tbody tr").forEach(function (fila) {
        fila.hidden = normalizar(fila.textContent).indexOf(buscado) === -1;
      });
    });
  });

  /* -------------------------------------------------------------------
     9. Cambiar la contraseña (mi-cuenta.html)
     Revisa las reglas RN-03 (mínimo 8 caracteres) y que la confirmación
     coincida. Muestra el error junto al campo, como pide RNF-08.
     ------------------------------------------------------------------- */
  var formularioClave = document.querySelector("[data-form-clave]");

  if (formularioClave) {
    formularioClave.addEventListener("submit", function (evento) {
      evento.preventDefault();
      var actual = formularioClave.actual;
      var nueva = formularioClave.nueva;
      var confirmacion = formularioClave.confirmacion;
      var hayError = false;

      // Pone o quita el error de un campo.
      function marcar(campo, mensaje) {
        var contenedor = campo.closest(".ui-campo");
        contenedor.classList.toggle("ui-campo--error", mensaje !== "");
        contenedor.querySelector(".ui-campo__error").textContent = mensaje;
        campo.setAttribute("aria-invalid", mensaje !== "" ? "true" : "false");
        if (mensaje !== "") hayError = true;
      }

      marcar(actual, actual.value === "" ? "Escriba su contraseña actual." : "");
      marcar(nueva, nueva.value.length < 8 ? "La contraseña nueva debe tener al menos 8 caracteres." : "");
      marcar(confirmacion, confirmacion.value !== nueva.value ? "Las contraseñas nuevas no coinciden." : "");

      var aviso = document.getElementById("aviso-pagina");
      if (!hayError) {
        formularioClave.reset();
        mostrarAviso("<strong>Contraseña actualizada.</strong>");
      } else if (aviso) {
        aviso.hidden = true;
      }
    });
  }
})();
