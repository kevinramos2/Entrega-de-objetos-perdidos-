from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


def dominio_permitido(email):
    if not email or '@' not in email:
        return False
    dominio = email.rsplit('@', 1)[1].strip().lower()
    return dominio in settings.ALLOWED_EMAIL_DOMAINS


class CuentaDominioAdapter(DefaultAccountAdapter):
    """Rechaza correos que no pertenezcan a los dominios institucionales."""

    def clean_email(self, email):
        email = super().clean_email(email).strip().lower()
        if not dominio_permitido(email):
            raise ValidationError(
                'Solo se permiten cuentas con correo institucional autorizado.'
            )
        return email


class CorreoInstitucionalAdapter(DefaultSocialAccountAdapter):
    """Bloquea el login social cuando el correo no es institucional."""

    def is_open_for_signup(self, request, sociallogin):
        email = ''
        if sociallogin.email_addresses:
            email = sociallogin.email_addresses[0].email or ''
        if not email:
            email = (sociallogin.account.extra_data or {}).get('email', '') or ''
        if not dominio_permitido(email):
            messages.error(
                request,
                'No pudimos verificar tu correo institucional. ' +
                'Solo se permite el ingreso con cuentas de la institución.',
            )
            return False
        return True

    def pre_social_login(self, request, sociallogin):
        email = ''
        if sociallogin.email_addresses:
            email = sociallogin.email_addresses[0].email or ''
        if email and not dominio_permitido(email):
            # Cortar el flujo antes de crear/ingresar cuentas no autorizadas
            messages.error(
                request,
                'El correo con el que intentas ingresar no pertenece a la institución.',
            )
            sociallogin.state['process'] = 'login'
            raise ValidationError('Dominio de correo no autorizado.')
        return None