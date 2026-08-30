"""Crea datos de demostración: categorías, usuarios y objetos disponibles.

Uso:
    python manage.py seed_demo
"""
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from registro_objetos.models import Categoria, ObjetoReclamado, PerfilUsuario

CATEGORIAS = [
    ('Termos y cafeteras', 'termo', '#f59e0b', 1),
    ('Documentos', 'documento', '#3b82f6', 2),
    ('Cargadores', 'cargador', '#10b981', 3),
    ('Tecnología', 'tecnologia', '#6366f1', 4),
    ('Loncheras', 'lonchera', '#8b5cf6', 5),
    ('Comida', 'comida', '#ef4444', 6),
    ('Sombrillas', 'sombrilla', '#06b6d4', 7),
    ('Cartucheras', 'cartuchera', '#ec4899', 8),
    ('Ropa y accesorios', 'ropa', '#14b8a6', 9),
    ('Libros y cuadernos', 'libros', '#92400e', 10),
    ('Llaves', 'llaves', '#eab308', 11),
    ('Otros', 'otros', '#64748b', 99),
]

OBJETOS_DEMO = [
    ('Termo negro con detalles plateados', 'Termos y cafeteras', 'Termo de acero inoxidable, negro mate, con un sticker circular.', 'Sede Minas', 'Biblioteca Gabriel García Márquez', 6),
    ('Carpeta de documentos', 'Documentos', 'Carpeta azul con hojas y un certificado de estudios.', 'Sede Minas', 'Facultad de Ciencias', 5),
    ('Cargador USB-C blanco', 'Cargadores', 'Cargador de pared blanco USB-C de 65W con cable trenzado.', 'Sede Minas', 'Auditorio principal', 4),
    ('Lonchera térmica gris', 'Loncheras', 'Lonchera gris con bolsillo frontal, contiene un termo pequeño.', 'Sede El Volador', 'Cafetería central', 3),
    ('Gafas de lectura', 'Otros', 'Gafas con marco rojo oscuro, estuche duro.', 'Sede El Volador', 'Sala de sistemas', 10),
    ('Sombrilla negra', 'Sombrillas', 'Sombrilla plegable color negro con mango curvo de madera.', 'Sede Minas', 'Estación de buses', 8),
    ('Estuche de lápices', 'Cartucheras', 'Cartuchera azul con varios marcadores y lapiceros.', 'Sede Minas', 'Edificio de Ingeniería', 2),
    ('Llaves con llavero verde', 'Llaves', 'Tres llaves en un llavero de tela color verde con argolla.', 'Sede El Volador', 'Canchas deportivas', 1),
    ('Cuaderno de apuntes', 'Libros y cuadernos', 'Cuaderno de espiral con carátula personalizada.', 'Sede Minas', 'Bloque 1, salón 204', 9),
]

PASSWORD_ADMIN = 'CambiaEsteAdmin123!'
PASSWORD_ESTUDIANTE = 'Estudiante123!'


class Command(BaseCommand):
    help = 'Crea datos de demostración (categorías, usuarios y objetos disponibles).'

    def handle(self, *args, **opciones):
        # 1. Categorías
        categorias = {}
        for nombre, icono, color, orden in CATEGORIAS:
            cat, _ = Categoria.objects.get_or_create(
                nombre=nombre, defaults={'icono': icono, 'color': color, 'orden': orden},
            )
            categorias[nombre] = cat
        self.stdout.write(self.style.SUCCESS(f'Categorías listas ({Categoria.objects.count()}).'))

        # 2. Usuario administrador
        if User.objects.filter(username='admin').exists():
            admin = User.objects.get(username='admin')
            self.stdout.write('El usuario "admin" ya existe.')
        else:
            admin = User.objects.create_superuser(
                username='admin', email='admin@unal.edu.co', password=PASSWORD_ADMIN,
                first_name='Administración', last_name='General',
            )
            self.stdout.write(self.style.SUCCESS(
                f'Superusuario creado: usuario "admin", contrasena {PASSWORD_ADMIN} '
                '(cambiala despues de probar).'
            ))

        # 3. Usuario estudiante de ejemplo
        if User.objects.filter(username='estudiante').exists():
            self.stdout.write('El usuario "estudiante" ya existe.')
        else:
            estudiante = User.objects.create_user(
                username='estudiante', email='estudiante@unal.edu.co',
                password=PASSWORD_ESTUDIANTE,
                first_name='Andrea', last_name='Martínez Pérez',
            )
            perfil = PerfilUsuario.objects.get_or_create(usuario=estudiante)[0]
            perfil.tipo_documento = 'CC'
            perfil.numero_documento = '1020304050'
            perfil.telefono = '3001234567'
            perfil.programa = 'Ingeniería de Sistemas'
            perfil.save()
            self.stdout.write(self.style.SUCCESS(
                f'Estudiante creado: usuario "estudiante", contrasena {PASSWORD_ESTUDIANTE} '
                'y correo estudiante@unal.edu.co'
            ))

        # 4. Objetos disponibles de ejemplo
        hoy = timezone.now().date()
        creados = 0
        for nombre, categoria, descripcion, sede, lugar, dias in OBJETOS_DEMO:
            _, sido_creado = ObjetoReclamado.objects.get_or_create(
                nombre_objeto=nombre,
                defaults={
                    'categoria': categorias[categoria],
                    'descripcion_objeto': descripcion,
                    'sede': ObjetoReclamado.Sedes.MINAS if sede == 'Sede Minas' else ObjetoReclamado.Sedes.VOLADOR,
                    'lugar_encontrado': lugar,
                    'estado': ObjetoReclamado.Estados.DISPONIBLE,
                    'registrado_por': admin,
                    'fecha_registro': hoy - timedelta(days=dias),
                },
            )
            if sido_creado:
                creados += 1
        self.stdout.write(self.style.SUCCESS(f'Objetos disponibles de ejemplo: {creados}.'))

        self.stdout.write(self.style.SUCCESS('\nListo. Entra como "estudiante" para ver el portal y como "admin" para el panel.'))