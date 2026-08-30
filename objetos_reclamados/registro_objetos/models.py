from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Categoria(models.Model):
    """Categorías para clasificar los objetos (ej. Termos, Documentos, Cargadores)."""
    nombre = models.CharField('Nombre', max_length=100, unique=True)
    icono = models.CharField(
        'Ícono', max_length=10, blank=True, default='',
        help_text='Ícono del catálogo que identifica la categoría.',
    )
    color = models.CharField('Color (hex)', max_length=7, default='#0b7a54')
    orden = models.PositiveIntegerField('Orden', default=0)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre


class ObjetoReclamado(models.Model):
    """Objeto perdido/encontrado registrado en la plataforma.

    Un objeto inicia el ciclo como ``disponible`` (sin dueño asignado),
    luego pasa a ``reclamado`` (alguien solicitó su reclamo y fue aprobado)
    y finalmente a ``entregado`` cuando el responsable hace la entrega.
    """

    class Estados(models.TextChoices):
        DISPONIBLE = 'disponible', 'Disponible'
        RECLAMADO = 'reclamado', 'Reclamado'
        ENTREGADO = 'entregado', 'Entregado'

    class Sedes(models.TextChoices):
        MINAS = 'minas', 'Sede Minas'
        VOLADOR = 'volador', 'Sede El Volador'

    # Información del objeto
    nombre_objeto = models.CharField('Nombre del objeto', max_length=120, blank=True)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, null=True, blank=True,
        related_name='objetos', verbose_name='Categoría',
    )
    descripcion_objeto = models.TextField('Descripción', blank=True)
    sede = models.CharField(
        'Sede', max_length=20, choices=Sedes.choices,
        default=Sedes.MINAS, db_index=True,
        help_text='Sede donde se encontró o se entrega el objeto.',
    )
    lugar_encontrado = models.CharField('Lugar donde fue encontrado', max_length=150, blank=True)
    fecha_registro = models.DateField('Fecha de registro', auto_now_add=True, null=True)
    foto = models.ImageField('Foto', upload_to='objetos/', blank=True, null=True)
    estado = models.CharField(
        'Estado', max_length=20, choices=Estados.choices,
        default=Estados.DISPONIBLE, db_index=True,
    )
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='objetos_registrados', verbose_name='Registrado por',
    )

    # Datos de la persona que reclama / entrega
    nombre_persona = models.CharField('Nombre de quien reclama', max_length=100, blank=True)
    tipo_documento = models.CharField('Tipo de documento', max_length=50, blank=True)
    numero_documento = models.CharField('Número de documento', max_length=50, blank=True)
    telefono = models.CharField('Teléfono', max_length=20, blank=True)
    suministro_correo = models.BooleanField('¿Suministró correo?', default=False)
    correo = models.EmailField('Correo', blank=True, null=True)
    fecha_entrega = models.CharField('Fecha de entrega', max_length=100, blank=True)
    responsable_entrega = models.CharField('Responsable de la entrega', max_length=100, blank=True)

    # Trazabilidad del reclamo
    reclamado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='objetos_reclamados', verbose_name='Reclamado por (usuario)',
    )
    fecha_reclamo = models.DateTimeField('Fecha del reclamo', null=True, blank=True)

    class Meta:
        verbose_name = 'Objeto'
        verbose_name_plural = 'Objetos'
        ordering = ['-fecha_registro', '-id']

    def __str__(self):
        nombre = self.nombre_objeto or (self.descripcion_objeto[:40] + '…' if self.descripcion_objeto else 'Objeto')
        return f'{nombre} · {self.get_estado_display()}'

    @property
    def etiqueta_categoria(self):
        return self.categoria.nombre if self.categoria else 'Sin categoría'

    @property
    def icono(self):
        return self.categoria.icono if self.categoria else ''

    @property
    def esta_disponible(self):
        return self.estado == self.Estados.DISPONIBLE


class PerfilUsuario(models.Model):
    """Datos extra del usuario (estudiante)."""
    class TiposDocumento(models.TextChoices):
        CC = 'CC', 'Cédula de ciudadanía'
        TI = 'TI', 'Tarjeta de identidad'
        CE = 'CE', 'Cédula de extranjería'
        PEP = 'PEP', 'Pasaporte'

    usuario = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='perfil',
    )
    tipo_documento = models.CharField(
        'Tipo de documento', max_length=10, choices=TiposDocumento.choices, blank=True,
    )
    numero_documento = models.CharField('Número de documento', max_length=50, blank=True)
    telefono = models.CharField('Teléfono', max_length=20, blank=True)
    programa = models.CharField('Programa / Carrera', max_length=120, blank=True)

    class Meta:
        verbose_name = 'Perfil de usuario'
        verbose_name_plural = 'Perfiles de usuario'

    def __str__(self):
        return f'Perfil de {self.usuario.username}'


class SolicitudReclamacion(models.Model):
    """Solicitud que hace un estudiante porque cree que el objeto es suyo.

    El administrador la aprueba (el objeto pasa a ``reclamado``) o la rechaza.
    """

    class Estados(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        APELADA = 'apelada', 'Apelada'
        APROBADA = 'aprobada', 'Aprobada'
        RECHAZADA = 'rechazada', 'Rechazada'

    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='solicitudes',
        verbose_name='Estudiante',
    )
    objeto = models.ForeignKey(
        ObjetoReclamado, on_delete=models.CASCADE, related_name='solicitudes',
        verbose_name='Objeto',
    )
    mensaje = models.TextField('¿Por qué crees que es tuyo? (opcional)', blank=True)
    estado = models.CharField(
        'Estado', max_length=20, choices=Estados.choices, default=Estados.PENDIENTE,
        db_index=True,
    )
    fecha = models.DateTimeField('Fecha de la solicitud', auto_now_add=True)
    respondida_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='solicitudes_respondidas', verbose_name='Respondida por',
    )
    fecha_respuesta = models.DateTimeField('Fecha de respuesta', null=True, blank=True)
    respuesta_vista = models.BooleanField(
        '¿Respuesta vista por el estudiante?', default=True,
        help_text='Se marca como no vista cuando hay una respuesta nueva del admin.',
    )
    comentario_admin = models.TextField(
        'Comentario del administrador', blank=True,
        help_text='Motivo de la decisión que verá el estudiante.',
    )
    # Apelación: una sola vez por solicitud
    fue_apelada = models.BooleanField('¿Fue apelada?', default=False)
    apelacion = models.TextField('Motivo de la apelación', blank=True)
    fecha_apelacion = models.DateTimeField('Fecha de apelación', null=True, blank=True)
    datos_entrega = models.TextField(
        'Datos para reclamar el objeto', blank=True,
        help_text='Información específica de esta entrega (lugar, horario). Se '
                  'muestra al estudiante al aprobar; si está vacía se usa el '
                  'texto general de configuración.',
    )

    class Meta:
        verbose_name = 'Solicitud de reclamación'
        verbose_name_plural = 'Solicitudes de reclamación'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.usuario} → {self.objeto} ({self.get_estado_display()})'

    @property
    def puede_apelar(self):
        """Solo se puede apelar una vez y únicamente cuando fue rechazada."""
        return (
            self.estado == self.Estados.RECHAZADA
            and not self.fue_apelada
        )

    def apelar(self, usuario, motivo):
        if not self.puede_apelar:
            raise ValueError('Esta solicitud ya no admite apelación.')
        if usuario != self.usuario:
            raise ValueError('Solo el estudiante solicitante puede apelar.')
        self.estado = self.Estados.APELADA
        self.fue_apelada = True
        self.apelacion = (motivo or '').strip()
        self.fecha_apelacion = timezone.now()
        self.save()

    def aprobar(self, admin, comentario='', datos_entrega=''):
        self.estado = self.Estados.APROBADA
        self.respondida_por = admin
        self.fecha_respuesta = timezone.now()
        self.comentario_admin = (comentario or '').strip()
        self.datos_entrega = (datos_entrega or '').strip()
        self.respuesta_vista = False
        self.save()
        objeto = self.objeto
        objeto.estado = ObjetoReclamado.Estados.RECLAMADO
        objeto.reclamado_por = self.usuario
        objeto.fecha_reclamo = timezone.now()
        perfil = getattr(self.usuario, 'perfil', None)
        if perfil:
            objeto.nombre_persona = self.usuario.get_full_name() or self.usuario.username
            objeto.tipo_documento = perfil.get_tipo_documento_display()
            objeto.numero_documento = perfil.numero_documento or ''
            objeto.telefono = perfil.telefono or ''
            if self.usuario.email:
                objeto.correo = self.usuario.email
                objeto.suministro_correo = True
        objeto.save()

    def rechazar(self, admin, comentario=''):
        self.estado = self.Estados.RECHAZADA
        self.respondida_por = admin
        self.fecha_respuesta = timezone.now()
        self.comentario_admin = (comentario or '').strip()
        self.respuesta_vista = False
        self.save()


class InstruccionesEntrega(models.Model):
    """Instrucciones globales sobre dónde y cómo reclamar un objeto aprobado.

    Es un singleton (pk=1): el administrador la edita desde el panel y el
    estudiante la ve en su solicitud aprobada.
    """

    texto = models.TextField(
        'Instrucciones para reclamar el objeto', blank=True,
        help_text='Lugar, horario, oficina o cualquier indicación para la entrega.',
    )
    fecha_actualizada = models.DateTimeField('Actualizado', auto_now=True)

    class Meta:
        verbose_name = 'Instrucciones de entrega'
        verbose_name_plural = 'Instrucciones de entrega'

    def __str__(self):
        return 'Instrucciones de entrega'


def obtener_instrucciones_entrega():
    """Devuelve (creándola si no existe) la única fila del singleton."""
    obj, _ = InstruccionesEntrega.objects.get_or_create(pk=1)
    return obj