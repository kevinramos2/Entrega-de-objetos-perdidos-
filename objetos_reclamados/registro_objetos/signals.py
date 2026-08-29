from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PerfilUsuario


@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Asegura que todo usuario tenga un perfil (registro local o Google)."""
    if created:
        PerfilUsuario.objects.get_or_create(usuario=instance)


@receiver(post_save, sender=User)
def promover_admin_institucional(sender, instance, **kwargs):
    """Clasifica automáticamente como administrador a los correos autorizados.

    Se aplica en cada guardado para cubrir tanto el registro local como el
    inicio de sesión con Google (allauth guarda al usuario antes del login).
    """
    correos = getattr(settings, 'EMAILS_ADMINISTRADOR', set())
    if (
        instance.email
        and instance.email.strip().lower() in correos
        and not instance.is_staff
    ):
        instance.is_staff = True
        instance.is_superuser = True
        # update() no dispara señales: al ya ser staff, se evita el bucle.
        User.objects.filter(pk=instance.pk).update(is_staff=True, is_superuser=True)