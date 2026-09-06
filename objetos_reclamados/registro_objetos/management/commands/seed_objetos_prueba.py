"""Crea ~30 objetos de prueba con sedes, categorías, estados y fechas variados.

Uso:
    python manage.py seed_objetos_prueba        # crea (idempotente por nombre)
    python manage.py seed_objetos_prueba --limpiar   # borra los creados antes de recrearlos
"""
from datetime import datetime, timedelta, time

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from registro_objetos.models import Categoria, ObjetoReclamado

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

# (nombre, categoría, descripción, sede, lugar, días atrás, estado, datos_persona|None)
# sedes: 'minas' / 'volador' · estados: disponible / reclamado / entregado
OBJETOS = [
    # ---- Disponibles · Sede Minas ----
    ('Audífonos inalámbricos negros', 'Tecnología', 'Audífonos Bluetooth color negro mate con estuche de carga.', 'minas', 'Biblioteca Gabriel García Márquez', 2, 'disponible', None),
    ('Termo plateado 750 ml', 'Termos y cafeteras', 'Termo de acero inoxidable plateado con tapa de rosca.', 'minas', 'Facultad de Ciencias', 1, 'disponible', None),
    ('Calculadora científica Casio', 'Tecnología', 'Calculadora científica con funda de tela y dos pilas.', 'minas', 'Auditorio principal', 3, 'disponible', None),
    ('Carpeta manila con fotocopias', 'Documentos', 'Carpeta manila con fotocopias y un resumen manuscrito.', 'minas', 'Bloque 1, salón 204', 4, 'disponible', None),
    ('Morral universitario azul', 'Ropa y accesorios', 'Morral azul con compartimiento para portátil, algo pesado.', 'minas', 'Estación de buses', 5, 'disponible', None),
    ('Gafas de sol con marco carey', 'Ropa y accesorios', 'Gafas de sol con marco carey y estuche rígido.', 'minas', 'Parqueadero de motos', 6, 'disponible', None),
    ('Cargador de laptop HP 65W', 'Cargadores', 'Cargador original de 65W con cable de tres clavijas.', 'minas', 'Salón de cómputo 3', 7, 'disponible', None),
    ('Sombrilla roja plegable', 'Sombrillas', 'Sombrilla color rojo con apertura automática.', 'minas', 'Puerta principal', 8, 'disponible', None),
    ('Lonchera azul con logo', 'Loncheras', 'Lonchera azul de tela con un termo pequeño adentro.', 'minas', 'Cafetería de Ingeniería', 9, 'disponible', None),
    ('Libro de Cálculo Multivariable', 'Libros y cuadernos', 'Libro de texto de Cálculo Multivariable, séptima edición.', 'minas', 'Biblioteca Gabriel García Márquez', 10, 'disponible', None),
    ('Cartuchera negra estampada', 'Cartucheras', 'Cartuchera negra con lapiceros y resaltadores adentro.', 'minas', 'Bachillerato, salón 101', 11, 'disponible', None),
    ('Llavero con tarjeta de ingreso', 'Llaves', 'Llavero con tarjeta de acceso y una llave mediana.', 'minas', 'Torre de laboratorios', 12, 'disponible', None),

    # ---- Disponibles · Sede El Volador ----
    ('Casco de bicicleta blanco', 'Ropa y accesorios', 'Casco blanco con tiras rojas reflectivas, talla M.', 'volador', 'Ciclo-parqueadero', 2, 'disponible', None),
    ('Carpeta verde con constancias', 'Documentos', 'Carpeta verde con constancias de estudio y un folleto.', 'volador', 'Secretaría académica', 3, 'disponible', None),
    ('Cargador tipo C doble puerto', 'Cargadores', 'Cargador con dos puertos USB-C de 30W.', 'volador', 'Sala de sistemas', 4, 'disponible', None),
    ('Sombrilla negra automática', 'Sombrillas', 'Sombrilla negra de tela gruesa con mango de goma.', 'volador', 'Cafetería central', 5, 'disponible', None),
    ('Termo pequeño rojo 350 ml', 'Termos y cafeteras', 'Termo compacto color rojo de 350 ml.', 'volador', 'Salón de tutorías', 6, 'disponible', None),
    ('Estuche con audífonos rosados', 'Cartucheras', 'Cartuchera rosada con audífonos de diadema y organizador.', 'volador', 'Aulas 201-210', 7, 'disponible', None),
    ('Guante de béisbol derecho', 'Otros', 'Guante de béisbol para mano derecha con una pelota.', 'volador', 'Canchas deportivas', 8, 'disponible', None),
    ('Lonchera gris con bolsillo', 'Loncheras', 'Lonchera gris con compartimiento para botella.', 'volador', 'Cafetería central', 11, 'disponible', None),

    # ---- Reclamados ----
    ('Billetera marrón de cuero', 'Ropa y accesorios', 'Billetera marrón con algunas tarjetas en su interior.', 'minas', 'Biblioteca Gabriel García Márquez', 15, 'reclamado', None),
    ('Memoria USB 32 GB', 'Tecnología', 'Memoria USB plateada con llavero azul.', 'volador', 'Sala de sistemas', 13, 'reclamado', None),
    ('Tablet Samsung gris', 'Tecnología', 'Tablet gris con funda negra, pantalla de 11 pulgadas.', 'minas', 'Sala de literatura', 20, 'reclamado', None),
    ('Carpeta negra con recibos', 'Documentos', 'Carpeta negra con recibos y un cuaderno de finanzas.', 'volador', 'Secretaría financiera', 18, 'reclamado', None),
    ('Sombrilla azul con estampado', 'Sombrillas', 'Sombrilla azul con estampado floral.', 'minas', 'Cafetería del edificio A', 22, 'reclamado', None),

    # ---- Entregados ----
    ('Cargador iPhone blanco 20W', 'Cargadores', 'Cargador de pared blanco de 20W para iPhone.', 'volador', 'Aulas 101-110', 25, 'entregado', ('Laura Camila Torres', 'CC', '1015487236', '3204587912')),
    ('Termo de acero con franja roja', 'Termos y cafeteras', 'Termo de acero con franja roja y tapa de presión.', 'minas', 'Auditorio de posgrado', 28, 'entregado', ('Andrés Felipe Díaz', 'CC', '1023456789', '3104567821')),
    ('Gafas de sol estilo militar', 'Ropa y accesorios', 'Gafas de sol estilo militar con estuche forrado.', 'volador', 'Canchas de fútbol', 30, 'entregado', ('Valentina Rojas', 'TI', '1098765432', '3009876543')),
    ('Libro de Anatomía Humana', 'Libros y cuadernos', 'Libro de Anatomía Humana con separadores autoadhesivos.', 'minas', 'Facultad de Medicina', 24, 'entregado', ('Sebastián Gómez', 'CC', '1045678912', '3112345678')),
    ('Carpeta azul con documentos', 'Documentos', 'Carpeta azul con documentos personales y copias.', 'volador', 'Parqueadero', 26, 'entregado', ('Mariana Ospina', 'CC', '1122334455', '3123456789')),
]


class Command(BaseCommand):
    help = 'Crea ~30 objetos de prueba con sedes, categorías, estados y fechas variados.'

    def add_arguments(self, parser):
        parser.add_argument('--limpiar', action='store_true', help='Borrar los objetos de prueba antes de recrearlos.')

    def handle(self, *args, **opciones):
        if opciones['limpiar']:
            nombres = [obj[0] for obj in OBJETOS]
            borrados, _ = ObjetoReclamado.objects.filter(nombre_objeto__in=nombres).delete()
            self.stdout.write(self.style.WARNING(f'Objetos de prueba eliminados ({borrados}).'))

        categorias = {}
        for nombre, icono, color, orden in CATEGORIAS:
            cat, _ = Categoria.objects.get_or_create(
                nombre=nombre, defaults={'icono': icono, 'color': color, 'orden': orden},
            )
            categorias[nombre] = cat

        admin = User.objects.filter(is_superuser=True).first()
        estudiante = User.objects.filter(username='estudiante').first()

        hoy = timezone.now().date()

        def hace(dias):
            return timezone.make_aware(datetime.combine(hoy - timedelta(days=dias), time()))

        creados = 0
        existentes = 0
        for nombre, categoria, descripcion, sede, lugar, dias, estado, persona in OBJETOS:
            datos = {
                'categoria': categorias[categoria],
                'descripcion_objeto': descripcion,
                'sede': ObjetoReclamado.Sedes.MINAS if sede == 'minas' else ObjetoReclamado.Sedes.VOLADOR,
                'lugar_encontrado': lugar,
                'fecha_registro': hoy - timedelta(days=dias),
                'estado': estado,
                'registrado_por': admin,
                'foto_base64': '',
            }
            if estado == 'reclamado':
                datos['reclamado_por'] = estudiante
                datos['fecha_reclamo'] = hace(max(0, dias // 2))
            if estado == 'entregado' and persona:
                nombre_persona, tipo_doc, num_doc, telefono = persona
                datos.update({
                    'nombre_persona': nombre_persona,
                    'tipo_documento': tipo_doc,
                    'numero_documento': num_doc,
                    'telefono': telefono,
                    'correo': None,
                    'suministro_correo': False,
                    'fecha_entrega': (hoy - timedelta(days=max(0, dias - 3))).strftime('%d/%m/%Y'),
                    'responsable_entrega': admin.get_full_name() or 'Administración',
                    'reclamado_por': estudiante,
                    'fecha_reclamo': hace(dias + 2),
                })
            _, creado = ObjetoReclamado.objects.get_or_create(nombre_objeto=nombre, defaults=datos)
            if creado:
                creados += 1
            else:
                existentes += 1

        por_sede = {
            'minas': ObjetoReclamado.objects.filter(sede=ObjetoReclamado.Sedes.MINAS).count(),
            'volador': ObjetoReclamado.objects.filter(sede=ObjetoReclamado.Sedes.VOLADOR).count(),
        }
        self.stdout.write(self.style.SUCCESS(f'Objetos creados: {creados}, ya existían: {existentes}.'))
        self.stdout.write(f'Total por sede -> Minas: {por_sede["minas"]}, El Volador: {por_sede["volador"]}.')
        self.stdout.write(self.style.SUCCESS('\nListo. Para verlos entra al panel y abre "Objetos" (filtra por sede/estado).'))