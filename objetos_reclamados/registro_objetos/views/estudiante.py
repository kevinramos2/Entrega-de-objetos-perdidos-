"""Vistas del estudiante: búsqueda, detalle, solicitudes y apelaciones."""
import base64 as _base64

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .. import estadisticas as stats
from ..forms import ApelacionForm, SolicitudForm
from ..models import (
    Categoria,
    ObjetoReclamado,
    SolicitudReclamacion,
    obtener_instrucciones_entrega,
)
from .helpers import _actualizar_perfil_desde_solicitud, estados_activos_solicitud


@login_required
def lista_objetos(request):
    q = request.GET.get('q', '').strip()
    categoria_id = request.GET.get('categoria', '') or None
    sede = request.GET.get('sede', '') or None
    objetos = stats.buscar_objetos(q, categoria_id, sede=sede, solo_disponibles=True)
    return render(request, 'objetos/listado.html', {
        'objetos': objetos,
        'categorias': Categoria.objects.all(),
        'categoria_actual': categoria_id,
        'sede': sede,
        'sedes': ObjetoReclamado.Sedes.choices,
        'q': q,
        'resumen': stats.resumen_global(),
        'mensajes': stats.informacion_para_estudiantes(),
    })


@login_required
def detalle_objeto(request, pk):
    objeto = get_object_or_404(
        ObjetoReclamado.objects.select_related('categoria'),
        pk=pk,
        estado=ObjetoReclamado.Estados.DISPONIBLE,
    )
    ya_solicito = SolicitudReclamacion.objects.filter(
        usuario=request.user, objeto=objeto,
        estado__in=estados_activos_solicitud(),
    ).exists()
    inicial = {}
    perfil = getattr(request.user, 'perfil', None)
    if perfil:
        if perfil.tipo_documento:
            inicial['tipo_documento'] = perfil.tipo_documento
        if perfil.numero_documento:
            inicial['numero_documento'] = perfil.numero_documento
        if perfil.telefono:
            inicial['telefono'] = perfil.telefono
    return render(request, 'objetos/detalle.html', {
        'objeto': objeto,
        'form': SolicitudForm(initial=inicial),
        'ya_solicito': ya_solicito,
    })


def servir_foto_objeto(request, pk):
    """Sirve la foto guardada en la DB (base64) como respuesta HTTP, sin
    embebarla en el HTML para no agotar la memoria del plan gratuito."""
    objeto = get_object_or_404(ObjetoReclamado, pk=pk)
    foto = (objeto.foto_base64 or '').strip()
    if not foto:
        raise Http404('Este objeto no tiene foto.')
    if foto.startswith('data:') and ';base64,' in foto:
        mime = foto[5:foto.index(';')]
        datos = foto[foto.index(',') + 1:]
    else:
        mime = 'image/jpeg'
        datos = foto
    try:
        bytes_img = _base64.b64decode(datos)
    except Exception:
        raise Http404('Foto inválida.')
    return HttpResponse(bytes_img, content_type=mime)


@login_required
@require_POST
def solicitar_reclamacion(request, pk):
    objeto = get_object_or_404(ObjetoReclamado, pk=pk)
    if not objeto.esta_disponible:
        messages.info(request, 'Este objeto ya no está disponible.')
        return redirect('mis_solicitudes')

    ya_existe = SolicitudReclamacion.objects.filter(
        usuario=request.user, objeto=objeto,
        estado__in=estados_activos_solicitud(),
    ).exists()
    if ya_existe:
        messages.warning(request, 'Ya tienes una solicitud pendiente para este objeto.')
        return redirect('mis_solicitudes')

    form = SolicitudForm(request.POST)
    if form.is_valid():
        SolicitudReclamacion.objects.create(
            usuario=request.user,
            objeto=objeto,
            mensaje=form.cleaned_data['mensaje'].strip(),
            tipo_documento=form.cleaned_data['tipo_documento'],
            numero_documento=form.cleaned_data['numero_documento'].strip(),
            telefono=form.cleaned_data['telefono'].strip(),
        )
        _actualizar_perfil_desde_solicitud(request.user, form.cleaned_data)
        messages.success(
            request,
            '¡Listo! Tu solicitud fue enviada. La coordinación revisará que sea '
            'tu objeto y te contactará por el medio que registraste.',
        )
        return redirect('mis_solicitudes')
    messages.error(request, 'Completa los datos requeridos para enviar la solicitud.')
    return redirect('detalle_objeto', pk=objeto.pk)


@login_required
def mis_solicitudes(request):
    # Al visitar la página, las respuestas pendientes de ver se marcan como vistas.
    request.user.solicitudes.filter(
        estado__in=[
            SolicitudReclamacion.Estados.APROBADA,
            SolicitudReclamacion.Estados.RECHAZADA,
        ],
        respuesta_vista=False,
    ).update(respuesta_vista=True)
    solicitudes = (
        request.user.solicitudes
        .select_related('objeto', 'objeto__categoria')
    )
    return render(request, 'objetos/mis_solicitudes.html', {
        'solicitudes': solicitudes,
        'instrucciones': obtener_instrucciones_entrega(),
    })


@login_required
@require_POST
def apelar_solicitud(request, pk):
    solicitud = get_object_or_404(
        SolicitudReclamacion, pk=pk, usuario=request.user,
    )
    if not solicitud.puede_apelar:
        messages.warning(
            request,
            'Esta solicitud ya no admite apelación: solo puedes apelar una vez '
            'y únicamente cuando la respuesta fue un rechazo.',
        )
        return redirect('mis_solicitudes')

    form = ApelacionForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Escribe el motivo de tu apelación para continuar.')
    else:
        solicitud.apelar(request.user, form.cleaned_data['motivo'])
        messages.success(
            request,
            'Tu apelación fue enviada. La coordinación la revisará de nuevo y '
            'te responderá por este mismo medio.',
        )
    return redirect('mis_solicitudes')
