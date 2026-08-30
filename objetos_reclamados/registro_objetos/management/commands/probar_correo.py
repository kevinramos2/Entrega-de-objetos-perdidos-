"""Envía un correo de prueba para verificar la configuración del backend.

Uso:
    python manage.py probar_correo <correo@destino>

Sirve para validar la API key de Resend (o el SMTP) directamente desde
Render sin tener que aprobar/rechazar una solicitud real.
"""
import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Envía un correo de prueba a la dirección indicada.'

    def add_arguments(self, parser):
        parser.add_argument('destinatario', help='Correo de destino para la prueba.')

    def handle(self, *args, **opciones):
        destinatario = (opciones['destinatario'] or '').strip()
        if '@' not in destinatario:
            raise CommandError('Indica un correo válido, p. ej. python manage.py probar_correo alguien@gmail.com')

        self.stdout.write(f'Backend activo: {settings.EMAIL_BACKEND}')
        self.stdout.write(
            f'Remitente: {settings.DEFAULT_FROM_EMAIL} | '
            f'Resend configurado: {bool(getattr(settings, "ANYMAIL", {}).get("RESEND_API_KEY"))}'
        )

        correo = EmailMultiAlternatives(
            subject='Prueba de correo · Objetos perdidos y encontrados UNAL',
            body='Este es un correo de prueba. Si lo ves, el envío funciona correctamente.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[destinatario],
        )
        correo.attach_alternative(
            '<p>Este es un <b>correo de prueba</b>. Si lo ves, el envío funciona correctamente.</p>',
            'text/html',
        )
        try:
            enviados = correo.send()
        except Exception:  # noqa: BLE001 - solo reporta el fallo
            logger.exception('Fallo al enviar el correo de prueba a %s.', destinatario)
            raise CommandError('El proveedor rechazó el correo; mira el detalle en el log.')

        if enviados:
            self.stdout.write(self.style.SUCCESS(
                f'Correo de prueba enviado a {destinatario}.'
            ))
        else:
            self.stdout.write(self.style.ERROR('El proveedor no aceptó el correo; revisa la API key.'))