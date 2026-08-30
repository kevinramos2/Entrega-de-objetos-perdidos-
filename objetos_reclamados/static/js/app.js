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
});