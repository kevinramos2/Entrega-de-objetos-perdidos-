"""Seed de Categorías y backfill de los registros históricos.

El modelo original solo tenía ``tipo_objeto`` (texto libre). Esta migración:
  1. Crea categorías (Tecnología, Documentos, etc.).
  2. Asigna a cada objeto histórico su categoría según su ``tipo_objeto``.
  3. Los objetos históricos quedan como ``entregado`` (ya fueron devueltos).
  4. Copia el nombre de la categoría como ``nombre_objeto`` aproximado.
"""
from django.db import migrations
from django.db.models import Count


CATEGORIAS = [
    {'nombre': 'Termos y cafeteras', 'icono': '', 'color': '#f59e0b', 'orden': 1},
    {'nombre': 'Documentos', 'icono': '', 'color': '#3b82f6', 'orden': 2},
    {'nombre': 'Cargadores', 'icono': '', 'color': '#10b981', 'orden': 3},
    {'nombre': 'Tecnología', 'icono': '', 'color': '#6366f1', 'orden': 4},
    {'nombre': 'Loncheras', 'icono': '', 'color': '#8b5cf6', 'orden': 5},
    {'nombre': 'Comida', 'icono': '', 'color': '#ef4444', 'orden': 6},
    {'nombre': 'Sombrillas', 'icono': '', 'color': '#06b6d4', 'orden': 7},
    {'nombre': 'Cartucheras', 'icono': '', 'color': '#ec4899', 'orden': 8},
    {'nombre': 'Ropa y accesorios', 'icono': '', 'color': '#14b8a6', 'orden': 9},
    {'nombre': 'Libros y cuadernos', 'icono': '', 'color': '#92400e', 'orden': 10},
    {'nombre': 'Llaves', 'icono': '', 'color': '#eab308', 'orden': 11},
    {'nombre': 'Otros', 'icono': '', 'color': '#64748b', 'orden': 99},
]

# Mapeo de los tipos históricos a categorías
MAPA = {
    'Termo': 'Termos y cafeteras',
    'Documentos': 'Documentos',
    'Cargador': 'Cargadores',
    'Lonchera': 'Loncheras',
    'Comida': 'Comida',
    'Sombrilla': 'Sombrillas',
    'Cartuchera': 'Cartucheras',
}


def seed_y_backfill(apps, schema_editor):
    Categoria = apps.get_model('registro_objetos', 'Categoria')
    Objeto = apps.get_model('registro_objetos', 'ObjetoReclamado')

    creadas = {}
    for datos in CATEGORIAS:
        categoria, _ = Categoria.objects.get_or_create(nombre=datos['nombre'], defaults=datos)
        creadas[categoria.nombre] = categoria

    for objeto in Objeto.objects.all():
        nombre_categoria = MAPA.get(objeto.tipo_objeto, 'Otros')
        categoria = creadas.get(nombre_categoria) or Categoria.objects.filter(nombre='Otros').first()
        objeto.categoria = categoria
        objeto.estado = 'entregado'
        if not objeto.nombre_objeto:
            objeto.nombre_objeto = objeto.tipo_objeto or ''
        objeto.save()


def retroceder(apps, schema_editor):
    # No deshacemos: eliminar categorías borraría información valiosa.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('registro_objetos', '0002_categoria_alter_objetoreclamado_options_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_y_backfill, retroceder),
    ]