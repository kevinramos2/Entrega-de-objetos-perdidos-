"""Panel del administrador: CRUD de objetos y formato de entrega por objeto."""
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from ..forms import ObjetoReclamadoForm
from ..models import Categoria, ObjetoReclamado, SolicitudReclamacion


@staff_member_required
def panel_objetos(request):
    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '')
    categoria_id = request.GET.get('categoria', '') or None
    sede = request.GET.get('sede', '') or None
    qs = ObjetoReclamado.objects.select_related('categoria', 'registrado_por').all()
    if estado:
        qs = qs.filter(estado=estado)
    if sede:
        qs = qs.filter(sede=sede)
    if categoria_id:
        qs = qs.filter(categoria_id=categoria_id)
    if q:
        qs = qs.filter(
            Q(nombre_objeto__icontains=q)
            | Q(descripcion_objeto__icontains=q)
            | Q(lugar_encontrado__icontains=q)
            | Q(categoria__nombre__icontains=q)
        )
    return render(request, 'panel/objetos_lista.html', {
        'objetos': qs,
        'categorias': Categoria.objects.all(),
        'estados': ObjetoReclamado.Estados.choices,
        'sedes': ObjetoReclamado.Sedes.choices,
        'q': q, 'estado': estado, 'categoria_id': categoria_id, 'sede': sede,
    })


@staff_member_required
def panel_objeto_nuevo(request):
    form = ObjetoReclamadoForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        objeto = form.save(commit=False)
        objeto.registrado_por = request.user
        if not objeto.fecha_registro:
            objeto.fecha_registro = timezone.localdate()
        objeto.save()
        messages.success(request, f'Objeto «{objeto}» registrado correctamente.')
        return redirect('panel_objetos')
    return render(request, 'panel/objeto_form.html', {
        'form': form, 'titulo': 'Registrar nuevo objeto', 'es_nuevo': True,
    })


@staff_member_required
def panel_objeto_editar(request, pk):
    objeto = get_object_or_404(ObjetoReclamado, pk=pk)
    form = ObjetoReclamadoForm(
        request.POST or None, request.FILES or None, instance=objeto,
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Los cambios fueron guardados.')
        return redirect('panel_objetos')
    return render(request, 'panel/objeto_form.html', {
        'form': form, 'titulo': 'Editar objeto', 'es_nuevo': False, 'objeto': objeto,
    })


@staff_member_required
@require_POST
def panel_objeto_eliminar(request, pk):
    objeto = get_object_or_404(ObjetoReclamado, pk=pk)
    nombre = str(objeto)
    objeto.delete()
    messages.success(request, f'Se eliminó el registro «{nombre}».')
    return redirect('panel_objetos')


@staff_member_required
@require_POST
def panel_objetos_eliminar_seleccion(request):
    ids = request.POST.get('ids', '')
    pks = [valor for valor in ids.split(',') if valor.isdigit()]
    if not pks:
        messages.error(request, 'No seleccionaste ningún objeto para eliminar.')
        return redirect('panel_objetos')
    total, _ = ObjetoReclamado.objects.filter(pk__in=pks).delete()
    mensaje = f'Se eliminaron {total} registros.' if total != 1 else 'Se eliminó 1 registro.'
    messages.success(request, mensaje)
    return redirect('panel_objetos')


@staff_member_required
@require_POST
def panel_objeto_estado(request, pk):
    objeto = get_object_or_404(ObjetoReclamado, pk=pk)
    nuevo = request.POST.get('estado')
    valores = ObjetoReclamado.Estados.values
    if nuevo not in valores:
        messages.error(request, 'Estado no válido.')
        return redirect('panel_objetos')

    if nuevo in (ObjetoReclamado.Estados.RECLAMADO, ObjetoReclamado.Estados.ENTREGADO):
        if not objeto.nombre_persona:
            messages.error(
                request,
                'Para marcar el objeto como reclamado o entregado primero debes '
                'registrar los datos de la persona que reclama.',
            )
            return redirect('panel_objeto_editar', pk=objeto.pk)

    if nuevo == ObjetoReclamado.Estados.RECLAMADO and not objeto.fecha_reclamo:
        objeto.fecha_reclamo = timezone.now()
        if not objeto.reclamado_por:
            objeto.reclamado_por = request.user
    if nuevo == ObjetoReclamado.Estados.ENTREGADO:
        if not objeto.fecha_entrega:
            objeto.fecha_entrega = timezone.now().strftime('%Y-%m-%d')
        if not objeto.responsable_entrega:
            objeto.responsable_entrega = request.user.get_full_name() or request.user.username
        # Si hay una solicitud aprobada para este objeto, se marca como entregada
        # para que el formato quede disponible a partir de la solicitud también.
        solicitud_aprobada = SolicitudReclamacion.objects.filter(
            objeto=objeto,
            estado=SolicitudReclamacion.Estados.APROBADA,
        ).order_by('pk').first()
        if solicitud_aprobada:
            solicitud_aprobada.marcar_entregado(request.user, fecha=objeto.fecha_entrega)
    objeto.estado = nuevo
    objeto.save()
    mensaje = f'El objeto pasó a estado «{objeto.get_estado_display()}».'
    if nuevo == ObjetoReclamado.Estados.ENTREGADO:
        mensaje += ' Ya puedes descargar el formato de entrega (PDF) desde este listado.'
    messages.success(request, mensaje)
    return redirect('panel_objetos')


@staff_member_required
def panel_objeto_formato(request, pk):
    """Genera y descarga el PDF de entrega de un objeto ya entregado."""
    from ..firma_util import firma_path_de
    from ..formato_entrega import generar_formato_entrega, generar_formato_entrega_objeto

    objeto = get_object_or_404(ObjetoReclamado, pk=pk)
    if objeto.estado != ObjetoReclamado.Estados.ENTREGADO:
        messages.error(request, 'El objeto debe estar en estado «Entregado» para generar el formato.')
        return redirect('panel_objetos')

    # Prioriza la solicitud aprobada (datos del estudiante) si existe.
    solicitud_aprobada = SolicitudReclamacion.objects.filter(
        objeto=objeto,
        estado=SolicitudReclamacion.Estados.APROBADA,
        fecha_entrega__isnull=False,
    ).order_by('pk').first()
    if solicitud_aprobada:
        solicitud_aprobada.formato_descargado = True
        solicitud_aprobada.save(update_fields=['formato_descargado'])
        pdf_bytes = generar_formato_entrega(solicitud_aprobada)
    else:
        pdf_bytes = generar_formato_entrega_objeto(
            objeto,
            nombre_encargado=objeto.responsable_entrega or
            (request.user.get_full_name() or request.user.username),
            firma_path=firma_path_de(request.user),
        )

    nombre = f'formato_entrega_{objeto.pk}.pdf'
    respuesta = HttpResponse(pdf_bytes, content_type='application/pdf')
    respuesta['Content-Disposition'] = f'attachment; filename="{nombre}"'
    return respuesta
