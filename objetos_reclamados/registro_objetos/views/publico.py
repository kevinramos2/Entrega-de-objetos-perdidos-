"""Vistas públicas: inicio y autenticación."""
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .. import estadisticas as stats
from ..forms import InicioSesionForm
from ..models import Categoria, ObjetoReclamado
from .helpers import (
    _clave_ip,
    _clave_login,
    intentos_bloqueados,
    limpiar_intentos,
    obtener_ip,
    redirigir_por_rol,
    registrar_intento_fallido,
)


def inicio(request):
    resumen = stats.resumen_global()
    recientes = (
        ObjetoReclamado.objects
        .select_related('categoria')
        .filter(estado=ObjetoReclamado.Estados.DISPONIBLE)[:3]
    )
    categorias = (
        Categoria.objects.annotate(
            total_disponibles=Count(
                'objetos', filter=Q(objetos__estado=ObjetoReclamado.Estados.DISPONIBLE),
            ),
        )
        .order_by('orden')
    )
    return render(request, 'objetos/home.html', {
        'resumen': resumen,
        'recientes': recientes,
        'categorias': categorias,
        'mensajes': stats.informacion_para_estudiantes()[:3],
    })


def registro_usuario(request):
    """El registro manual se deshabilitó: el acceso es con correo institucional."""
    if request.user.is_authenticated:
        return redirigir_por_rol(request.user)
    return redirect('login')


def iniciar_sesion(request):
    if request.user.is_authenticated:
        return redirigir_por_rol(request.user)

    form = InicioSesionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        identificador = form.cleaned_data['identificador'].strip()
        clave = form.cleaned_data['contrasena']
        ip = obtener_ip(request)
        claves = [_clave_login(identificador), _clave_ip(ip)]

        if intentos_bloqueados(*claves):
            messages.error(
                request,
                'Demasiados intentos fallidos. Espera unos minutos e inténtalo de nuevo.',
            )
        else:
            usuario = authenticate(request, username=identificador, password=clave)
            if usuario is None and '@' in identificador:
                # Permitir iniciar sesión también con el correo institucional
                try:
                    cuenta = User.objects.get(email__iexact=identificador)
                    usuario = authenticate(request, username=cuenta.username, password=clave)
                except User.DoesNotExist:
                    usuario = None

            if usuario is not None and usuario.is_active:
                login(request, usuario)
                limpiar_intentos(*claves)
                messages.success(
                    request,
                    f'¡Hola de nuevo, {usuario.first_name or usuario.username}!',
                )
                return redirigir_por_rol(usuario)

            registrar_intento_fallido(*claves)
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'registro/login.html', {'form': form})


@require_POST
def cerrar_sesion(request):
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('inicio')
