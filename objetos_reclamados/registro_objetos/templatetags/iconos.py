"""Filtros y tags para íconos de categoría en las plantillas."""
import json

from django import template
from django.utils.safestring import mark_safe

from registro_objetos.iconos import ICONOS_CATEGORIA, plantilla_categoria

register = template.Library()


@register.filter
def icono_cat(categoria):
    """SVG del ícono de la categoría (heredando ``currentColor``)."""
    clave = getattr(categoria, 'icono', '')
    return mark_safe(plantilla_categoria(clave))


@register.simple_tag
def iconos_json():
    """JSON con el catálogo de íconos (clave -> contenido SVG) para el panel."""
    return mark_safe(json.dumps(ICONOS_CATEGORIA, ensure_ascii=False))