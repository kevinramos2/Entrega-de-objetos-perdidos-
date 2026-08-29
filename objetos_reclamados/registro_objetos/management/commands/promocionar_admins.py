"""Promueve a administrador a los usuarios cuyo correo este en DJANGO_ADMIN_EMAILS.

Uso:
    python manage.py promocionar_admins
"""
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Marca como administradores (is_staff) a los correos de DJANGO_ADMIN_EMAILS.'

    def handle(self, *args, **opciones):
        correos = getattr(settings, 'EMAILS_ADMINISTRADOR', set())
        if not correos:
            raise CommandError('DJANGO_ADMIN_EMAILS no define ningún correo.')

        promovidos = 0
        for usuario in User.objects.filter(email__isnull=False).exclude(email=''):
            correo = usuario.email.strip().lower()
            if correo in correos and not usuario.is_staff:
                usuario.is_staff = True
                usuario.is_superuser = True
                usuario.save(update_fields=['is_staff', 'is_superuser'])
                promovidos += 1
                self.stdout.write(f'  Promovido: {usuario.username} <{usuario.email}>')

        self.stdout.write(self.style.SUCCESS(
            f'{promovidos} usuario(s) marcado(s) como administrador.'
        ))
        if not promovidos:
            self.stdout.write('Ya estaban como administradores o no había cuentas con esos correos.')