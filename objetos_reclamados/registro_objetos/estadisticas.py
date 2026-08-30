"""Agregados y estadísticas reutilizados por las vistas.

Mantiene la lógica de reportes separada de las vistas para que el
proyecto quede bien estructurado y sea fácil de ampliar o exportar
a Power BI.
"""
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone

from .models import Categoria, ObjetoReclamado, SolicitudReclamacion


def _total_por_campo(campo):
    return list(
        ObjetoReclamado.objects
        .values(campo)
        .annotate(total=Count('id'))
        .order_by('-total')
    )


def objetos_por_categoria():
    filas = (
        ObjetoReclamado.objects
        .values('categoria__nombre', 'categoria__icono', 'categoria__color')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    return list(filas)


def objetos_por_estado():
    return _total_por_campo('estado')


def objetos_por_mes():
    """Agrupa por mes (fecha_registro) para la línea de tendencia."""
    filas = (
        ObjetoReclamado.objects
        .filter(fecha_registro__isnull=False)
        .annotate(mes=TruncMonth('fecha_registro'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )
    return list(filas)


def resumen_global():
    total = ObjetoReclamado.objects.count()
    disponibles = ObjetoReclamado.objects.filter(estado=ObjetoReclamado.Estados.DISPONIBLE).count()
    reclamados = ObjetoReclamado.objects.filter(estado=ObjetoReclamado.Estados.RECLAMADO).count()
    entregados = ObjetoReclamado.objects.filter(estado=ObjetoReclamado.Estados.ENTREGADO).count()
    recuperados = reclamados + entregados
    solicitudes_pendientes = SolicitudReclamacion.objects.filter(estado__in=[
        SolicitudReclamacion.Estados.PENDIENTE,
        SolicitudReclamacion.Estados.APELADA,
    ]).count()
    tasa = _porcentaje(recuperados, total)
    return {
        'total': total,
        'disponibles': disponibles,
        'reclamados': reclamados,
        'entregados': entregados,
        'recuperados': recuperados,
        'tasa_recuperacion': tasa,
        'solicitudes_pendientes': solicitudes_pendientes,
    }


def _porcentaje(parte, total):
    if not total:
        return 0
    return int((Decimal(parte) * 100 / Decimal(total)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def informacion_para_estudiantes():
    """Mensajes relevantes que se muestran al estudiante (recuadros/señales)."""
    hoy = timezone.now().date()
    desde = hoy - timedelta(days=30)

    total_30 = ObjetoReclamado.objects.filter(fecha_registro__gte=desde).count()
    resumen = resumen_global()

    top = objetos_por_categoria()
    top_categoria = {
        'nombre': top[0]['categoria__nombre'] or 'Sin categoría',
        'total': top[0]['total'],
    } if top else {'nombre': '—', 'total': 0}

    # Tiempo promedio de espera entre el registro y la entrega
    plazo_total = 0
    plazo_n = 0
    for obj in ObjetoReclamado.objects.filter(
            estado=ObjetoReclamado.Estados.ENTREGADO,
            fecha_registro__isnull=False,
            fecha_entrega__isnull=False,
    ):
        try:
            fecha_entrega = timezone.datetime.strptime(obj.fecha_entrega, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            continue
        if fecha_entrega >= obj.fecha_registro:
            plazo_total += (fecha_entrega - obj.fecha_registro).days
            plazo_n += 1
    promedio_dias = round(plazo_total / plazo_n, 1) if plazo_n else None

    mensajes = []
    if total_30 > 0:
        mensajes.append({
            'tipo': 'reportes',
            'titulo': f'{total_30} objetos reportados en el último mes',
            'detalle': 'Reportados por la comunidad universitaria en los últimos 30 días.',
        })
    else:
        mensajes.append({
            'tipo': 'reportes',
            'titulo': f'{resumen.get("total", 0)} objetos reportados hasta ahora',
            'detalle': 'Cada reporte ayuda a que alguien recupere lo que perdió.',
        })

    mensajes.append({
        'tipo': 'recuperados',
        'titulo': f'{resumen.get("tasa_recuperacion", 0)}% recuperados por sus dueños',
        'detalle': 'De los objetos reportados, este porcentaje ya fue reclamado y entregado.',
    })

    mensajes.append({
        'tipo': 'disponibles',
        'titulo': f'{resumen.get("disponibles", 0)} objetos esperan a su dueño',
        'detalle': 'Revisa la lista y confirma si alguno es tuyo.',
    })

    if resumen.get('solicitudes_pendientes', 0) > 0:
        mensajes.append({
            'tipo': 'solicitudes',
            'titulo': f'{resumen.get("solicitudes_pendientes", 0)} reclamos en revisión',
            'detalle': 'La coordinación está verificando estas solicitudes.',
        })

    if top_categoria['total'] > 0:
        mensajes.append({
            'tipo': 'categoria',
            'titulo': f'Los {top_categoria["nombre"].lower()} son lo más extraviado',
            'detalle': f'{top_categoria["total"]} registros en esta categoría. ¡Cuida los tuyos!',
        })

    if promedio_dias is not None:
        mensajes.append({
            'tipo': 'plazo',
            'titulo': f'Se recuperan en ~{promedio_dias} días',
            'detalle': 'Tiempo promedio entre el reporte y la entrega al dueño.',
        })

    return mensajes


def actividad_reciente(limite=6):
    return {
        'objetos': ObjetoReclamado.objects.select_related('categoria', 'registrado_por')[:limite],
        'solicitudes': SolicitudReclamacion.objects.select_related('usuario', 'objeto')[:limite],
    }


def buscar_objetos(q='', categoria_id=None, solo_disponibles=False):
    """Búsqueda con filtros; siempre usa el ORM (consultas parametrizadas)."""
    qs = ObjetoReclamado.objects.select_related('categoria').all()
    if solo_disponibles:
        qs = qs.filter(estado=ObjetoReclamado.Estados.DISPONIBLE)
    if categoria_id:
        qs = qs.filter(categoria_id=categoria_id)
    if q:
        qs = qs.filter(
            Q(nombre_objeto__icontains=q)
            | Q(descripcion_objeto__icontains=q)
            | Q(lugar_encontrado__icontains=q)
            | Q(categoria__nombre__icontains=q)
        )
    return qs