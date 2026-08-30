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
});