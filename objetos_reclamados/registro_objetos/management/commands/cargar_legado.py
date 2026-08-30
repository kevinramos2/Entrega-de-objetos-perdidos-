"""Carga los objetos reales desde el fixture en bases de datos vacías.

Pensado para el primer despliegue (p. ej. en Render): si la base de datos
recién migrada no tiene objetos, se importan las categorías y los objetos
históricos reales del fixture ``legado.json``. Es idempotente: si ya hay
objetos no hace nada (se puede forzar con ``--force``).

Uso:
    python manage.py cargar_legado
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand

from registro_objetos.models import Categoria, ObjetoReclamado

FIXTURE = Path(__file__).resolve().parent.parent.parent / 'fixtures' / 'legado.json'


class Command(BaseCommand):
    help = 'Importa categorías y objetos históricos reales a la base de datos.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force', action='store_true',
            help='Importa aunque ya existan objetos (no borra los actuales).',
        )

    def handle(self, *args, **opciones):
        if not FIXTURE.exists():
            self.stdout.write(self.style.ERROR('No existe el fixture. Ejecuta primero: exportar_legado.'))
            return

        if ObjetoReclamado.objects.count() > 0 and not opciones['force']:
            self.stdout.write(
                self.style.WARNING(f'Ya hay {ObjetoReclamado.objects.count()} objetos; no se importó nada.')
            )
            return

        datos = json.loads(FIXTURE.read_text(encoding='utf-8'))

        categorias = {}
        for item in datos:
            if item['model'] != 'registro_objetos.categoria':
                continue
            cat, _ = Categoria.objects.get_or_create(
                nombre=item['fields']['nombre'],
                defaults={'icono': '', 'color': item['fields']['color'], 'orden': item['fields']['orden']},
            )
            categorias[item['pk']] = cat

        creados = 0
        for item in datos:
            if item['model'] != 'registro_objetos.objetoreclamado':
                continue
            campos = item['fields']
            categoria = categorias.get(campos.get('categoria'))
            ObjetoReclamado.objects.get_or_create(
                pk=item['pk'],
                defaults={
                    'nombre_objeto': campos.get('nombre_objeto') or '',
                    'categoria': categoria,
                    'descripcion_objeto': campos.get('descripcion_objeto') or '',
                    'sede': campos.get('sede') or ObjetoReclamado.Sedes.MINAS,
                    'lugar_encontrado': campos.get('lugar_encontrado') or '',
                    'fecha_registro': campos.get('fecha_registro'),
                    'estado': campos.get('estado') or ObjetoReclamado.Estados.DISPONIBLE,
                    'fecha_reclamo': campos.get('fecha_reclamo'),
                    'fecha_entrega': campos.get('fecha_entrega') or '',
                },
            )
            creados += 1

        self.stdout.write(self.style.SUCCESS(
            f'Carga completada: {len(categorias)} categorías y {creados} objetos reales.'
        ))