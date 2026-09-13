"""Utilidades compartidas entre los distintos módulos de vistas."""
import json

from django.core.cache import cache
from django.shortcuts import redirect
from django.utils.safestring import mark_safe

from ..models import PerfilUsuario, SolicitudReclamacion

MAX_INTENTOS_FALLIDOS = 5
VENTANA_BLOQUEO_SEG = 900  # 15 minutos


def redirigir_por_rol(user):
    if user.is_staff:
        return redirect('panel_inicio')
    return redirect('lista_objetos')


def _actualizar_perfil_desde_solicitud(usuario, datos):
    """Sincroniza documento y teléfono del estudiante a su perfil."""
    perfil, _ = PerfilUsuario.objects.get_or_create(usuario=usuario)
    tipo = datos.get('tipo_documento')
    numero = (datos.get('numero_documento') or '').strip()
    telefono = (datos.get('telefono') or '').strip()
    if tipo:
        perfil.tipo_documento = tipo
    if numero:
        perfil.numero_documento = numero
    if telefono:
        perfil.telefono = telefono
    perfil.save()


def _clave_login(identificador):
    return f'login_fallos:{identificador.lower()}'


def _clave_ip(direccion):
    return f'login_fallos_ip:{direccion}'


def intentos_bloqueados(*claves):
    return any(cache.get(c, 0) >= MAX_INTENTOS_FALLIDOS for c in claves)


def registrar_intento_fallido(*claves):
    for clave in claves:
        cache.set(clave, cache.get(clave, 0) + 1, VENTANA_BLOQUEO_SEG)


def limpiar_intentos(*claves):
    for clave in claves:
        cache.delete(clave)


def obtener_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def serializar_json(datos):
    return mark_safe(json.dumps(datos, ensure_ascii=False))


def estados_activos_solicitud():
    """Estados que impiden crear una nueva solicitud para el mismo objeto."""
    return [
        SolicitudReclamacion.Estados.PENDIENTE,
        SolicitudReclamacion.Estados.APELADA,
    ]
