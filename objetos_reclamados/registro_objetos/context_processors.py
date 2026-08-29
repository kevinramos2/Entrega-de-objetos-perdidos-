from django.conf import settings


def globales(request):
    """Variables disponibles en todas las plantillas."""
    datos = {
        'GOOGLE_OAUTH_CONFIGURADO': bool(
            settings.GOOGLE_OAUTH_CLIENT_ID and settings.GOOGLE_OAUTH_CLIENT_SECRET
        ),
        'DOMINIOS_PERMITIDOS': settings.ALLOWED_EMAIL_DOMAINS,
    }
    if request.user.is_authenticated and request.user.is_staff:
        from .models import SolicitudReclamacion
        datos['solicitudes_pendientes'] = (
            SolicitudReclamacion.objects
            .filter(estado=SolicitudReclamacion.Estados.PENDIENTE)
            .count()
        )
    return datos