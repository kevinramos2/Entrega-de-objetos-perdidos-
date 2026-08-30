"""Exporta las categorías y objetos reales de la base local a un fixture.

Sanitiza los datos: quita emojis de las señas y elimina la información
personal de quien reclamó (documento, teléfono, correo) y los archivos de
foto, de modo que el fixture pueda cargarse en producción con seguridad.

Uso:
    python manage.py exportar_legado
"""
import json
import re
from pathlib import Path

from django.core.management.base import BaseCommand

from registro_objetos.models import Categoria, ObjetoReclamado

EMOJI = re.compile(
    '[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U00002B00-\U00002BFF\U0001F000-\U0001F0FF]'
)

DESTINO = Path(__file__).resolve().parent.parent.parent / 'fixtures' / 'legado.json'


class Command(BaseCommand):
    help = 'Genera el fixture público con los objetos reales (sin datos personales).'

    def handle(self, *args, **opciones):
        categorias = []
        mapa_nombre = {}
        for cat in Categoria.objects.order_by('orden', 'id'):
            mapa_nombre[cat.id] = cat.nombre
            categorias.append({
                'model': 'registro_objetos.categoria',
                'pk': cat.id,
                'fields': {
                    'nombre': cat.nombre,
                    'icono': '',
                    'color': cat.color,
                    'orden': cat.orden,
                },
            })

        objetos = []
        for obj in ObjetoReclamado.objects.order_by('id'):
            descripcion = EMOJI.sub('', obj.descripcion_objeto or '').strip()
            objetos.append({
                'model': 'registro_objetos.objetoreclamado',
                'pk': obj.id,
                'fields': {
                    'nombre_objeto': obj.nombre_objeto,
                    'categoria': obj.categoria_id,
                    'descripcion_objeto': descripcion,
                    'sede': obj.sede,
                    'lugar_encontrado': obj.lugar_encontrado,
                    'fecha_registro': obj.fecha_registro.isoformat() if obj.fecha_registro else None,
                    'foto': None,
                    'estado': obj.estado,
                    # Datos personales: se vacían en el fixture público
                    'nombre_persona': '',
                    'tipo_documento': '',
                    'numero_documento': '',
                    'telefono': '',
                    'suministro_correo': False,
                    'correo': None,
                    'fecha_entrega': obj.fecha_entrega,
                    'responsable_entrega': '',
                    'fecha_reclamo': obj.fecha_reclamo.isoformat() if obj.fecha_reclamo else None,
                    # Referencias a usuarios: no se exportan (no existen en prod)
                    'registrado_por': None,
                    'reclamado_por': None,
                },
            })

        DESTINO.parent.mkdir(parents=True, exist_ok=True)
        DESTINO.write_text(
            json.dumps(categorias + objetos, ensure_ascii=False, indent=2),
            encoding='utf-8',
        )
        self.stdout.write(self.style.SUCCESS(
            f'Fixture generado: {DESTINO} '
            f'({len(categorias)} categorías, {len(objetos)} objetos).'
        ))