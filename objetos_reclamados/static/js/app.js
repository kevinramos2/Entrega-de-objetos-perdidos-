// Menú móvil
document.addEventListener('DOMContentLoaded', function () {
  var toggle = document.querySelector('.nav-toggle');
  var links = document.querySelector('.nav-links');
  if (toggle && links) {
    toggle.addEventListener('click', function () {
      links.classList.toggle('open');
    });
  }

  // Cierre manual de toasts
  document.querySelectorAll('.toast .cerrar').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var toast = btn.closest('.toast');
      if (toast) toast.remove();
    });
  });
  // Los toasts desaparecen solos a los 6 segundos
  setTimeout(function () {
    document.querySelectorAll('.toast').forEach(function (t) {
      t.style.transition = 'opacity .4s, transform .4s';
      t.style.opacity = '0';
      t.style.transform = 'translateX(40px)';
      setTimeout(function () { t.remove(); }, 450);
    });
  }, 6000);

  // Luminosidad que sigue al cursor dentro del hero (solo mouse y sin animación reducida)
  var tracker = document.querySelector('.hero-tracker');
  if (tracker && window.matchMedia('(pointer: fine)').matches &&
      !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var hero = tracker.closest('.hero');
    var centro = tracker.classList.contains('hero-tracker-anillo') ? 22 : 5;
    var destino = { x: 0, y: 0 };
    var actual = { x: 0, y: 0 };
    var iniciado = false;
    var ultimaParticula = 0;
    function animarTracker() {
      actual.x += (destino.x - actual.x) * 0.14;
      actual.y += (destino.y - actual.y) * 0.14;
      tracker.style.transform =
        'translate3d(' + (actual.x - centro) + 'px,' + (actual.y - centro) + 'px,0)';
      requestAnimationFrame(animarTracker);
    }
    function espolvorear(x, y) {
      var ahora = Date.now();
      if (ahora - ultimaParticula < 45) return;
      ultimaParticula = ahora;
      var p = document.createElement('span');
      p.className = 'hero-particula';
      p.style.left = (x - 3) + 'px';
      p.style.top = (y - 3) + 'px';
      var tam = (Math.random() * 4 + 3).toFixed(1);
      p.style.width = tam + 'px';
      p.style.height = tam + 'px';
      p.style.setProperty('--dx', (Math.random() * 60 - 30).toFixed(0) + 'px');
      p.style.setProperty('--dy', (Math.random() * -46).toFixed(0) + 'px');
      hero.appendChild(p);
      setTimeout(function () { p.remove(); }, 950);
    }
    hero.addEventListener('mousemove', function (e) {
      var r = hero.getBoundingClientRect();
      var x = e.clientX - r.left;
      var y = e.clientY - r.top;
      destino.x = x;
      destino.y = y;
      espolvorear(x, y);
      if (!iniciado) {
        iniciado = true;
        actual.x = x;
        actual.y = y;
        requestAnimationFrame(animarTracker);
      }
      tracker.classList.add('visible');
    });
    hero.addEventListener('mouseleave', function () {
      tracker.classList.remove('visible');
    });
  }

  // Vista previa del ícono de categoría en el panel
  var catalogo = window.CATEGORIA_ICONOS || null;
  function pintarIcono(select, span) {
    if (!catalogo) return;
    var interior = catalogo[select.value] || catalogo['otros'];
    span.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + interior + '</svg>';
  }
  document.querySelectorAll('select[name="icono"]').forEach(function (select) {
    var span = document.querySelector('[data-icono-preview][data-icono-de="' + select.id + '"]');
    if (!span) return;
    pintarIcono(select, span);
    select.addEventListener('change', function () { pintarIcono(select, span); });
  });

  // ------------- Modal de confirmación (reemplaza window.confirm) -------------
  var modalConfirmar = document.getElementById('modal-confirmacion');
  var modalTitulo = document.getElementById('modal-confirmacion-titulo');
  var modalMsg = document.getElementById('modal-confirmacion-msg');
  var modalIco = document.getElementById('modal-confirmacion-ico');
  var modalBoton = document.getElementById('modal-confirmacion-aceptar');
  var modalCancelar = document.getElementById('modal-confirmacion-cancelar');
  var accionPendiente = null;

  function cerrarModal() {
    modalConfirmar.setAttribute('hidden', 'hidden');
    accionPendiente = null;
    modalIco.classList.remove('ok');
    modalBoton.classList.remove('btn-danger', 'btn-success');
    modalBoton.classList.add('btn-primary');
  }

  function abrirConfirmacion(mensaje, alAceptar, opciones) {
    opciones = opciones || {};
    modalTitulo.textContent = opciones.titulo || '¿Confirmar acción?';
    modalMsg.textContent = mensaje;
    modalBoton.textContent = opciones.etiqueta || 'Confirmar';
    modalBoton.classList.remove('btn-primary', 'btn-danger', 'btn-success');
    if (opciones.tone === 'danger') {
      modalBoton.classList.add('btn-danger');
    } else if (opciones.tone === 'success') {
      modalBoton.classList.add('btn-success');
      modalIco.classList.add('ok');
    } else {
      modalBoton.classList.add('btn-primary');
    }
    accionPendiente = alAceptar;
    modalConfirmar.removeAttribute('hidden');
    modalBoton.focus();
  }

  modalCancelar.addEventListener('click', cerrarModal);
  modalConfirmar.addEventListener('click', function (e) {
    if (e.target === modalConfirmar) cerrarModal();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !modalConfirmar.hasAttribute('hidden')) cerrarModal();
  });
  modalBoton.addEventListener('click', function () {
    if (!accionPendiente) return;
    var accion = accionPendiente;
    accionPendiente = null;
    cerrarModal();
    accion();
  });

  // Formularios con data-confirm (se envían al aceptar el modal)
  document.querySelectorAll('form[data-confirm]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      cerrarMenusAcciones();
      abrirConfirmacion(form.getAttribute('data-confirm'), function () {
        form.submit();
      }, { tone: 'danger', etiqueta: 'Eliminar' });
    });
  });

  // Botones submit con data-confirm (dentro de un formulario)
  document.querySelectorAll('form button[data-confirm]').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopImmediatePropagation();
      var form = btn.closest('form');
      var tono = btn.getAttribute('data-confirm-tone') || 'danger';
      abrirConfirmacion(btn.getAttribute('data-confirm'), function () {
        if (btn.name) {
          var oculto = document.createElement('input');
          oculto.type = 'hidden';
          oculto.name = btn.name;
          oculto.value = btn.value || '';
          form.appendChild(oculto);
        }
        form.submit();
      }, {
        tone: tono,
        etiqueta: btn.getAttribute('data-confirm-label') || 'Continuar'
      });
    });
  });

  // ------------- Borrado múltiple en el panel de objetos -------------
  var checks = document.querySelectorAll('.seleccion-objeto');
  if (checks.length) {
    var todos = document.getElementById('seleccionar-todos');
    var barra = document.getElementById('barra-borrado-masivo');
    var btnBorrar = document.getElementById('btn-borrar-seleccion');
    var cancelar = document.getElementById('cancelar-seleccion');
    var conteo = document.getElementById('seleccion-conteo');
    var palabra = document.getElementById('seleccion-palabra');
    var formMasivo = document.getElementById('form-borrado-seleccion');
    var idsMasivos = formMasivo ? formMasivo.querySelector('[name="ids"]') : null;

    function actualizarSeleccion() {
      var cuantos = document.querySelectorAll('.seleccion-objeto:checked').length;
      if (conteo) conteo.textContent = String(cuantos);
      if (palabra) palabra.textContent = cuantos === 1 ? 'seleccionado' : 'seleccionados';
      if (barra) {
        if (cuantos > 0) barra.removeAttribute('hidden');
        else barra.setAttribute('hidden', 'hidden');
      }
      if (todos) todos.checked = cuantos > 0 && cuantos === checks.length;
    }

    function limpiarSeleccion() {
      checks.forEach(function (c) { c.checked = false; });
      actualizarSeleccion();
    }

    checks.forEach(function (c) {
      c.addEventListener('change', actualizarSeleccion);
    });
    if (todos) {
      todos.addEventListener('change', function () {
        checks.forEach(function (c) { c.checked = todos.checked; });
        actualizarSeleccion();
      });
    }
    if (btnBorrar) {
      btnBorrar.addEventListener('click', function (e) {
        e.preventDefault();
        if (!formMasivo || !idsMasivos) return;
        var ids = [];
        document.querySelectorAll('.seleccion-objeto:checked').forEach(function (c) { ids.push(c.value); });
        if (!ids.length) return;
        idsMasivos.value = ids.join(',');
        var palabraMsg = ids.length === 1 ? 'registro' : 'registros';
        abrirConfirmacion(
          'Vas a eliminar ' + ids.length + ' ' + palabraMsg + ' de forma permanente. Esta acción no se puede deshacer.',
          function () { formMasivo.submit(); },
          { tone: 'danger', etiqueta: 'Eliminar ' + ids.length }
        );
      });
    }
    if (cancelar) cancelar.addEventListener('click', limpiarSeleccion);
  }

  // ------------- Menú de acciones por fila -------------
  function cerrarMenusAcciones() {
    document.querySelectorAll('.menu-acciones-panel').forEach(function (panel) {
      panel.setAttribute('hidden', 'hidden');
      panel.style.position = '';
      panel.style.top = '';
      panel.style.right = '';
    });
  }

  function abrirMenuAcciones(btn) {
    cerrarMenusAcciones();
    var panel = btn.closest('.menu-acciones').querySelector('.menu-acciones-panel');
    if (!panel) return;
    panel.removeAttribute('hidden');
    var rect = btn.getBoundingClientRect();
    var alto = panel.offsetHeight;
    panel.style.position = 'fixed';
    panel.style.right = Math.max(8, window.innerWidth - rect.right) + 'px';
    var top = rect.bottom + 6;
    if (top + alto + 10 > window.innerHeight) {
      top = Math.max(8, rect.top - alto - 6);
    }
    panel.style.top = top + 'px';
  }

  document.querySelectorAll('[data-menu-boton]').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var cont = btn.closest('.menu-acciones');
      if (!cont) return;
      var panel = cont.querySelector('.menu-acciones-panel');
      if (!panel) return;
      if (panel.hasAttribute('hidden')) {
        abrirMenuAcciones(btn);
      } else {
        cerrarMenusAcciones();
      }
    });
  });
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.menu-acciones')) cerrarMenusAcciones();
  });
  window.addEventListener('resize', function () { cerrarMenusAcciones(); });
  window.addEventListener('scroll', function () { cerrarMenusAcciones(); }, true);

  // Vista previa de la instrucción de entrega por sede (solicitudes del panel)
  var guionSedes = document.getElementById('textos-entrega-sedes');
  var radiosSede = document.querySelectorAll('.select-sede input[name="sede"]');
  var textoSede = document.getElementById('texto-sede-entrega');
  if (guionSedes && radiosSede.length && textoSede) {
    var textosSede = JSON.parse(guionSedes.textContent || '{}');
    function actualizarOpcionSede() {
      document.querySelectorAll('.radio-sede').forEach(function (r) {
        r.classList.toggle('seleccionada', r.querySelector('input').checked);
      });
    }
    function pintarInstruccionSede() {
      var marcada = document.querySelector('.select-sede input[name="sede"]:checked');
      var clave = marcada ? marcada.value : '';
      var texto = textosSede[clave] || '';
      textoSede.textContent = texto || 'No hay instrucción configurada para esta sede.';
    }
    radiosSede.forEach(function (r) {
      r.addEventListener('change', function () {
        actualizarOpcionSede();
        pintarInstruccionSede();
      });
    });
    actualizarOpcionSede();
    pintarInstruccionSede();
  }

  // Subida de foto con vista previa (formulario de objeto)
  var inputFoto = document.querySelector('.archivo-subida-input');
  if (inputFoto) {
    var area = inputFoto.closest('.archivo-subida-area');
    var preview = area.querySelector('.archivo-subida-preview');
    var vacio = area.querySelector('.archivo-subida-vacio');
    // El clic en el área abre el selector
    if (area) {
      area.addEventListener('click', function () { inputFoto.click(); });
    }
    inputFoto.addEventListener('change', function () {
      if (inputFoto.files && inputFoto.files[0]) {
        var lector = new FileReader();
        lector.onload = function (ev) {
          preview.src = ev.target.result;
          preview.hidden = false;
          if (vacio) vacio.hidden = true;
        };
        lector.readAsDataURL(inputFoto.files[0]);
      }
    });
    // Arrastrar y soltar
    ['dragenter', 'dragover'].forEach(function (evt) {
      area.addEventListener(evt, function (e) {
        e.preventDefault();
        area.classList.add('dragging');
      });
    });
    ['dragleave', 'drop'].forEach(function (evt) {
      area.addEventListener(evt, function (e) {
        e.preventDefault();
        area.classList.remove('dragging');
      });
    });
    area.addEventListener('drop', function (e) {
      var archivos = e.dataTransfer && e.dataTransfer.files;
      if (archivos && archivos.length) {
        inputFoto.files = archivos;
        inputFoto.dispatchEvent(new Event('change'));
      }
    });
  }

  // Picker de fecha propio (reemplaza el widget nativo de type=date)
  var MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio',
               'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
  var DIAS_SEMANA = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sá', 'Do'];

  function formatearFecha(iso) {
    // 'YYYY-MM-DD' -> 'dd/mm/aaaa'
    if (!iso || typeof iso !== 'string') return '';
    var partes = iso.split('-');
    if (partes.length !== 3) return '';
    return partes[2] + '/' + partes[1] + '/' + partes[0];
  }

  function crearDatePicker(campo) {
    var input = campo.querySelector('.campo-fecha > input');
    if (!input) return;
    var texto = campo.querySelector('[data-fecha-texto]');
    var pop = document.createElement('div');
    pop.className = 'datepicker-pop';
    pop.hidden = true;
    campo.appendChild(pop);

    // El calendario propio guía la selección; se evita teclear a ciegas.
    input.readOnly = true;

    // Fecha visible para el calendario
    var actual = (function () {
      var val = input.value;
      if (val) {
        var p = val.split('-').map(Number);
        if (p.length === 3 && !isNaN(p[0]) && !isNaN(p[1]) && !isNaN(p[2])) {
          return new Date(p[0], p[1] - 1, p[2]);
        }
      }
      return new Date();
    })();

    // Texto inicial
    if (texto) texto.textContent = formatearFecha(input.value);

    function pintarTexto() {
      if (texto) texto.textContent = formatearFecha(input.value);
    }

    function renderCalendario() {
      var anio = actual.getFullYear();
      var mes = actual.getMonth();
      var hoy = new Date();
      hoy.setHours(0, 0, 0, 0);
      var seleccionado = input.value;

      var cabecera = document.createElement('div');
      cabecera.className = 'datepicker-cabecera';

      function botonNav(direccion) {
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'datepicker-nav';
        b.innerHTML = direccion > 0
          ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>'
          : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>';
        b.addEventListener('click', function () {
          actual.setMonth(actual.getMonth() + direccion);
          renderCalendario();
        });
        return b;
      }

      var titulo = document.createElement('span');
      titulo.className = 'datepicker-titulo';
      titulo.textContent = MESES[mes] + ' ' + anio;

      cabecera.appendChild(botonNav(-1));
      cabecera.appendChild(titulo);
      cabecera.appendChild(botonNav(1));

      var semana = document.createElement('div');
      semana.className = 'datepicker-dias-semana';
      DIAS_SEMANA.forEach(function (d) {
        var s = document.createElement('span');
        s.textContent = d;
        semana.appendChild(s);
      });

      // Rejilla de días
      var primeroSemana = new Date(anio, mes, 1).getDay(); // 0=domingo
      var offset = (primeroSemana + 6) % 7; // convertir a lunes=0
      var diasEnMes = new Date(anio, mes + 1, 0).getDate();
      var rejilla = document.createElement('div');
      rejilla.className = 'datepicker-rejilla';

      for (var i = 0; i < offset; i++) {
        var celdaVacia = document.createElement('span');
        rejilla.appendChild(celdaVacia);
      }

      for (var d = 1; d <= diasEnMes; d++) {
        (function (dia) {
          var boton = document.createElement('button');
          boton.type = 'button';
          boton.className = 'datepicker-dia';
          boton.textContent = dia;

          var fechaActual = new Date(anio, mes, dia);

          if (fechaActual.getTime() === hoy.getTime()) boton.classList.add('hoy');

          var iso = anio + '-' + String(mes + 1).padStart(2, '0') + '-' + String(dia).padStart(2, '0');
          if (iso === seleccionado) {
            boton.classList.add('seleccionado');
            // No marcar "hoy" también si hoy está seleccionado (favorece seleccionado)
            boton.classList.remove('hoy');
          }

          boton.addEventListener('click', function () {
            input.value = iso;
            pintarTexto();
            pop.hidden = true;
          });
          rejilla.appendChild(boton);
        })(d);
      }

      // Pie: Hoy / Limpiar
      var pie = document.createElement('div');
      pie.className = 'datepicker-pie';

      var hoyBtn = document.createElement('button');
      hoyBtn.type = 'button';
      hoyBtn.className = 'datepicker-hoy-btn';
      hoyBtn.textContent = 'Hoy';
      hoyBtn.addEventListener('click', function () {
        var h = new Date();
        input.value = h.getFullYear() + '-' + String(h.getMonth() + 1).padStart(2, '0') + '-' + String(h.getDate()).padStart(2, '0');
        actual = new Date();
        pintarTexto();
        pop.hidden = true;
      });

      var limpiarBtn = document.createElement('button');
      limpiarBtn.type = 'button';
      limpiarBtn.className = 'datepicker-limpiar-btn';
      limpiarBtn.textContent = 'Limpiar';
      limpiarBtn.addEventListener('click', function () {
        input.value = '';
        pintarTexto();
        pop.hidden = true;
      });

      pie.appendChild(hoyBtn);
      pie.appendChild(limpiarBtn);

      pop.textContent = '';
      pop.appendChild(cabecera);
      pop.appendChild(semana);
      pop.appendChild(rejilla);
      pop.appendChild(pie);
    }

    // Clic en cualquier parte del campo abre el calendario
    campo.addEventListener('click', function (e) {
      if (e.target.closest('.datepicker-pop')) return;
      if (pop.hidden) {
        actual = (function () {
          var val = input.value;
          if (val) {
            var p = val.split('-').map(Number);
            if (p.length === 3 && !isNaN(p[0]) && !isNaN(p[1]) && !isNaN(p[2])) {
              return new Date(p[0], p[1] - 1, p[2]);
            }
          }
          return new Date();
        })();
        renderCalendario();
        pop.hidden = false;
      } else {
        pop.hidden = true;
      }
    });

    // Cerrar al hacer clic fuera
    document.addEventListener('click', function (e) {
      if (!campo.contains(e.target)) pop.hidden = true;
    });
  }

  document.querySelectorAll('.campo-fecha').forEach(crearDatePicker);
});