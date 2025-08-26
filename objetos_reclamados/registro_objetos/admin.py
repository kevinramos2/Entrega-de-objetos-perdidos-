from django.contrib import admin
from django.db.models import Count
from django.utils.safestring import mark_safe
from django.core.serializers.json import DjangoJSONEncoder
import json
from .models import ObjetoReclamado

@admin.register(ObjetoReclamado)
class ObjetoReclamadoAdmin(admin.ModelAdmin):
    list_display = ('nombre_persona', 'tipo_objeto', 'fecha_entrega', 'responsable_entrega')
    list_filter = ('tipo_objeto', 'fecha_entrega', 'suministro_correo')
    search_fields = ('nombre_persona', 'numero_documento', 'tipo_objeto')

    change_list_template = "admin/objetos_reportes.html"

    def changelist_view(self, request, extra_context=None):
        # Datos agrupados por tipo_objeto
        datos_por_tipo = (
            ObjetoReclamado.objects
            .values('tipo_objeto')
            .annotate(total=Count('id'))
            .order_by('-total')
        )

        # Extraer listas para Chart.js
        etiquetas_tipo = [item['tipo_objeto'] for item in datos_por_tipo]
        valores_tipo = [item['total'] for item in datos_por_tipo]

        # Porcentaje de quienes suministraron correo
        total_entregas = ObjetoReclamado.objects.count()
        total_si = ObjetoReclamado.objects.filter(suministro_correo=True).count()
        total_no = ObjetoReclamado.objects.filter(suministro_correo=False).count()

        if total_entregas > 0:
            porcentaje_correos = round((total_si / total_entregas) * 100, 2)
        else:
            porcentaje_correos = 0



        # Número de entregas por días
        datos_por_fecha = (
            ObjetoReclamado.objects
            .values('fecha_entrega')
            .annotate(total=Count('id'))
            .order_by('fecha_entrega')
        )
        etiquetas_fecha = [str(item['fecha_entrega']) for item in datos_por_fecha]
        valores_fecha = [item['total'] for item in datos_por_fecha]

        # Encontrar el día con más entregas
        if valores_fecha:
            max_index = valores_fecha.index(max(valores_fecha))
        else:
            max_index = None

        # Variables de resumen
        total_entregas = sum(valores_fecha) if valores_fecha else 0
        dia_mas_activo = etiquetas_fecha[max_index] if max_index is not None else "N/A"
        entregas_dia_mas_activo = max(valores_fecha) if valores_fecha else 0

        if etiquetas_tipo and valores_tipo:
            idx_categoria = valores_tipo.index(max(valores_tipo))
            categoria_mas_comun = etiquetas_tipo[idx_categoria]
            total_categoria_mas_comun = valores_tipo[idx_categoria]
        else:
            categoria_mas_comun = "N/A"
            total_categoria_mas_comun = 0

        # Contexts
        extra_context = extra_context or {}
        extra_context.update({
            'datos_por_tipo': datos_por_tipo,
            'chart_labels': mark_safe(json.dumps(etiquetas_tipo, cls=DjangoJSONEncoder)),
            'chart_values': mark_safe(json.dumps(valores_tipo, cls=DjangoJSONEncoder)),
            'correo_labels': mark_safe(json.dumps(["Sí suministró correo", "No suministró correo"], cls=DjangoJSONEncoder)),
            'correo_values': mark_safe(json.dumps([total_si, total_no], cls=DjangoJSONEncoder)),
            'fecha_labels': mark_safe(json.dumps(etiquetas_fecha, cls=DjangoJSONEncoder)),
            'fecha_values': mark_safe(json.dumps(valores_fecha, cls=DjangoJSONEncoder)),
            'max_fecha_index': max_index,
            'total_entregas': total_entregas,
            'dia_mas_activo': dia_mas_activo,
            'entregas_dia_mas_activo': entregas_dia_mas_activo,
            'categoria_mas_comun': categoria_mas_comun,
            'total_categoria_mas_comun': total_categoria_mas_comun,
            'porcentaje_correos': porcentaje_correos,
        })

        return super().changelist_view(request, extra_context=extra_context)
