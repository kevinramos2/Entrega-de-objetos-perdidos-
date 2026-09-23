"""Endpoints del estudiante: búsqueda, detalle, solicitudes y apelaciones.
Traducción 1:1 de la lógica que ya vivía en ``views/estudiante.py`` — mismas
reglas, misma reutilización de ``forms`` y ``estadisticas``, solo cambia el
formato de salida de HTML a JSON."""
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .. import estadisticas as stats
from ..forms import ApelacionForm, SolicitudForm
from ..models import (
    Categoria,
    InstruccionesEntrega,
    ObjetoReclamado,
    SolicitudReclamacion,
    obtener_instrucciones_entrega,
)
from ..views.helpers import _actualizar_perfil_desde_solicitud, estados_activos_solicitud
from .serializers import (
    CategoriaSerializer,
    InstruccionesEntregaSerializer,
    ObjetoPublicoSerializer,
    SolicitudSerializer,
)


class ResumenView(APIView):
    """Indicadores y mensajes que se muestran en Inicio y en el listado."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'resumen': stats.resumen_global(),
            'mensajes': stats.informacion_para_estudiantes(),
        })


class CategoriasView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categorias = Categoria.objects.all()
        return Response(CategoriaSerializer(categorias, many=True, context={'request': request}).data)


class ObjetosDisponiblesView(APIView):
    """Listado con búsqueda y filtros de categoría/sede (solo disponibles)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        q = request.query_params.get('q', '').strip()
        categoria_id = request.query_params.get('categoria') or None
        sede = request.query_params.get('sede') or None
        objetos = stats.buscar_objetos(q, categoria_id, sede=sede, solo_disponibles=True)
        return Response(ObjetoPublicoSerializer(objetos, many=True, context={'request': request}).data)


class ObjetoDetalleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        objeto = get_object_or_404(
            ObjetoReclamado.objects.select_related('categoria'),
            pk=pk, estado=ObjetoReclamado.Estados.DISPONIBLE,
        )
        ya_solicito = SolicitudReclamacion.objects.filter(
            usuario=request.user, objeto=objeto,
            estado__in=estados_activos_solicitud(),
        ).exists()
        datos = ObjetoPublicoSerializer(objeto, context={'request': request}).data
        datos['ya_solicito'] = ya_solicito
        return Response(datos)


class SolicitarReclamacionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        objeto = get_object_or_404(ObjetoReclamado, pk=pk)
        if not objeto.esta_disponible:
            return Response({'detail': 'Este objeto ya no está disponible.'}, status=409)

        ya_existe = SolicitudReclamacion.objects.filter(
            usuario=request.user, objeto=objeto,
            estado__in=estados_activos_solicitud(),
        ).exists()
        if ya_existe:
            return Response({'detail': 'Ya tienes una solicitud pendiente para este objeto.'}, status=409)

        form = SolicitudForm(request.data)
        if not form.is_valid():
            return Response({'errores': form.errors}, status=400)

        solicitud = SolicitudReclamacion.objects.create(
            usuario=request.user,
            objeto=objeto,
            mensaje=form.cleaned_data['mensaje'].strip(),
            tipo_documento=form.cleaned_data['tipo_documento'],
            numero_documento=form.cleaned_data['numero_documento'].strip(),
            telefono=form.cleaned_data['telefono'].strip(),
        )
        _actualizar_perfil_desde_solicitud(request.user, form.cleaned_data)
        return Response(SolicitudSerializer(solicitud, context={'request': request}).data, status=201)


class MisSolicitudesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Al consultar, las respuestas pendientes de ver se marcan como vistas.
        request.user.solicitudes.filter(
            estado__in=[SolicitudReclamacion.Estados.APROBADA, SolicitudReclamacion.Estados.RECHAZADA],
            respuesta_vista=False,
        ).update(respuesta_vista=True)
        solicitudes = request.user.solicitudes.select_related('objeto', 'objeto__categoria')
        config = obtener_instrucciones_entrega()
        return Response({
            'solicitudes': SolicitudSerializer(solicitudes, many=True, context={'request': request}).data,
            'instrucciones': InstruccionesEntregaSerializer(config).data,
        })


class ApelarSolicitudView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        solicitud = get_object_or_404(SolicitudReclamacion, pk=pk, usuario=request.user)
        if not solicitud.puede_apelar:
            return Response({
                'detail': 'Esta solicitud ya no admite apelación: solo puedes apelar una vez '
                          'y únicamente cuando la respuesta fue un rechazo.',
            }, status=409)

        form = ApelacionForm(request.data)
        if not form.is_valid():
            return Response({'errores': form.errors}, status=400)

        solicitud.apelar(request.user, form.cleaned_data['motivo'])
        return Response(SolicitudSerializer(solicitud, context={'request': request}).data)
