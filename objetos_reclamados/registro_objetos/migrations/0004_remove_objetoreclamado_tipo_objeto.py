"""Elimina el campo legado ``tipo_objeto`` ya migrado a ``categoria``."""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registro_objetos', '0003_seed_categorias_y_backfill'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='objetoreclamado',
            name='tipo_objeto',
        ),
    ]