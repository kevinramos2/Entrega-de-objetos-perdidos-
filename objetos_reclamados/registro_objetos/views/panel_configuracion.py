"""Panel del administrador: instrucciones de entrega por sede y categorías."""
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from ..forms import CategoriaForm, InstruccionesEntregaForm
from ..models import Categoria, obtener_instrucciones_entrega


@staff_member_required
def panel_configuracion_entrega(request):
    """Instrucciones globales de dónde reclamar un objeto aprobado."""
    config = obtener_instrucciones_entrega()
    form = InstruccionesEntregaForm(request.POST or None, instance=config)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(
            request,
            'Instrucciones de entrega actualizadas: el estudiante las verá en '
            'sus solicitudes aprobadas.',
        )
        return redirect('panel_configuracion_entrega')
    return render(request, 'panel/configuracion_entrega.html', {'form': form, 'config': config})


@staff_member_required
def panel_categorias(request):
    form = CategoriaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Categoría creada.')
        return redirect('panel_categorias')
    return render(request, 'panel/categorias.html', {
        'form': form,
        'categorias': Categoria.objects.annotate(total_objetos=Count('objetos')),
    })


@staff_member_required
def panel_categoria_editar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    form = CategoriaForm(request.POST or None, instance=categoria)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Categoría actualizada.')
        return redirect('panel_categorias')
    return render(request, 'panel/categoria_form.html', {'form': form, 'categoria': categoria})


@staff_member_required
@require_POST
def panel_categoria_eliminar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if categoria.objetos.exists():
        messages.error(request, 'No puedes eliminar una categoría que tiene objetos.')
    else:
        categoria.delete()
        messages.success(request, 'Categoría eliminada.')
    return redirect('panel_categorias')
