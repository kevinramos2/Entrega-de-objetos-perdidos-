"""Panel del administrador: dashboard con indicadores y gráficas."""
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from .. import estadisticas as stats
from ..models import ObjetoReclamado
from .helpers import serializar_json


@staff_member_required
def panel_inicio(request):
    resumen = stats.resumen_global()
    por_categoria = stats.objetos_por_categoria()
    por_estado = stats.objetos_por_estado()
    por_mes = stats.objetos_por_mes()
    actividad = stats.actividad_reciente(limite=5)

    nombres_estado = dict(ObjetoReclamado.Estados.choices)

    def iniciales_categoria(nombre):
        return (nombre or '—').strip()[:2].upper() or '—'

    context = {
        'resumen': resumen,
        'actividad': actividad,
        'chart_categoria_labels': serializar_json([c['categoria__nombre'] or 'Sin categoría' for c in por_categoria]),
        'chart_categoria_iconos': serializar_json([iniciales_categoria(c['categoria__nombre']) for c in por_categoria]),
        'chart_categoria_values': serializar_json([c['total'] for c in por_categoria]),
        'chart_estado_labels': serializar_json([nombres_estado.get(e['estado'], e['estado']) for e in por_estado]),
        'chart_estado_values': serializar_json([e['total'] for e in por_estado]),
        'chart_mes_labels': serializar_json([m['mes'].strftime('%Y-%m') if m['mes'] else '' for m in por_mes]),
        'chart_mes_values': serializar_json([m['total'] for m in por_mes]),
    }
    return render(request, 'panel/inicio.html', context)
