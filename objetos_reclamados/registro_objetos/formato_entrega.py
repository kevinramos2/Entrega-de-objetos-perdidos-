"""Formato de entrega de objetos encontrados: PDF (carta) listo para imprimir.

Estructura (sin tablas):
- Cabecera izquierda: Macroproceso / Proceso / Título aplicable.
- Cabecera derecha: espacio para el logo y el nombre de la UNAL.
- Título centrado: «Entrega de objetos encontrados».
- Párrafo que indica quién entrega, a quién (con tipo y número de documento)
  y qué objeto (nombre / descripción).
- Fecha de firma en Medellín (día/mes del día de entrega y año).
- Dos bloques de firma: el estudiante (con correo y teléfono) y quien entrega.

El PDF solo se emite cuando el objeto ya fue marcado como entregado, por lo que
usa la fecha de entrega registrada. El logo de la UNAL se lee desde los
estáticos (`/static/img/unal.png`); si no está presente se deja el espacio.
"""
import io
from datetime import date
from xml.sax.saxutils import escape

from PIL import Image as PillowImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Image as FlowableImage,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

VERDE = colors.HexColor('#06543c')
GRIS = colors.HexColor('#5f6b66')
LINEA = colors.HexColor('#9aa6a0')
NEGRO = colors.HexColor('#1c1c1c')

MARGEN = 22 * mm
USABLE = letter[0] - 2 * MARGEN

MES_ABREV = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
             'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']


def _est(nombre, **kw):
    base = dict(
        fontName='Helvetica', fontSize=10, leading=14,
        textColor=NEGRO, spaceAfter=0, spaceBefore=0,
    )
    base.update(kw)
    return ParagraphStyle(nombre, **base)


EST = {
    'cabecera_titulo': _est('cabecera_titulo', fontName='Helvetica-Bold', fontSize=8.6, leading=11, textColor=GRIS),
    'cabecera_valor': _est('cabecera_valor', fontName='Helvetica', fontSize=9.6, leading=13),
    'nombre_univ': _est('nombre_univ', fontName='Helvetica-Bold', fontSize=10, leading=13,
                        alignment=TA_CENTER, textColor=VERDE),
    'subtitulo_univ': _est('subtitulo_univ', fontSize=7.6, leading=10,
                           alignment=TA_CENTER, textColor=GRIS),
    'titulo': _est('titulo', fontName='Helvetica-Bold', fontSize=16, leading=20,
                   alignment=TA_CENTER, textColor=VERDE, spaceAfter=6),
    'cuerpo': _est('cuerpo', fontSize=10.6, leading=17),
    'firma_label': _est('firma_label', fontName='Helvetica-Bold', fontSize=9, textColor=GRIS),
    'firma_dato': _est('firma_dato', fontSize=9.5, leading=14),
}


def _leer_logo(static_root):
    """Devuelve un flowable con el logo UNAL si existe, o None."""
    import os
    rutas = [
        os.path.join(static_root, 'img', 'unal.png'),
        os.path.join(static_root, 'img', 'unal.jpg'),
        os.path.join(static_root, 'img', 'unal.jpeg'),
    ]
    for ruta in rutas:
        if not os.path.exists(ruta):
            continue
        try:
            with PillowImage.open(ruta) as im:
                ancho, alto = im.size
        except Exception:
            continue
        if not ancho or not alto:
            continue
        limite = 42 * mm
        if ancho >= alto:
            w = limite
            h = alto * w / ancho
        else:
            h = limite
            w = ancho * h / alto
        return FlowableImage(ruta, width=w, height=h)
    return None


def _bloque_logo(static_root):
    """Columna derecha de la cabecera: logo + nombre de la universidad."""
    logo = _leer_logo(static_root)
    piezas = []
    if logo:
        piezas.append(logo)
        piezas.append(Spacer(1, 3 * mm))
    piezas.append(Paragraph('Universidad Nacional de Colombia', EST['nombre_univ']))
    piezas.append(Spacer(1, 1 * mm))
    piezas.append(Paragraph('Sede Medellín', EST['subtitulo_univ']))
    return piezas


def _definir_fecha(fecha):
    """Descompone la fecha de entrega en día, mes (texto) y año."""
    if not fecha:
        fecha = date.today()
    elif hasattr(fecha, 'date'):
        fecha = fecha.date()
    return fecha.day, MES_ABREV[fecha.month], fecha.year


def generar_formato_entrega(solicitud):
    """Compone y devuelve el PDF del formato de entrega como bytes."""
    from django.conf import settings
    import os

    static_root = getattr(settings, 'STATIC_ROOT', '') or ''
    if static_root and not os.path.exists(static_root):
        static_root = getattr(settings, 'BASE_DIR', '') or ''

    objeto = solicitud.objeto
    usuario = solicitud.usuario
    perfil = getattr(usuario, 'perfil', None)

    nombre_reclamante = usuario.get_full_name() or usuario.username
    tipo_doc = solicitud.tipo_documento or (perfil.get_tipo_documento_display() if perfil else '')
    num_doc = solicitud.numero_documento or (perfil.numero_documento if perfil else '')
    telefono = solicitud.telefono or (perfil.telefono if perfil else '')
    correo = usuario.email or ''

    nombre_objeto = objeto.nombre_objeto or 'objeto sin nombre'
    descripcion = objeto.descripcion_objeto or ''

    nombre_encargado = (
        (solicitud.entregado_por.get_full_name() or solicitud.entregado_por.username)
        if solicitud.entregado_por else ''
    )

    dia, mes, anio = _definir_fecha(solicitud.fecha_entrega)

    flujo = []

    # ---- Cabecera: izquierda (proceso) y derecha (logo UNAL) ----
    bloque_izq = [
        Paragraph('Macroproceso: <b>Gestión Financiera y Administrativa</b>', EST['cabecera_valor']),
        Spacer(1, 1.5 * mm),
        Paragraph('Proceso: <b>Servicios Generales y Apoyo Administrativo</b>', EST['cabecera_valor']),
        Spacer(1, 1.5 * mm),
        Paragraph('Título: <b>Entrega de objetos encontrados</b>', EST['cabecera_valor']),
    ]
    bloque_der = _bloque_logo(static_root)

    cab_tabla = _dos_columna([bloque_izq, bloque_der], [0.62, 0.38])
    flujo.append(cab_tabla)
    flujo.append(Spacer(1, 3 * mm))
    flujo.append(HRFlowable(width='100%', thickness=0.8, color=LINEA))
    flujo.append(Spacer(1, 8 * mm))

    # ---- Título centrado ----
    flujo.append(Paragraph('ENTREGA DE OBJETOS ENCONTRADOS', EST['titulo']))
    flujo.append(Spacer(1, 8 * mm))

    # ---- Cuerpo ----
    desc_objeto = f' ({descripcion})' if descripcion else ''
    flujo.append(Paragraph(
        f'La <b>Unidad de Gestión Logística y Servicios Transversales</b> hace '
        f'entrega a <b>{escape(nombre_reclamante)}</b>, identificado con '
        f'<b>{escape(tipo_doc or "documento")}</b> '
        f'número <b>{escape(num_doc or "—")}</b>, del objeto '
        f'<b>{escape(nombre_objeto)}</b>{escape(desc_objeto)}.',
        EST['cuerpo'],
    ))
    flujo.append(Spacer(1, 10 * mm))

    # ---- Se firma en Medellín ----
    flujo.append(Paragraph(
        f'Se firma en Medellín el día <u>&nbsp;<b>{dia}</b>&nbsp;</u> de '
        f'<u>&nbsp;{mes}&nbsp;</u> del año <u>&nbsp;<b>{anio}</b>&nbsp;</u>.',
        EST['cuerpo'],
    ))
    flujo.append(Spacer(1, 22 * mm))

    # ---- Firmas ----
    mitad = USABLE / 2
    fila_firmas = [
        Paragraph('Firma del estudiante', EST['firma_label']),
        Spacer(1, 24 * mm),
        HRFlowable(width='88%', thickness=0.8, color=LINEA),
        Spacer(1, 2 * mm),
        Paragraph(escape(nombre_reclamante), EST['firma_dato']),
        Paragraph(f'Correo: {escape(correo or "—")}', EST['firma_dato']),
        Paragraph(f'Teléfono: {escape(telefono or "—")}', EST['firma_dato']),
    ]
    col_encargado = [
        Paragraph('Firma de quien entrega', EST['firma_label']),
        Spacer(1, 24 * mm),
        HRFlowable(width='88%', thickness=0.8, color=LINEA),
        Spacer(1, 2 * mm),
        Paragraph(escape(nombre_encargado or '—'), EST['firma_dato']),
        Paragraph('Unidad de Gestión Logística y Servicios Transversales', EST['firma_dato']),
    ]
    flujo.append(_dos_columna([fila_firmas, col_encargado], [0.5, 0.5]))

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        leftMargin=MARGEN,
        rightMargin=MARGEN,
        title='Entrega de objetos encontrados',
        author='Universidad Nacional de Colombia · Sede Medellín',
    )

    def _pie(canvas, _doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 7.8)
        canvas.setFillColor(GRIS)
        canvas.drawString(
            MARGEN, 9 * mm,
            'Unidad de Gestión Logística y Servicios Transversales',
        )
        canvas.drawRightString(
            letter[0] - MARGEN, 9 * mm,
            'Universidad Nacional de Colombia · Sede Medellín',
        )
        canvas.restoreState()

    doc.build(flujo, onFirstPage=_pie, onLaterPages=_pie)
    return buf.getvalue()


def _dos_columna(columnas, pesos):
    """Coloca dos bloques de flowables lado a lado sin cajas alrededor."""
    from reportlab.platypus import Table, TableStyle
    celdas = [[col] for col in columnas]
    tabla = Table(
        celdas,
        colWidths=[USABLE * pesos[0], USABLE * pesos[1]],
        style=TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]),
    )
    return tabla
