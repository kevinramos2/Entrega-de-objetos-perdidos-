"""Recomprime las fotos guardadas en la base de datos (base64) para reducir
su peso y el consumo de memoria del servidor.

Uso:
    python manage.py recomprimir_fotos
"""
import base64
import io

from django.core.management.base import BaseCommand

from registro_objetos.models import ObjetoReclamado

ANCHO_MAXIMO = 900
CALIDAD = 78


def _decodificar(foto_base64):
    foto = (foto_base64 or '').strip()
    if foto.startswith('data:') and ';base64,' in foto:
        datos = foto[foto.index(',') + 1:]
    else:
        datos = foto
    return base64.b64decode(datos)


def _comprimir(contenido):
    from PIL import Image
    img = Image.open(io.BytesIO(contenido))
    img = img.convert('RGB')
    if img.width > ANCHO_MAXIMO:
        altura = round(img.height * ANCHO_MAXIMO / img.width)
        img = img.resize((ANCHO_MAXIMO, altura), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, 'JPEG', quality=CALIDAD, optimize=True)
    return buf.getvalue()


class Command(BaseCommand):
    help = 'Recomprime todas las fotos base64 a JPEG de hasta 900px.'

    def handle(self, *args, **opciones):
        queryset = ObjetoReclamado.objects.exclude(foto_base64='').only('pk', 'foto_base64')
        proceso = 0
        errores = 0
        for objeto in queryset.iterator():
            try:
                contenido = _comprimir(_decodificar(objeto.foto_base64))
                objeto.foto_base64 = 'data:image/jpeg;base64,%s' % base64.b64encode(contenido).decode('ascii')
                objeto.save(update_fields=['foto_base64'])
                proceso += 1
            except Exception as exc:  # noqa: BLE001
                errores += 1
                self.stdout.write(self.style.WARNING(
                    f'  Error con objeto #{objeto.pk}: {exc}'
                ))

        self.stdout.write(self.style.SUCCESS(
            f'{proceso} foto(s) recomprimida(s).'
        ))
        if errores:
            self.stdout.write(self.style.WARNING(f'{errores} foto(s) no pudieron procesarse.'))
