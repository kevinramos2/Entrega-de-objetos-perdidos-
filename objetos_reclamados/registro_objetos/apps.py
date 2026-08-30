from django.apps import AppConfig


def _restringir_login_admin():
    """El administrador de Django solo muestra el formulario de login a
    visitantes anónimos. Un usuario ya autenticado sin permisos de staff ve la
    página 403 del sitio en lugar de un segundo formulario de credenciales."""
    from django.contrib import admin
    from django.shortcuts import render

    sitio = admin.site
    login_original = sitio.login

    def login_sin_duplicado(request, extra_context=None):
        if request.user.is_authenticated and not request.user.is_staff:
            return render(request, '403.html', status=403)
        return login_original(request, extra_context=extra_context)

    sitio.login = login_sin_duplicado


class RegistroObjetosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'registro_objetos'

    def ready(self):
        from . import signals  # noqa: F401
        _restringir_login_admin()
