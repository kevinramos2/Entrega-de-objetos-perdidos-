"""Envío de notificaciones por correo.

Hasta ahora la única notificación es para el estudiante cuando el
administrador responde (aprueba o rechaza) su solicitud de reclamo.
"""
import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import obtener_instrucciones_entrega

logger = logging.getLogger(__name__)


def _datos_para_entrega(solicitud):
    """Texto de entrega: específico de la solicitud o el general de config."""
    if solicitud.datos_entrega:
        return solicitud.datos_entrega
    return obtener_instrucciones_entrega().texto or ''


def notificar_respuesta_solicitud(solicitud, accion):
    """Envía al estudiante el resultado (aprobada/rechazada) de su solicitud.

    Retorna True si el correo se encoló/envió; False si no hay destinatario
    o si falló el envío (en ese caso se registra el error y se continúa,
    porque la decisión del administrador ya quedó guardada).
    """
    destinatario = (solicitud.usuario.email or '').strip()
    if not destinatario:
        logger.warning(
            'Solicitud %s: el estudiante %s no tiene correo; no se envió aviso.',
            solicitud.pk, solicitud.usuario.username,
        )
        return False

    aprobada = accion == 'aprobar'
    contexto = {
        'solicitud': solicitud,
        'objeto': solicitud.objeto,
        'aprobada': aprobada,
        'resultado': solicitud.get_estado_display(),
        'comentario_admin': solicitud.comentario_admin or '',
        'datos_entrega': _datos_para_entrega(solicitud) if aprobada else '',
        'es_apelacion': solicitud.fue_apelada,
        'site_url': settings.SITE_URL.rstrip('/'),
    }

    plantillas = 'correo/respuesta_solicitud'
    prefijo_apelacion = 'Apelación ' if contexto['es_apelacion'] else ''
    asunto = (
        f'{prefijo_apelacion}{contexto["resultado"]} · '
        f'{solicitud.objeto.nombre_objeto}'
    )

    html = render_to_string(f'{plantillas}.html', contexto)
    texto = render_to_string(f'{plantillas}.txt', contexto)

    correo = EmailMultiAlternatives(
        subject=asunto,
        body=texto or strip_tags(html),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[destinatario],
    )
    correo.attach_alternative(html, 'text/html')

    try:
        correo.send(fail_silently=True)
    except Exception:  # noqa: BLE001 - un fallo de correo no debe tumbar la decisión
        logger.exception(
            'No se pudo notificar al estudiante %s por la solicitud %s.',
            solicitud.usuario.username, solicitud.pk,
        )
        return False
    logger.info(
        'Aviso enviado a %s (solicitud %s, %s).', destinatario, solicitud.pk, accion,
    )
    return True