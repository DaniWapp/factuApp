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
      10. Las etiquetas de las tablas para verlas en el celular.
      11. El botón Confirmar de los diálogos.
      12. El selector con buscador (listas de más de 5 opciones).
      13. Los avisos que llegan desde otra página.

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
      // Regla RN-03: al menos 8 caracteres, con letras y números.
      var tieneLetra = /\p{L}/u.test(nueva.value);
      var tieneNumero = /\d/.test(nueva.value);
      marcar(nueva, nueva.value.length < 8 ? "La contraseña debe tener al menos 8 caracteres." :
        (!tieneLetra || !tieneNumero) ? "La contraseña debe tener letras y números." : "");
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

  /* -------------------------------------------------------------------
     10. Etiquetas de las tablas para el celular
     En pantallas angostas cada fila de una tabla se muestra como un
     bloque, y cada dato lleva a su izquierda el nombre de su columna
     (ver ui.css, sección 5). Ese nombre se toma del encabezado <th> y
     se copia en el atributo data-etiqueta de cada celda, para no tener
     que escribirlo a mano en cada <td>.
     Se deja disponible como window.etiquetarTablas para que otros
     archivos (entrega.js, remision.js) lo llamen después de agregar filas.
     ------------------------------------------------------------------- */
  function etiquetarTablas() {
    document.querySelectorAll(".ui-tabla").forEach(function (tabla) {
      var titulos = [];
      tabla.querySelectorAll("thead th").forEach(function (th) {
        titulos.push(th.textContent.trim());
      });
      tabla.querySelectorAll("tbody tr").forEach(function (fila) {
        // children son las celdas de la fila, en orden.
        Array.prototype.forEach.call(fila.children, function (celda, posicion) {
          var titulo = titulos[posicion];
          if (titulo && !celda.hasAttribute("data-etiqueta")) {
            celda.setAttribute("data-etiqueta", titulo);
          }
        });
      });
    });
  }

  etiquetarTablas();
  window.etiquetarTablas = etiquetarTablas;

  /* -------------------------------------------------------------------
     11. Botón "Confirmar" de los diálogos
     Un botón con data-confirmar dentro de un <dialog>:
       - revisa que los campos con data-obligatorio no estén vacíos; si
         alguno lo está, muestra su error y no cierra el diálogo;
       - si todo está bien, cierra el diálogo y muestra el aviso de
         éxito con el texto de data-mensaje.
     Es solo una simulación: no se guarda nada.
     ------------------------------------------------------------------- */
  document.querySelectorAll("[data-confirmar]").forEach(function (boton) {
    boton.addEventListener("click", function () {
      var dialogo = boton.closest("dialog");
      var faltaAlgo = false;

      dialogo.querySelectorAll("[data-obligatorio]").forEach(function (campo) {
        var vacio = campo.value.trim() === "";
        var contenedor = campo.closest(".ui-campo");
        contenedor.classList.toggle("ui-campo--error", vacio);
        campo.setAttribute("aria-invalid", vacio ? "true" : "false");
        if (vacio && !faltaAlgo) campo.focus();
        if (vacio) faltaAlgo = true;
      });
      if (faltaAlgo) return;

      dialogo.close();
      // Deja el diálogo limpio para la próxima vez.
      dialogo.querySelectorAll("textarea, input:not([type=radio]), select").forEach(function (campo) {
        campo.value = "";
      });
      mostrarAviso(boton.dataset.mensaje || "<strong>Listo.</strong>");
    });
  });

  /* -------------------------------------------------------------------
     12. Selector con buscador
     REGLA del proyecto: toda lista desplegable (<select>) con más de 5
     opciones lleva un buscador. Esta función busca esos <select> y los
     convierte en un selector con buscador:
       - el <select> original se esconde, pero sigue guardando el valor
         (así los formularios y las validaciones funcionan igual);
       - aparece un botón con el aspecto de un campo;
       - al abrirlo se ve un buscador y la lista de opciones;
       - con el teclado: flechas para moverse, Enter para elegir, Esc
         para cerrar.
     Se deja disponible como window.mejorarSelects(contenedor) para usarla
     con las filas que se agregan después (entrega.js, solicitud.js).

     Conceptos:
       - role="combobox" / role="listbox" / role="option": le dicen al
         lector de pantalla que es una lista para elegir.
       - aria-activedescendant: indica cuál opción está señalada.
       - dispatchEvent(new Event("change")): avisa que el valor cambió,
         como si la persona hubiera usado el <select> original.
     ------------------------------------------------------------------- */
  var MINIMO_PARA_BUSCADOR = 5;
  var contadorSelectores = 0;

  function mejorarSelects(contenedor) {
    (contenedor || document).querySelectorAll("select.ui-campo__control").forEach(function (select) {
      if (select.dataset.mejorado) return;
      // Solo cuentan las opciones reales, no "Seleccione...".
      var reales = Array.prototype.filter.call(select.options, function (o) { return o.value !== ""; });
      if (reales.length <= MINIMO_PARA_BUSCADOR) return;
      crearSelector(select);
    });
  }

  function crearSelector(select) {
    contadorSelectores++;
    var id = "selector-" + contadorSelectores;
    select.dataset.mejorado = "si";

    // Envoltura que contiene el botón y el panel.
    var envoltura = document.createElement("div");
    envoltura.className = "ui-selector";
    select.parentNode.insertBefore(envoltura, select);
    envoltura.appendChild(select);
    select.classList.add("ui-oculto");
    select.tabIndex = -1;

    // Botón visible: usa las clases del campo para verse igual.
    var boton = document.createElement("button");
    boton.type = "button";
    boton.className = "ui-campo__control ui-selector__boton";
    boton.setAttribute("aria-haspopup", "listbox");
    boton.setAttribute("aria-expanded", "false");
    var textoBoton = document.createElement("span");
    textoBoton.className = "ui-selector__texto";
    boton.appendChild(textoBoton);
    envoltura.insertBefore(boton, select);

    // La etiqueta <label for="..."> del select ahora nombra al botón.
    if (select.id) {
      boton.id = select.id + "-boton";
      document.querySelectorAll('label[for="' + select.id + '"]').forEach(function (etiqueta) {
        etiqueta.setAttribute("for", boton.id);
      });
    }
    var describe = select.getAttribute("aria-describedby");
    if (describe) boton.setAttribute("aria-describedby", describe);

    // Panel con el buscador y la lista.
    var panel = document.createElement("div");
    panel.className = "ui-selector__panel";
    panel.hidden = true;
    var buscador = document.createElement("input");
    buscador.type = "search";
    buscador.className = "ui-campo__control";
    buscador.setAttribute("role", "combobox");
    buscador.setAttribute("aria-expanded", "true");
    buscador.setAttribute("aria-controls", id + "-lista");
    buscador.setAttribute("aria-autocomplete", "list");
    buscador.setAttribute("aria-label", "Buscar");
    buscador.placeholder = "Escriba para buscar";
    var lista = document.createElement("ul");
    lista.className = "ui-selector__lista";
    lista.id = id + "-lista";
    lista.setAttribute("role", "listbox");
    panel.appendChild(buscador);
    panel.appendChild(lista);
    envoltura.appendChild(panel);

    var visibles = [];   // opciones que se ven con el texto buscado
    var senalada = -1;   // posición de la opción señalada con el teclado

    // Escribe en el botón el texto de la opción elegida.
    function actualizarBoton() {
      var elegida = select.options[select.selectedIndex];
      var vacio = !elegida || elegida.value === "";
      textoBoton.textContent = elegida ? elegida.text : "";
      boton.classList.toggle("ui-selector__boton--vacio", vacio);
    }

    // Dibuja las opciones que coinciden con lo escrito en el buscador.
    function dibujarLista() {
      // Cada palabra escrita debe aparecer en la opción, en cualquier orden:
      // "motor cond" encuentra "Motor ventilador condensador".
      var palabras = normalizar(buscador.value.trim()).split(/\s+/).filter(Boolean);
      lista.textContent = "";
      visibles = [];
      Array.prototype.forEach.call(select.options, function (opcion, posicion) {
        if (opcion.value === "") return;
        var texto = normalizar(opcion.text);
        var coincide = palabras.every(function (palabra) { return texto.indexOf(palabra) !== -1; });
        if (!coincide) return;
        var item = document.createElement("li");
        item.className = "ui-selector__opcion";
        item.id = id + "-op-" + posicion;
        item.setAttribute("role", "option");
        item.textContent = opcion.text;
        if (opcion.disabled) item.setAttribute("aria-disabled", "true");
        item.addEventListener("mousedown", function (evento) {
          evento.preventDefault(); // evita que el buscador pierda el foco antes de elegir
          elegir(posicion);
        });
        lista.appendChild(item);
        visibles.push({ item: item, posicion: posicion, deshabilitada: opcion.disabled });
      });
      if (visibles.length === 0) {
        var vacio = document.createElement("li");
        vacio.className = "ui-selector__vacio";
        vacio.textContent = "No hay resultados.";
        lista.appendChild(vacio);
      }
      senalar(visibles.length ? 0 : -1);
    }

    // Señala una opción (fondo suave) y la deja a la vista dentro de la lista.
    function senalar(nueva) {
      visibles.forEach(function (v) { v.item.setAttribute("aria-selected", "false"); });
      senalada = nueva;
      if (nueva >= 0 && visibles[nueva]) {
        visibles[nueva].item.setAttribute("aria-selected", "true");
        visibles[nueva].item.scrollIntoView({ block: "nearest" });
        buscador.setAttribute("aria-activedescendant", visibles[nueva].item.id);
      } else {
        buscador.removeAttribute("aria-activedescendant");
      }
    }

    function abrir() {
      panel.hidden = false;
      boton.setAttribute("aria-expanded", "true");
      buscador.value = "";
      dibujarLista();
      buscador.focus();
    }

    function cerrar(devolverFoco) {
      panel.hidden = true;
      boton.setAttribute("aria-expanded", "false");
      if (devolverFoco) boton.focus();
    }

    // Elige una opción: cambia el <select> original y avisa del cambio.
    function elegir(posicion) {
      var opcion = select.options[posicion];
      if (!opcion || opcion.disabled) return;
      select.selectedIndex = posicion;
      select.dispatchEvent(new Event("change", { bubbles: true }));
      actualizarBoton();
      cerrar(true);
    }

    boton.addEventListener("click", function () {
      if (panel.hidden) abrir(); else cerrar(true);
    });
    // Flecha abajo sobre el botón también abre la lista.
    boton.addEventListener("keydown", function (evento) {
      if (evento.key === "ArrowDown") { evento.preventDefault(); abrir(); }
    });

    buscador.addEventListener("input", dibujarLista);
    buscador.addEventListener("keydown", function (evento) {
      if (evento.key === "ArrowDown") {
        evento.preventDefault();
        senalar(Math.min(senalada + 1, visibles.length - 1));
      } else if (evento.key === "ArrowUp") {
        evento.preventDefault();
        senalar(Math.max(senalada - 1, 0));
      } else if (evento.key === "Enter") {
        evento.preventDefault(); // no envía el formulario
        if (visibles[senalada]) elegir(visibles[senalada].posicion);
      } else if (evento.key === "Escape") {
        evento.preventDefault();
        evento.stopPropagation(); // no cierra el diálogo donde esté el selector
        cerrar(true);
      } else if (evento.key === "Tab") {
        cerrar(false);
      }
    });

    // Un clic fuera del selector lo cierra.
    document.addEventListener("click", function (evento) {
      if (!panel.hidden && !envoltura.contains(evento.target)) cerrar(false);
    });

    // Si otro código cambia el <select> o le da el foco (por ejemplo, al
    // marcar un error), el botón se actualiza o recibe el foco.
    select.addEventListener("change", actualizarBoton);
    select.addEventListener("focus", function () { boton.focus(); });
    // El estado de error del <select> se copia al botón.
    new MutationObserver(function () {
      boton.setAttribute("aria-invalid", select.getAttribute("aria-invalid") || "false");
    }).observe(select, { attributes: true, attributeFilter: ["aria-invalid"] });

    actualizarBoton();
  }

  mejorarSelects(document);
  window.mejorarSelects = mejorarSelects;

  /* -------------------------------------------------------------------
     13. Aviso que viene de otra página
     Cuando una página guarda algo y lleva a otra (por ejemplo, "Nueva
     solicitud" lleva a la lista), deja el texto del aviso en
     sessionStorage; aquí se muestra y se borra.
     ------------------------------------------------------------------- */
  try {
    var avisoGuardado = sessionStorage.getItem("facturapp-aviso");
    if (avisoGuardado) {
      sessionStorage.removeItem("facturapp-aviso");
      mostrarAviso(avisoGuardado);
    }
  } catch (error) {
    // Si el navegador no deja usar sessionStorage, no se muestra el aviso.
  }

  /* -------------------------------------------------------------------
     14. Solicitudes creadas en el prototipo
     "Nueva solicitud" (solicitud.js) guarda cada solicitud creada en
     sessionStorage. Aquí se agregan al inicio de la tabla de solicitudes
     (la más reciente primero), con entrega "Pendiente" y estado "Abierta".
     Duran mientras la pestaña del navegador esté abierta.
     ------------------------------------------------------------------- */
  var tablaSolicitudes = document.getElementById("tabla-solicitudes");
  if (tablaSolicitudes) {
    var creadas = [];
    try {
      creadas = JSON.parse(sessionStorage.getItem("facturapp-solicitudes") || "[]");
    } catch (error) {
      creadas = [];
    }
    var cuerpoSolicitudes = tablaSolicitudes.querySelector("tbody");

    // Crea una celda con texto (textContent: no interpreta HTML) y una clase opcional.
    function celda(texto, clase) {
      var td = document.createElement("td");
      td.textContent = texto;
      if (clase) td.className = clase;
      return td;
    }
    // Crea una celda con una insignia de estado.
    function celdaInsignia(texto, tipo) {
      var td = document.createElement("td");
      var span = document.createElement("span");
      span.className = "ui-insignia ui-insignia--" + tipo;
      span.textContent = texto;
      td.appendChild(span);
      return td;
    }

    creadas.forEach(function (solicitud) {
      var fila = document.createElement("tr");
      fila.appendChild(celda(solicitud.numero, "ui-codigo"));
      fila.appendChild(celda(solicitud.fecha, "ui-codigo"));
      fila.appendChild(celda(solicitud.equipo, "ui-codigo"));
      fila.appendChild(celda(solicitud.contratista));
      fila.appendChild(celdaInsignia("Pendiente", "neutra"));
      fila.appendChild(celdaInsignia("Abierta", "neutra"));
      var acciones = celda("", "ui-tabla__acciones");
      var nota = document.createElement("span");
      nota.className = "ui-campo__ayuda";
      nota.textContent = "Creada en esta prueba";
      acciones.appendChild(nota);
      fila.appendChild(acciones);
      // insertBefore con firstChild: la más reciente queda arriba.
      cuerpoSolicitudes.insertBefore(fila, cuerpoSolicitudes.firstChild);
    });
    if (creadas.length) etiquetarTablas();
  }
})();
