from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PerfilUsuario


@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Asegura que todo usuario tenga un perfil (registro local o Google)."""
    if created:
        PerfilUsuario.objects.get_or_create(usuario=instance)