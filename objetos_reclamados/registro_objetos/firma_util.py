"""Utilidades para la firma digital de los administradores.

Normalizan la imagen que sube el usuario (formato, tamaño y transparencia)
para que el servidor no tenga que procesar archivos enormes y para que la
estampa quede bien en el PDF de entrega. Siempre se guarda como PNG RGBA
(preserva la transparencia del fondo), con el lado más largo limitado.
"""
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image

# Límite de píxeles por lado para una firma razonable. Una firma de 1000 px
# rinde de sobra para imprimir en el formato y pesa pocos KB.
MAX_LADO = 1000

# Protección ante imágenes de tamaño desmedido (bombas de compresión). Pillow
# lanza DecompressionBombError cuando una imagen supera este límite de píxeles.
Image.MAX_IMAGE_PIXELS = 40_000_000


class ErrorFirma(ValueError):
    pass


def _blanco_a_transparente(im):
    """Vuelve transparentes los píxeles casi blancos (fondo escaneado)."""
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    pixeles = im.load()
    ancho, alto = im.size
    for y in range(alto):
        for x in range(ancho):
            r, g, b, a = pixeles[x, y]
            if a > 0 and r >= 240 and g >= 240 and b >= 240:
                pixeles[x, y] = (r, g, b, 0)
    return im


def normalizar_firma(archivo, max_lado=MAX_LADO):
    """Convierte la imagen subida en un PNG RGBA listo para guardar.

    Devuelve un ``ContentFile`` con el PNG normalizado. Lanza
    ``ErrorFirma`` si el archivo no es una imagen válida o está vacía.
    """
    try:
        imagen = Image.open(archivo)
        imagen.load()
    except Exception as exc:
        raise ErrorFirma('El archivo no es una imagen válida.') from exc

    modo_original = imagen.mode
    tiene_alpha = 'A' in imagen.mode

    if imagen.mode in ('P', 'RGB', 'L'):
        imagen = imagen.convert('RGBA')
    elif imagen.mode in ('RGBA', 'LA'):
        imagen = imagen.convert('RGBA')
    else:
        raise ErrorFirma(
            'Formato de imagen no compatible. Usa PNG, JPG o WEBP.',
        )

    ancho, alto = imagen.size
    lado_mayor = max(ancho, alto)
    if lado_mayor > max_lado:
        escala = max_lado / lado_mayor
        imagen = imagen.resize(
            (max(1, round(ancho * escala)), max(1, round(alto * escala))),
            Image.LANCZOS,
        )

    # Las fotos/fondos sin canal alfa suelen tener fondo blanco: lo quitamos
    # para que la firma se estampe sin cuadro blanco.
    if not tiene_alpha:
        imagen = _blanco_a_transparente(imagen)

    if not imagen.getbbox():
        raise ErrorFirma('La imagen está vacía o es transparente por completo.')

    buf = BytesIO()
    imagen.save(buf, format='PNG', optimize=True)
    return ContentFile(buf.getvalue(), name='firma.png')


def firma_path_de(usuario):
    """Ruta en disco de la firma de un usuario, o '' si no tiene."""
    if not usuario:
        return ''
    perfil = getattr(usuario, 'perfil', None)
    if perfil and perfil.firma:
        try:
            return perfil.firma.path
        except Exception:
            return ''
    return ''


def firma_png_bytes(ruta, max_lado=MAX_LADO):
    """Lee una firma guardada y la devuelve como PNG RGBA en bytes.

    Si algo falla (archivo borrado, formato raro) devuelve ``None`` para que
    el PDF se genere igualmente sin la estampa. Nunca levanta excepciones.
    """
    import os
    if not ruta or not os.path.exists(ruta):
        return None
    try:
        imagen = Image.open(ruta)
        imagen.load()
        imagen = imagen.convert('RGBA')
        ancho, alto = imagen.size
        if max(ancho, alto) > max_lado:
            escala = max_lado / max(ancho, alto)
            imagen = imagen.resize(
                (max(1, round(ancho * escala)), max(1, round(alto * escala))),
                Image.LANCZOS,
            )
        buf = BytesIO()
        imagen.save(buf, format='PNG', optimize=True)
        return buf.getvalue()
    except Exception:
        return None