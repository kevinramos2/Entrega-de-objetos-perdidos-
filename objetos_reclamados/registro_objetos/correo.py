"""Envío de notificaciones por correo.

Hasta ahora la única notificación es para el estudiante cuando el
administrador responde (aprueba o rechaza) su solicitud de reclamo.
"""
import logging
import threading

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

    El mensaje se compone al momento y el envío se hace en un hilo de fondo
    (solo cuando el backend es SMTP) para que un servidor de correo lento o
    caído no cuelgue ni tumbe la petición del administrador. Con Resend
    (HTTPS) o la consola el envío es inmediato y sincrónico. La decisión ya
    quedó guardada antes de llamar a esta función.

    Retorna True si el correo se encoló/envió; False si no hay destinatario.
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

    es_smtp = bool(settings.EMAIL_BACKEND) and (
        settings.EMAIL_BACKEND.endswith('smtp.EmailBackend')
    )
    if es_smtp:
        # En segundo plano: la respuesta del admin no espera al proveedor SMTP.
        threading.Thread(
            target=_enviar_correo,
            args=(correo, destinatario, solicitud, accion),
            daemon=True,
        ).start()
    else:
        # Consola / locmem / Resend (HTTPS): envío inmediato y sincrónico.
        _enviar_correo(correo, destinatario, solicitud, accion)
    return True


def _enviar_correo(correo, destinatario, solicitud, accion):
    try:
        # Sin fail_silently: cualquier rechazo del proveedor debe quedar
        # registrado en el log (en Render el motivo se ve en los logs).
        enviados = correo.send()
    except Exception:  # noqa: BLE001 - un fallo de correo no debe tumbar nada
        logger.exception(
            'No se pudo notificar al estudiante %s por la solicitud %s.',
            solicitud.usuario.username, solicitud.pk,
        )
        return False
    if not enviados:
        logger.warning(
            'El proveedor no envió el aviso a %s (solicitud %s, %s).',
            destinatario, solicitud.pk, accion,
        )
        return False
    logger.info(
        'Aviso enviado a %s (solicitud %s, %s).', destinatario, solicitud.pk, accion,
    )
    return True