"""Panel del administrador: exportación de datos a CSV."""
import csv

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.utils import timezone

from ..models import ObjetoReclamado


@staff_member_required
def panel_exportar_csv(request):
    """Exporta los datos para su análisis en Excel o Power BI."""
    respuesta = HttpResponse(content_type='text/csv; charset=utf-8')
    respuesta['Content-Disposition'] = (
        f'attachment; filename="objetos_{timezone.now().strftime("%Y%m%d")}.csv"'
    )
    respuesta.write('﻿')  # BOM para que Excel/Power BI lean UTF-8

    escritor = csv.writer(respuesta)
    escritor.writerow([
        'id', 'fecha_registro', 'nombre_objeto', 'categoria', 'sede', 'estado',
        'lugar_encontrado', 'descripcion', 'registrado_por', 'fecha_reclamo',
        'reclamado_por', 'nombre_persona', 'tipo_documento', 'numero_documento',
        'telefono', 'correo', 'suministro_correo', 'fecha_entrega',
        'responsable_entrega',
    ])
    for obj in ObjetoReclamado.objects.select_related('categoria').prefetch_related('solicitudes'):
        escritor.writerow([
            obj.id,
            obj.fecha_registro.isoformat() if obj.fecha_registro else '',
            obj.nombre_objeto,
            obj.etiqueta_categoria,
            obj.get_sede_display(),
            obj.get_estado_display(),
            obj.lugar_encontrado,
            obj.descripcion_objeto,
            obj.registrado_por.username if obj.registrado_por else '',
            obj.fecha_reclamo.strftime('%Y-%m-%d %H:%M') if obj.fecha_reclamo else '',
            obj.reclamado_por.username if obj.reclamado_por else '',
            obj.nombre_persona,
            obj.tipo_documento,
            obj.numero_documento,
            obj.telefono,
            obj.correo or '',
            'Sí' if obj.suministro_correo else 'No',
            obj.fecha_entrega,
            obj.responsable_entrega,
        ])
    return respuesta
