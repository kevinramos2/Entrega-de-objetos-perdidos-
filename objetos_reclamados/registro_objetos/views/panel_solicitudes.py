"""Panel del administrador: revisión de solicitudes y formato de entrega."""
import json

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from ..correo import notificar_respuesta_solicitud
from ..formato_entrega import generar_formato_entrega
from ..models import ObjetoReclamado, SolicitudReclamacion, obtener_instrucciones_entrega


@staff_member_required
def panel_solicitudes(request):
    estado = request.GET.get('estado', '') or ''
    qs = SolicitudReclamacion.objects.select_related('usuario', 'objeto', 'objeto__categoria')
    if estado:
        qs = qs.filter(estado=estado)
    else:
        # Por revisar: pendientes y apelaciones pendientes de respuesta.
        qs = qs.filter(estado__in=[
            SolicitudReclamacion.Estados.PENDIENTE,
            SolicitudReclamacion.Estados.APELADA,
        ])
    conteo = {
        'pendiente': SolicitudReclamacion.objects.filter(estado=SolicitudReclamacion.Estados.PENDIENTE).count(),
        'apelada': SolicitudReclamacion.objects.filter(estado=SolicitudReclamacion.Estados.APELADA).count(),
        'aprobada': SolicitudReclamacion.objects.filter(estado=SolicitudReclamacion.Estados.APROBADA).count(),
        'rechazada': SolicitudReclamacion.objects.filter(estado=SolicitudReclamacion.Estados.RECHAZADA).count(),
    }
    conteo['por_revisar'] = conteo['pendiente'] + conteo['apelada']
    return render(request, 'panel/solicitudes.html', {
        'solicitudes': qs,
        'estado': estado,
        'estados': SolicitudReclamacion.Estados.choices,
        'conteos': conteo,
    })


@staff_member_required
def panel_solicitud_detalle(request, pk):
    solicitud = get_object_or_404(
        SolicitudReclamacion.objects.select_related('usuario', 'objeto', 'objeto__categoria'),
        pk=pk,
    )
    config = obtener_instrucciones_entrega()
    textos_entrega = {
        'minas': config.texto_minas or '',
        'volador': config.texto_volador or '',
    }
    return render(request, 'panel/solicitud_detalle.html', {
        'solicitud': solicitud,
        'sedes': ObjetoReclamado.Sedes.choices,
        'textos_entrega': textos_entrega,
        'textos_entrega_json': json.dumps(textos_entrega),
    })


@staff_member_required
@require_POST
def panel_solicitud_decision(request, pk, accion=None):
    solicitud = get_object_or_404(SolicitudReclamacion, pk=pk)
    accion = accion or request.POST.get('accion')
    comentario = (request.POST.get('comentario') or '').strip()
    datos_entrega = (request.POST.get('datos_entrega') or '').strip()
    sede = request.POST.get('sede') or solicitud.objeto.sede
    if sede not in ObjetoReclamado.Sedes.values:
        sede = solicitud.objeto.sede
    es_apelacion = solicitud.fue_apelada

    if solicitud.estado not in (
        SolicitudReclamacion.Estados.PENDIENTE,
        SolicitudReclamacion.Estados.APELADA,
    ):
        messages.warning(request, 'Esta solicitud ya fue respondida.')
    elif accion == 'aprobar':
        solicitud.aprobar(
            request.user,
            comentario=comentario,
            datos_entrega=datos_entrega,
            sede=sede,
        )
        notificar_respuesta_solicitud(solicitud, 'aprobar')
        prefijo = 'Apelación ' if es_apelacion else ''
        messages.success(
            request,
            f'{prefijo}Aprobada. El objeto pasó a «reclamado» y se vinculó el '
            f'perfil de {solicitud.usuario.get_full_name() or solicitud.usuario.username}.',
        )
    elif accion == 'rechazar':
        solicitud.rechazar(request.user, comentario=comentario)
        notificar_respuesta_solicitud(solicitud, 'rechazar')
        prefijo = 'Apelación ' if es_apelacion else ''
        finale = ' La apelación quedó cerrada.' if es_apelacion else ''
        messages.info(request, f'{prefijo}Rechazada. Se notificó al estudiante.{finale}')
    else:
        messages.error(request, 'Acción no válida.')
    return redirect('panel_solicitud_detalle', pk=solicitud.pk)


def _pdf_formato_entrega(solicitud):
    """Arma la respuesta HTTP con el PDF del formato de entrega."""
    pdf = generar_formato_entrega(solicitud)
    respuesta = HttpResponse(pdf, content_type='application/pdf')
    respuesta['Content-Disposition'] = (
        f'attachment; filename="formato_entrega_{solicitud.pk}.pdf"'
    )
    return respuesta


@staff_member_required
def panel_solicitud_formato(request, pk):
    """Descarga del formato de entrega (solo para el administrador y cuando el
    objeto ya fue marcado como entregado)."""
    solicitud = get_object_or_404(SolicitudReclamacion, pk=pk)
    if not solicitud.esta_entregada:
        messages.warning(
            request,
            'El formato de entrega está disponible cuando el objeto haya sido '
            'marcado como entregado.',
        )
        return redirect('panel_solicitud_detalle', pk=solicitud.pk)
    if not solicitud.formato_descargado:
        solicitud.formato_descargado = True
        solicitud.save(update_fields=['formato_descargado'])
    return _pdf_formato_entrega(solicitud)


@staff_member_required
@require_POST
def panel_solicitud_entregar(request, pk):
    """Marca la solicitud (y su objeto) como entregada y habilita el PDF."""
    solicitud = get_object_or_404(
        SolicitudReclamacion.objects.select_related('objeto'),
        pk=pk,
    )
    if solicitud.estado != SolicitudReclamacion.Estados.APROBADA:
        messages.error(request, 'Solo puedes entregar una solicitud aprobada.')
        return redirect('panel_solicitud_detalle', pk=solicitud.pk)
    if solicitud.objeto.estado == ObjetoReclamado.Estados.ENTREGADO and solicitud.fecha_entrega:
        messages.info(request, 'Este objeto ya fue marcado como entregado.')
        return redirect('panel_solicitud_detalle', pk=solicitud.pk)
    solicitud.marcar_entregado(request.user)
    messages.success(
        request,
        f'Objeto entregado el {solicitud.fecha_entrega}. Ya puedes descargar '
        f'el formato de entrega.',
    )
    return redirect('panel_solicitud_detalle', pk=solicitud.pk)
