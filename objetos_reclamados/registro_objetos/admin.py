from django.contrib import admin
from django.db.models import Count
from django.utils.safestring import mark_safe
from django.core.serializers.json import DjangoJSONEncoder
import json

from .models import (
    Categoria,
    ObjetoReclamado,
    PerfilUsuario,
    SolicitudReclamacion,
)


class SolicitudInline(admin.TabularInline):
    model = SolicitudReclamacion
    extra = 0
    readonly_fields = ('usuario', 'mensaje', 'estado', 'fecha')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('icono', 'nombre', 'color', 'orden', 'cantidad_objetos')
    list_editable = ('orden',)
    search_fields = ('nombre',)

    def cantidad_objetos(self, obj):
        return obj.objetos.count()
    cantidad_objetos.short_description = 'Objetos'


@admin.register(ObjetoReclamado)
class ObjetoReclamadoAdmin(admin.ModelAdmin):
    list_display = ('nombre_objeto', 'etiqueta_categoria', 'estado', 'fecha_registro', 'responsable_entrega')
    list_filter = ('estado', 'categoria', 'suministro_correo')
    search_fields = ('nombre_objeto', 'nombre_persona', 'numero_documento', 'descripcion_objeto')
    list_select_related = ('categoria',)
    inlines = [SolicitudInline]
    readonly_fields = ('fecha_registro', 'fecha_reclamo', 'registrado_por', 'reclamado_por')
    autocomplete_fields = ('categoria',)

    change_list_template = "admin/objetos_reportes.html"

    def changelist_view(self, request, extra_context=None):
        datos_por_tipo = (
            ObjetoReclamado.objects
            .values('categoria__nombre')
            .annotate(total=Count('id'))
            .order_by('-total')
        )
        etiquetas_tipo = [item['categoria__nombre'] or 'Sin categoría' for item in datos_por_tipo]
        valores_tipo = [item['total'] for item in datos_por_tipo]

        total_entregas = ObjetoReclamado.objects.count()
        total_si = ObjetoReclamado.objects.filter(suministro_correo=True).count()

        datos_por_estado = (
            ObjetoReclamado.objects
            .values('estado')
            .annotate(total=Count('id'))
            .order_by('estado')
        )
        etiquetas_estado = [ObjetoReclamado.Estados(i['estado']).label for i in datos_por_estado]
        valores_estado = [i['total'] for i in datos_por_estado]

        datos_por_fecha = (
            ObjetoReclamado.objects
            .filter(fecha_registro__isnull=False)
            .values('fecha_registro')
            .annotate(total=Count('id'))
            .order_by('fecha_registro')
        )
        etiquetas_fecha = [str(item['fecha_registro']) for item in datos_por_fecha]
        valores_fecha = [item['total'] for item in datos_por_fecha]

        if valores_tipo:
            idx_categoria = valores_tipo.index(max(valores_tipo))
            categoria_mas_comun = etiquetas_tipo[idx_categoria]
            total_categoria_mas_comun = valores_tipo[idx_categoria]
        else:
            categoria_mas_comun, total_categoria_mas_comun = 'N/A', 0

        extra_context = extra_context or {}
        extra_context.update({
            'chart_labels': mark_safe(json.dumps(etiquetas_tipo, cls=DjangoJSONEncoder)),
            'chart_values': mark_safe(json.dumps(valores_tipo, cls=DjangoJSONEncoder)),
            'estado_labels': mark_safe(json.dumps(etiquetas_estado, cls=DjangoJSONEncoder)),
            'estado_values': mark_safe(json.dumps(valores_estado, cls=DjangoJSONEncoder)),
            'fecha_labels': mark_safe(json.dumps(etiquetas_fecha, cls=DjangoJSONEncoder)),
            'fecha_values': mark_safe(json.dumps(valores_fecha, cls=DjangoJSONEncoder)),
            'total_entregas': total_entregas,
            'categoria_mas_comun': categoria_mas_comun,
            'total_categoria_mas_comun': total_categoria_mas_comun,
            'correo_si': total_si,
            'correo_no': total_entregas - total_si,
        })
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'programa', 'telefono', 'numero_documento')
    search_fields = ('usuario__username', 'usuario__email', 'programa', 'numero_documento')
    autocomplete_fields = ('usuario',)


@admin.register(SolicitudReclamacion)
class SolicitudReclamacionAdmin(admin.ModelAdmin):
    list_display = ('objeto', 'usuario', 'estado', 'fecha', 'respondida_por', 'fecha_respuesta')
    list_filter = ('estado',)
    search_fields = ('usuario__username', 'usuario__email', 'objeto__nombre_objeto')
    readonly_fields = ('fecha', 'fecha_respuesta')