"""Formato de entrega de objetos: PDF (carta) listo para imprimir y firmar.

Se genera para una solicitud aprobada tomando los datos del objeto y de quien
reclama. El espacio de firma del estudiante queda en blanco; si el encargado
que aprobó tiene registrada su firma digital, esta se estampa automáticamente.
"""
import io
from datetime import date
from xml.sax.saxutils import escape

from PIL import Image as PillowImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus import Image as FlowableImage

VERDE = colors.HexColor('#0b7a54')
VERDE_OSCURO = colors.HexColor('#064d37')
GRIS = colors.HexColor('#5f6b66')
LINEA = colors.HexColor('#cfe0d6')
FONDO = colors.HexColor('#eef6f1')

MARGEN = 20 * mm
USABLE = letter[0] - 2 * MARGEN


def _est(nombre, **kw):
    base = dict(
        fontName='Helvetica', fontSize=9.5, leading=13,
        textColor=colors.black, spaceAfter=0, spaceBefore=0,
    )
    base.update(kw)
    return ParagraphStyle(nombre, **base)


EST = {
    'titulo': _est('titulo', fontName='Helvetica-Bold', fontSize=17, textColor=VERDE_OSCURO),
    'subtitulo': _est('subtitulo', fontSize=8.6, textColor=GRIS),
    'formato': _est('formato', fontName='Helvetica-Bold', fontSize=10.5, alignment=TA_RIGHT),
    'formato_fecha': _est('formato_fecha', fontSize=8.8, alignment=TA_RIGHT, textColor=GRIS),
    'banda': _est('banda', fontName='Helvetica-Bold', fontSize=8.2, textColor=colors.white),
    'etiqueta': _est('etiqueta', fontName='Helvetica-Bold', fontSize=7.8, textColor=GRIS),
    'valor': _est('valor', fontSize=9.6, leading=13),
    'cuerpo': _est('cuerpo', fontSize=10, leading=15),
    'firma_label': _est('firma_label', fontName='Helvetica-Bold', fontSize=8.2, textColor=GRIS),
    'firma_linea': _est('firma_linea', fontSize=8.8, textColor=GRIS),
}


def _banda(texto):
    return Table(
        [[Paragraph(texto, EST['banda'])]],
        colWidths=[USABLE],
        style=TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), VERDE),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]),
    )


def _rejilla(filas):
    """Rejilla de 4 columnas (Etiqueta, valor, Etiqueta, valor)."""
    col_l = 30 * mm
    col_v = (USABLE - 2 * col_l) / 2
    celdas = []
    for fila in filas:
        fila_c = []
        for i, celda in enumerate(fila):
            if i % 2 == 0:
                fila_c.append(Paragraph(celda.upper(), EST['etiqueta']))
            else:
                fila_c.append(Paragraph(escape(celda), EST['valor']))
        celdas.append(fila_c)
    return Table(
        celdas,
        colWidths=[col_l, col_v, col_l, col_v],
        style=TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, LINEA),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (0, -1), FONDO),
            ('BACKGROUND', (2, 0), (2, -1), FONDO),
            ('LEFTPADDING', (0, 0), (-1, -1), 9),
            ('RIGHTPADDING', (0, 0), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ]),
    )


def _imagen_firma(encargado):
    """Devuelve un flowable (imagen) con la firma del encargado, o None."""
    if not encargado:
        return None
    perfil = getattr(encargado, 'perfil', None)
    if not perfil or not perfil.firma:
        return None
    try:
        datos = perfil.firma.read()
    except Exception:
        return None
    if not datos:
        return None
    buf = io.BytesIO(datos)
    buf.seek(0)
    try:
        with PillowImage.open(buf) as im:
            ancho, alto = im.size
    except Exception:
        return None
    if not ancho or not alto:
        return None
    if ancho >= alto:
        w = 55 * mm
        h = alto * w / ancho
    else:
        h = 45 * mm
        w = ancho * h / alto
    buf.seek(0)
    return FlowableImage(buf, width=w, height=h)


def generar_formato_entrega(solicitud):
    """Compone y devuelve el PDF del formato de entrega como bytes."""
    objeto = solicitud.objeto
    usuario = solicitud.usuario
    perfil = getattr(usuario, 'perfil', None)
    encargado = solicitud.respondida_por

    nombre_reclamante = usuario.get_full_name() or usuario.username
    documento = ''
    if perfil and perfil.numero_documento:
        documento = f'{perfil.get_tipo_documento_display() or perfil.tipo_documento} ' \
                    f'{perfil.numero_documento}'
    telefono = perfil.telefono if perfil else ''
    correo = usuario.email or ''

    nombre_objeto = objeto.nombre_objeto or 'Objeto sin nombre'
    categoria = objeto.etiqueta_categoria or '—'
    sede = objeto.get_sede_display()
    lugar = objeto.lugar_encontrado or '—'
    entrega = solicitud.datos_entrega or '—'
    nombre_encargado = (
        encargado.get_full_name() or encargado.username
    ) if encargado else ''

    fecha = (
        solicitud.fecha_respuesta.date().strftime('%d/%m/%Y')
        if solicitud.fecha_respuesta else date.today().strftime('%d/%m/%Y')
    )
    consecutivo = f'FE-{solicitud.pk:05d}'

    flujo = []

    # Cabecera
    cabecera = Table(
        [
            [
                Paragraph('Perdidos y Encontrados', EST['titulo']),
                Paragraph(f'Formato No. {consecutivo}', EST['formato']),
            ],
            [
                Paragraph('Universidad Nacional de Colombia · Sede Medellín', EST['subtitulo']),
                Paragraph(f'Fecha: {fecha}', EST['formato_fecha']),
            ],
        ],
        colWidths=[USABLE * 0.62, USABLE * 0.38],
        style=TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]),
    )
    flujo.append(cabecera)
    flujo.append(Spacer(1, 2 * mm))
    flujo.append(HRFlowable(width='100%', thickness=1.2, color=VERDE))
    flujo.append(Spacer(1, 5 * mm))

    # Datos del objeto
    flujo.append(_banda('DATOS DEL OBJETO'))
    flujo.append(Spacer(1, 2 * mm))
    flujo.append(_rejilla([
        ['Objeto', nombre_objeto, 'Categoría', categoria],
        ['Sede', sede, 'Lugar encontrado', lugar],
    ]))
    flujo.append(Spacer(1, 6 * mm))

    # Datos de quien reclama
    flujo.append(_banda('DATOS DE QUIEN RECLAMA'))
    flujo.append(Spacer(1, 2 * mm))
    flujo.append(_rejilla([
        ['Nombre', nombre_reclamante, 'Documento', documento or '—'],
        ['Celular', telefono or '—', 'Correo', correo or '—'],
    ]))
    flujo.append(Spacer(1, 6 * mm))

    # Instrucciones de entrega
    caja_entrega = Table(
        [
            [Paragraph('CÓMO RECLAMAR EL OBJETO', EST['banda'])],
            [Paragraph(escape(entrega), EST['valor'])],
        ],
        colWidths=[USABLE],
        style=TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), VERDE),
            ('BACKGROUND', (0, 1), (0, 1), FONDO),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (0, 0), 5),
            ('BOTTOMPADDING', (0, 0), (0, 0), 5),
            ('TOPPADDING', (0, 1), (0, 1), 10),
            ('BOTTOMPADDING', (0, 1), (0, 1), 10),
        ]),
    )
    flujo.append(caja_entrega)
    flujo.append(Spacer(1, 6 * mm))

    # Declaración
    flujo.append(Paragraph(
        f'Yo, {escape(nombre_reclamante)}, identificado con {escape(documento or "—")}, '
        f'declaro que he recibido el objeto <b>{escape(nombre_objeto)}</b> descrito en este '
        'formato y asumo su cuidado y responsabilidad.',
        EST['cuerpo'],
    ))
    flujo.append(Spacer(1, 8 * mm))

    # Firmas
    flujo.append(_banda('FIRMAS'))
    flujo.append(Spacer(1, 4 * mm))
    mitad = USABLE / 2

    def _celda_firma(origen):
        if origen == 'reclamante':
            return [
                Paragraph('Firma de quien recibe', EST['firma_label']),
                Spacer(1, 26 * mm),
                HRFlowable(width='100%', thickness=0.7, color=GRIS),
                Spacer(1, 2 * mm),
                Paragraph(f'Nombre: {escape(nombre_reclamante)}', EST['firma_linea']),
                Paragraph(f'Documento: {escape(documento or "—")}', EST['firma_linea']),
            ]
        firma_img = _imagen_firma(encargado)
        return [
            Paragraph('Firma del encargado', EST['firma_label']),
            firma_img or Spacer(1, 26 * mm),
            HRFlowable(width='100%', thickness=0.7, color=GRIS),
            Spacer(1, 2 * mm),
            Paragraph(f'Nombre: {escape(nombre_encargado)}', EST['firma_linea']),
            Paragraph('Cargo: Coordinación de objetos perdidos', EST['firma_linea']),
        ]

    firmas = Table(
        [[_celda_firma('reclamante'), _celda_firma('encargado')]],
        colWidths=[mitad, mitad],
        style=TableStyle([
            ('BOX', (0, 0), (0, 0), 0.9, LINEA),
            ('BOX', (1, 0), (1, 0), 0.9, LINEA),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]),
    )
    flujo.append(firmas)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        leftMargin=MARGEN,
        rightMargin=MARGEN,
        title=f'Formato de entrega {consecutivo}',
        author='Perdidos y Encontrados · UNAL Sede Medellín',
    )

    def _pie(canvas, _doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 7.8)
        canvas.setFillColor(GRIS)
        canvas.drawCentredString(
            letter[0] / 2, 9 * mm,
            'Perdidos y Encontrados · Universidad Nacional de Colombia, Sede Medellín',
        )
        canvas.restoreState()

    doc.build(flujo, onFirstPage=_pie, onLaterPages=_pie)
    return buf.getvalue()