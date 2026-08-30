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

  // Confirmación para formularios con data-confirm
  document.querySelectorAll('form[data-confirm]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      var msg = form.getAttribute('data-confirm') || '¿Estás seguro?';
      if (!window.confirm(msg)) e.preventDefault();
    });
  });

  // Confirmación para botones con data-confirm (dentro de un formulario)
  document.querySelectorAll('form button[data-confirm]').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      var msg = btn.getAttribute('data-confirm') || '¿Estás seguro?';
      if (!window.confirm(msg)) {
        e.preventDefault();
        e.stopImmediatePropagation();
      }
    });
  });

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
});