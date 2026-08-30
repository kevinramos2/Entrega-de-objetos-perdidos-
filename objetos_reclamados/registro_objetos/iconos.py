"""Íconos para las categorías.

Cada categoría guarda en su campo ``icono`` la clave de un ícono; aquí vive
el catálogo completo (trazo consistente, estilo lineal tipo Lucide) para
renderizarse como SVG inline con ``currentColor``.
"""

# Clave -> contenido interno del SVG (24x24, stroke, sin <svg> externo).
ICONOS_CATEGORIA = {
    'termo': '<path d="M17 8h1a4 4 0 1 1 0 8h-1"/><path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z"/>',
    'documento': '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/>'
                 '<path d="M14 2v4a2 2 0 0 0 2 2h4"/>'
                 '<path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/>',
    'cargador': '<path d="M12 22v-5"/><path d="M9 8V2"/><path d="M15 8V2"/>'
                '<path d="M18 8v5a4 4 0 0 1-4 4h-4a4 4 0 0 1-4-4V8Z"/>',
    'tecnologia': '<rect x="5" y="2" width="14" height="20" rx="2"/><path d="M12 18h.01"/>',
    'lonchera': '<path d="M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>'
                '<rect x="2" y="6" width="20" height="14" rx="2"/>',
    'comida': '<path d="M12 20.94c1.5 0 2.75 1.06 4 1.06 3 0 6-8 6-12.22A4.91 4.91 0 0 0 17 5c-2.22 0-4 1.44-5 2-1-.56-2.78-2-5-2a4.9 4.9 0 0 0-5 4.78C2 14 5 22 8 22c1.25 0 2.5-1.06 4-1.06Z"/>'
              '<path d="M10 2c1 .5 2 2 2 5"/>',
    'sombrilla': '<path d="M22 12a10 10 0 0 0-20 0Z"/><path d="M12 12v8a2 2 0 0 0 4 0"/>',
    'cartuchera': '<path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/>'
                  '<path d="m15 5 4 4"/>',
    'ropa': '<path d="M20.38 3.46 16 2a4 4 0 0 1-8 0L3.62 3.46a2 2 0 0 0-1.34 2.23l.58 3.47a1 1 0 0 0 .99.84H6v10c0 1.1.9 2 2 2h8a2 2 0 0 0 2-2V10h2.15a1 1 0 0 0 .99-.84l.58-3.47a2 2 0 0 0-1.34-2.23z"/>',
    'libros': '<path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>',
    'llaves': '<path d="m21 2-9.6 9.6"/><path d="m15.5 7.5 3 3L22 7l-3-3"/>'
              '<path d="m9 11 3 3"/><path d="M9.2 10.8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z"/>',
    'otros': '<path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/>'
             '<path d="M3.27 6.96 12 12.01l8.73-5.05"/><path d="M12 22.08V12"/>',
}

# Ícono genérico para categorías sin clave reconocida.
ICONO_DEFAULT = 'otros'

# Claves válidas al momento de crear/editar una categoría en el panel.
OPCIONES_ICONO = [
    ('otros', 'Genérico'),
    ('termo', 'Termo / bebida'),
    ('documento', 'Documentos'),
    ('cargador', 'Cargador'),
    ('tecnologia', 'Tecnología'),
    ('lonchera', 'Lonchera'),
    ('comida', 'Comida'),
    ('sombrilla', 'Sombrilla'),
    ('cartuchera', 'Cartuchera'),
    ('ropa', 'Ropa y accesorios'),
    ('libros', 'Libros y cuadernos'),
    ('llaves', 'Llaves'),
]


def interior_icono(clave):
    """Devuelve el contenido SVG del indicado o el genérico si no existe."""
    return ICONOS_CATEGORIA.get(clave or '', ICONOS_CATEGORIA[ICONO_DEFAULT])


def plantilla_categoria(clave, clases=''):
    """Devuelve un <svg> completo listo para ``mark_safe`` en plantillas."""
    interior = interior_icono(clave)
    attr_clases = ' class="%s"' % clases if clases else ''
    return (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        f'aria-hidden="true"{attr_clases}>{interior}</svg>'
    )