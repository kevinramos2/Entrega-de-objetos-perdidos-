"""Asigna íconos a las categorías existentes y ajusta el campo ``icono``.

El campo ``icono`` deja de ser una "seña" de iniciales y ahora guarda la
clave de un ícono del catálogo (ver ``registro_objetos/iconos.py``).
Este paso es idempotente: si una categoría ya tiene un ícono válido no lo
reemplaza, y si el nombre no coincide con las siembras, queda como estaba.
"""
from django.db import migrations, models

ICONOS_POR_NOMBRE = {
    'Termos y cafeteras': 'termo',
    'Documentos': 'documento',
    'Cargadores': 'cargador',
    'Tecnología': 'tecnologia',
    'Loncheras': 'lonchera',
    'Comida': 'comida',
    'Sombrillas': 'sombrilla',
    'Cartucheras': 'cartuchera',
    'Ropa y accesorios': 'ropa',
    'Libros y cuadernos': 'libros',
    'Llaves': 'llaves',
    'Otros': 'otros',
}


def asignar_iconos(apps, schema_editor):
    Categoria = apps.get_model('registro_objetos', 'Categoria')
    for nombre, clave in ICONOS_POR_NOMBRE.items():
        Categoria.objects.filter(nombre=nombre).update(icono=clave)


def sin_cambios(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('registro_objetos', '0009_objetoreclamado_sede'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoria',
            name='icono',
            field=models.CharField(
                blank=True, default='',
                help_text='Ícono del catálogo que identifica la categoría.',
                max_length=10,
                verbose_name='Ícono',
            ),
        ),
        migrations.RunPython(asignar_iconos, sin_cambios),
    ]