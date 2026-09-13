"""Páginas de error."""
from django.conf import settings
from django.http import HttpResponse
from django.utils.html import escape


def error_500(request, exception=None):
    """Pagina de error 500. Con DJANGO_SHOW_ERRORS=1 muestra el traceback
    completo en el navegador para facilitar el diagnostico de fallos que
    Render no reporta en sus logs."""
    if not getattr(settings, 'SHOW_TRACEBACKS', False):
        from django.views.defaults import server_error
        return server_error(request)

    import traceback

    detalles = list(traceback.format_exception(exception)) if exception else ['<sin excepción>']
    cuerpo = '\n'.join([f'{request.method} {request.path}', ''] + detalles)
    html = (
        '<div style="background:#2b2b2b;color:#e6e6e6;font-family:monospace;'
        'padding:20px;white-space:pre-wrap;font-size:13px">'
        + escape(cuerpo)
        + '</div>'
    )
    return HttpResponse(html, status=500)
