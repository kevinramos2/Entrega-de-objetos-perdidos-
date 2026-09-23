"""Compresión de imágenes compartida entre el formulario del panel clásico y
la API REST, para no duplicar la lógica al migrar a React."""
import base64
import io

from PIL import Image

ANCHO_MAXIMO = 900
CALIDAD_JPEG = 78


def comprimir_a_base64(contenido_bytes):
    """Comprime una imagen a JPEG (ancho máx. 900px) y la codifica como una
    cadena data URI en base64, lista para guardar en ``foto_base64``.

    Si el contenido no es una imagen válida, se codifica tal cual para no
    perder el archivo original.
    """
    mime = 'image/jpeg'
    try:
        img = Image.open(io.BytesIO(contenido_bytes))
        img = img.convert('RGB')
        if img.width > ANCHO_MAXIMO:
            alto = round(img.height * ANCHO_MAXIMO / img.width)
            img = img.resize((ANCHO_MAXIMO, alto), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, 'JPEG', quality=CALIDAD_JPEG, optimize=True)
        datos = buf.getvalue()
    except Exception:
        datos = contenido_bytes
    return 'data:%s;base64,%s' % (mime, base64.b64encode(datos).decode('ascii'))
