"""Serializers de la API REST. Reflejan los mismos campos que las plantillas
HTML mostraban, separando lo público (estudiante) de lo administrativo para
no exponer datos personales del reclamante a quien no debe verlos."""
from django.contrib.auth.models import User
from rest_framework import serializers

from ..models import (
    Categoria,
    InstruccionesEntrega,
    ObjetoReclamado,
    PerfilUsuario,
    SolicitudReclamacion,
)


def _url_absoluta(context, url):
    if not url:
        return None
    request = context.get('request')
    return request.build_absolute_uri(url) if request else url


class CategoriaSerializer(serializers.ModelSerializer):
    total_disponibles = serializers.IntegerField(read_only=True, required=False)
    total_objetos = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'icono', 'color', 'orden', 'total_disponibles', 'total_objetos']


class ObjetoPublicoSerializer(serializers.ModelSerializer):
    """Lo que puede ver un estudiante: sin datos del reclamante."""
    categoria_nombre = serializers.CharField(source='etiqueta_categoria', read_only=True)
    categoria_icono = serializers.CharField(source='icono', read_only=True)
    categoria_color = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    sede_display = serializers.CharField(source='get_sede_display', read_only=True)
    foto_url = serializers.SerializerMethodField()

    class Meta:
        model = ObjetoReclamado
        fields = [
            'id', 'nombre_objeto', 'categoria', 'categoria_nombre', 'categoria_icono', 'categoria_color',
            'descripcion_objeto', 'sede', 'sede_display', 'lugar_encontrado',
            'fecha_registro', 'foto_url', 'estado', 'estado_display',
        ]

    def get_categoria_color(self, obj):
        return obj.categoria.color if obj.categoria else None

    def get_foto_url(self, obj):
        return _url_absoluta(self.context, obj.foto_data)


class ObjetoAdminSerializer(serializers.ModelSerializer):
    """Vista completa para el panel: incluye los datos del reclamante."""
    categoria_nombre = serializers.CharField(source='etiqueta_categoria', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    sede_display = serializers.CharField(source='get_sede_display', read_only=True)
    foto_url = serializers.SerializerMethodField()
    registrado_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = ObjetoReclamado
        fields = [
            'id', 'nombre_objeto', 'categoria', 'categoria_nombre', 'descripcion_objeto',
            'sede', 'sede_display', 'lugar_encontrado', 'fecha_registro', 'foto_url',
            'estado', 'estado_display', 'registrado_por_nombre',
            'nombre_persona', 'tipo_documento', 'numero_documento', 'telefono',
            'suministro_correo', 'correo', 'fecha_entrega', 'responsable_entrega',
        ]

    def get_foto_url(self, obj):
        return _url_absoluta(self.context, obj.foto_data)

    def get_registrado_por_nombre(self, obj):
        return obj.registrado_por.username if obj.registrado_por else ''


class SolicitudSerializer(serializers.ModelSerializer):
    objeto_detalle = ObjetoPublicoSerializer(source='objeto', read_only=True)
    usuario_nombre = serializers.SerializerMethodField()
    usuario_email = serializers.EmailField(source='usuario.email', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    puede_apelar = serializers.BooleanField(read_only=True)
    esta_entregada = serializers.BooleanField(read_only=True)

    class Meta:
        model = SolicitudReclamacion
        fields = [
            'id', 'objeto', 'objeto_detalle', 'usuario', 'usuario_nombre', 'usuario_email',
            'mensaje', 'tipo_documento', 'numero_documento', 'telefono',
            'estado', 'estado_display', 'fecha', 'comentario_admin',
            'fue_apelada', 'apelacion', 'fecha_apelacion', 'datos_entrega',
            'fecha_entrega', 'formato_descargado', 'puede_apelar', 'esta_entregada',
        ]
        read_only_fields = [
            'usuario', 'estado', 'fecha', 'comentario_admin', 'fue_apelada',
            'fecha_apelacion', 'datos_entrega', 'fecha_entrega', 'formato_descargado',
        ]

    def get_usuario_nombre(self, obj):
        return obj.usuario.get_full_name() or obj.usuario.username


class InstruccionesEntregaSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstruccionesEntrega
        fields = ['texto_minas', 'texto_volador', 'fecha_actualizada']


class PerfilSerializer(serializers.ModelSerializer):
    firma_url = serializers.SerializerMethodField()

    class Meta:
        model = PerfilUsuario
        fields = ['tipo_documento', 'numero_documento', 'telefono', 'programa', 'firma_url']

    def get_firma_url(self, obj):
        return _url_absoluta(self.context, obj.firma.url if obj.firma else None)


class UsuarioSerializer(serializers.ModelSerializer):
    """Lectura de cuentas para el panel de administración."""
    perfil = serializers.SerializerMethodField()
    rol = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'rol', 'perfil']

    def get_rol(self, obj):
        return 'admin' if obj.is_staff else 'estudiante'

    def get_perfil(self, obj):
        perfil = getattr(obj, 'perfil', None)
        if not perfil:
            return None
        return PerfilSerializer(perfil, context=self.context).data


class UsuarioActualSerializer(serializers.ModelSerializer):
    """Respuesta de /auth/me/: identidad del usuario autenticado en la SPA."""
    rol = serializers.SerializerMethodField()
    perfil = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'rol', 'perfil']

    def get_rol(self, obj):
        return 'admin' if obj.is_staff else 'estudiante'

    def get_perfil(self, obj):
        perfil = getattr(obj, 'perfil', None)
        if not perfil:
            return None
        return PerfilSerializer(perfil, context=self.context).data
