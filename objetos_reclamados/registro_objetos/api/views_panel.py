"""Endpoints del panel de administración. Traducción 1:1 de la lógica que
vivía en ``views/panel_*.py``: mismas reglas de negocio y los mismos
formularios (``ObjetoReclamadoForm``, ``CategoriaForm``, etc.) para no
duplicar validaciones ya probadas — solo cambia HTML por JSON."""
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .. import estadisticas as stats
from ..correo import notificar_respuesta_solicitud
from ..firma_util import firma_path_de
from ..formato_entrega import generar_formato_entrega, generar_formato_entrega_objeto
from ..forms import CategoriaForm, InstruccionesEntregaForm, ObjetoReclamadoForm, UsuarioPanelForm
from ..models import Categoria, ObjetoReclamado, SolicitudReclamacion, obtener_instrucciones_entrega
from ..views.exportar import panel_exportar_csv as _panel_exportar_csv_html
from .serializers import (
    CategoriaSerializer,
    InstruccionesEntregaSerializer,
    ObjetoAdminSerializer,
    SolicitudSerializer,
    UsuarioSerializer,
)


def _pdf(pdf_bytes, nombre):
    respuesta = HttpResponse(pdf_bytes, content_type='application/pdf')
    respuesta['Content-Disposition'] = f'attachment; filename="{nombre}"'
    return respuesta


class PanelDashboardView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        actividad = stats.actividad_reciente(limite=5)
        return Response({
            'resumen': stats.resumen_global(),
            'por_categoria': list(stats.objetos_por_categoria()),
            'por_estado': list(stats.objetos_por_estado()),
            'por_mes': [
                {'mes': m['mes'].strftime('%Y-%m') if m['mes'] else '', 'total': m['total']}
                for m in stats.objetos_por_mes()
            ],
            'actividad': {
                'objetos': ObjetoAdminSerializer(actividad['objetos'], many=True, context={'request': request}).data,
                'solicitudes': SolicitudSerializer(actividad['solicitudes'], many=True, context={'request': request}).data,
            },
        })


class PanelObjetosView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        q = request.query_params.get('q', '').strip()
        estado = request.query_params.get('estado', '')
        categoria_id = request.query_params.get('categoria') or None
        sede = request.query_params.get('sede') or None
        qs = ObjetoReclamado.objects.select_related('categoria', 'registrado_por').all()
        if estado:
            qs = qs.filter(estado=estado)
        if sede:
            qs = qs.filter(sede=sede)
        if categoria_id:
            qs = qs.filter(categoria_id=categoria_id)
        if q:
            qs = qs.filter(
                Q(nombre_objeto__icontains=q)
                | Q(descripcion_objeto__icontains=q)
                | Q(lugar_encontrado__icontains=q)
                | Q(categoria__nombre__icontains=q)
            )
        return Response(ObjetoAdminSerializer(qs, many=True, context={'request': request}).data)

    def post(self, request):
        form = ObjetoReclamadoForm(request.data, request.FILES)
        if not form.is_valid():
            return Response({'errores': form.errors}, status=400)
        objeto = form.save(commit=False)
        objeto.registrado_por = request.user
        if not objeto.fecha_registro:
            objeto.fecha_registro = timezone.localdate()
        objeto.save()
        return Response(ObjetoAdminSerializer(objeto, context={'request': request}).data, status=201)


class PanelObjetoDetalleView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        objeto = get_object_or_404(ObjetoReclamado, pk=pk)
        return Response(ObjetoAdminSerializer(objeto, context={'request': request}).data)

    def put(self, request, pk):
        objeto = get_object_or_404(ObjetoReclamado, pk=pk)
        form = ObjetoReclamadoForm(request.data, request.FILES, instance=objeto)
        if not form.is_valid():
            return Response({'errores': form.errors}, status=400)
        form.save()
        return Response(ObjetoAdminSerializer(objeto, context={'request': request}).data)

    def delete(self, request, pk):
        objeto = get_object_or_404(ObjetoReclamado, pk=pk)
        objeto.delete()
        return Response(status=204)


class PanelObjetosEliminarSeleccionView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        ids = request.data.get('ids', '')
        pks = [valor for valor in str(ids).split(',') if valor.isdigit()]
        if not pks:
            return Response({'detail': 'No seleccionaste ningún objeto para eliminar.'}, status=400)
        total, _ = ObjetoReclamado.objects.filter(pk__in=pks).delete()
        return Response({'eliminados': total})


class PanelObjetoEstadoView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        objeto = get_object_or_404(ObjetoReclamado, pk=pk)
        nuevo = request.data.get('estado')
        if nuevo not in ObjetoReclamado.Estados.values:
            return Response({'detail': 'Estado no válido.'}, status=400)

        if nuevo in (ObjetoReclamado.Estados.RECLAMADO, ObjetoReclamado.Estados.ENTREGADO):
            if not objeto.nombre_persona:
                return Response({
                    'detail': 'Para marcar el objeto como reclamado o entregado primero debes '
                              'registrar los datos de la persona que reclama.',
                }, status=409)

        if nuevo == ObjetoReclamado.Estados.RECLAMADO and not objeto.fecha_reclamo:
            objeto.fecha_reclamo = timezone.now()
            if not objeto.reclamado_por:
                objeto.reclamado_por = request.user
        if nuevo == ObjetoReclamado.Estados.ENTREGADO:
            if not objeto.fecha_entrega:
                objeto.fecha_entrega = timezone.now().strftime('%Y-%m-%d')
            if not objeto.responsable_entrega:
                objeto.responsable_entrega = request.user.get_full_name() or request.user.username
            solicitud_aprobada = SolicitudReclamacion.objects.filter(
                objeto=objeto, estado=SolicitudReclamacion.Estados.APROBADA,
            ).order_by('pk').first()
            if solicitud_aprobada:
                solicitud_aprobada.marcar_entregado(request.user, fecha=objeto.fecha_entrega)
        objeto.estado = nuevo
        objeto.save()
        return Response(ObjetoAdminSerializer(objeto, context={'request': request}).data)


class PanelObjetoFormatoView(APIView):
    """Descarga del PDF de entrega de un objeto ya entregado (exclusivo admin)."""
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        objeto = get_object_or_404(ObjetoReclamado, pk=pk)
        if objeto.estado != ObjetoReclamado.Estados.ENTREGADO:
            return Response(
                {'detail': 'El objeto debe estar en estado «Entregado» para generar el formato.'},
                status=409,
            )
        solicitud_aprobada = SolicitudReclamacion.objects.filter(
            objeto=objeto, estado=SolicitudReclamacion.Estados.APROBADA, fecha_entrega__isnull=False,
        ).order_by('pk').first()
        if solicitud_aprobada:
            solicitud_aprobada.formato_descargado = True
            solicitud_aprobada.save(update_fields=['formato_descargado'])
            pdf_bytes = generar_formato_entrega(solicitud_aprobada)
        else:
            pdf_bytes = generar_formato_entrega_objeto(
                objeto,
                nombre_encargado=objeto.responsable_entrega or
                (request.user.get_full_name() or request.user.username),
                firma_path=firma_path_de(request.user),
            )
        return _pdf(pdf_bytes, f'formato_entrega_{objeto.pk}.pdf')


class PanelSolicitudesView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        estado = request.query_params.get('estado', '') or ''
        qs = SolicitudReclamacion.objects.select_related('usuario', 'objeto', 'objeto__categoria')
        if estado:
            qs = qs.filter(estado=estado)
        else:
            qs = qs.filter(estado__in=[
                SolicitudReclamacion.Estados.PENDIENTE, SolicitudReclamacion.Estados.APELADA,
            ])
        conteo = {
            'pendiente': SolicitudReclamacion.objects.filter(estado=SolicitudReclamacion.Estados.PENDIENTE).count(),
            'apelada': SolicitudReclamacion.objects.filter(estado=SolicitudReclamacion.Estados.APELADA).count(),
            'aprobada': SolicitudReclamacion.objects.filter(estado=SolicitudReclamacion.Estados.APROBADA).count(),
            'rechazada': SolicitudReclamacion.objects.filter(estado=SolicitudReclamacion.Estados.RECHAZADA).count(),
        }
        conteo['por_revisar'] = conteo['pendiente'] + conteo['apelada']
        return Response({
            'solicitudes': SolicitudSerializer(qs, many=True, context={'request': request}).data,
            'conteos': conteo,
        })


class PanelSolicitudDetalleView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        solicitud = get_object_or_404(
            SolicitudReclamacion.objects.select_related('usuario', 'objeto', 'objeto__categoria'), pk=pk,
        )
        config = obtener_instrucciones_entrega()
        return Response({
            'solicitud': SolicitudSerializer(solicitud, context={'request': request}).data,
            'textos_entrega': {'minas': config.texto_minas or '', 'volador': config.texto_volador or ''},
        })


class PanelSolicitudDecisionView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        solicitud = get_object_or_404(SolicitudReclamacion, pk=pk)
        accion = request.data.get('accion')
        comentario = (request.data.get('comentario') or '').strip()
        datos_entrega = (request.data.get('datos_entrega') or '').strip()
        sede = request.data.get('sede') or solicitud.objeto.sede
        if sede not in ObjetoReclamado.Sedes.values:
            sede = solicitud.objeto.sede

        if solicitud.estado not in (SolicitudReclamacion.Estados.PENDIENTE, SolicitudReclamacion.Estados.APELADA):
            return Response({'detail': 'Esta solicitud ya fue respondida.'}, status=409)
        if accion == 'aprobar':
            solicitud.aprobar(request.user, comentario=comentario, datos_entrega=datos_entrega, sede=sede)
            notificar_respuesta_solicitud(solicitud, 'aprobar')
        elif accion == 'rechazar':
            solicitud.rechazar(request.user, comentario=comentario)
            notificar_respuesta_solicitud(solicitud, 'rechazar')
        else:
            return Response({'detail': 'Acción no válida.'}, status=400)
        return Response(SolicitudSerializer(solicitud, context={'request': request}).data)


class PanelSolicitudFormatoView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        solicitud = get_object_or_404(SolicitudReclamacion, pk=pk)
        if not solicitud.esta_entregada:
            return Response({
                'detail': 'El formato de entrega está disponible cuando el objeto haya sido '
                          'marcado como entregado.',
            }, status=409)
        if not solicitud.formato_descargado:
            solicitud.formato_descargado = True
            solicitud.save(update_fields=['formato_descargado'])
        return _pdf(generar_formato_entrega(solicitud), f'formato_entrega_{solicitud.pk}.pdf')


class PanelSolicitudEntregarView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        solicitud = get_object_or_404(SolicitudReclamacion.objects.select_related('objeto'), pk=pk)
        if solicitud.estado != SolicitudReclamacion.Estados.APROBADA:
            return Response({'detail': 'Solo puedes entregar una solicitud aprobada.'}, status=409)
        if solicitud.objeto.estado == ObjetoReclamado.Estados.ENTREGADO and solicitud.fecha_entrega:
            return Response({'detail': 'Este objeto ya fue marcado como entregado.'}, status=409)
        solicitud.marcar_entregado(request.user)
        return Response(SolicitudSerializer(solicitud, context={'request': request}).data)


class PanelConfiguracionEntregaView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response(InstruccionesEntregaSerializer(obtener_instrucciones_entrega()).data)

    def put(self, request):
        config = obtener_instrucciones_entrega()
        form = InstruccionesEntregaForm(request.data, instance=config)
        if not form.is_valid():
            return Response({'errores': form.errors}, status=400)
        form.save()
        return Response(InstruccionesEntregaSerializer(config).data)


class PanelCategoriasView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        categorias = Categoria.objects.annotate(total_objetos=Count('objetos'))
        return Response(CategoriaSerializer(categorias, many=True).data)

    def post(self, request):
        form = CategoriaForm(request.data)
        if not form.is_valid():
            return Response({'errores': form.errors}, status=400)
        categoria = form.save()
        return Response(CategoriaSerializer(categoria).data, status=201)


class PanelCategoriaDetalleView(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, pk):
        categoria = get_object_or_404(Categoria, pk=pk)
        form = CategoriaForm(request.data, instance=categoria)
        if not form.is_valid():
            return Response({'errores': form.errors}, status=400)
        form.save()
        return Response(CategoriaSerializer(categoria).data)

    def delete(self, request, pk):
        categoria = get_object_or_404(Categoria, pk=pk)
        if categoria.objetos.exists():
            return Response({'detail': 'No puedes eliminar una categoría que tiene objetos.'}, status=409)
        categoria.delete()
        return Response(status=204)


def _guardar_usuario_desde_form(form, usuario=None):
    datos = form.cleaned_data
    if usuario is None:
        usuario = User.objects.create_user(
            username=datos['username'], email=datos['email'], password=datos['contrasena'],
            first_name=datos.get('first_name', ''), last_name=datos.get('last_name', ''),
        )
    else:
        usuario.username = datos['username']
        usuario.email = datos['email']
        usuario.first_name = datos.get('first_name', '')
        usuario.last_name = datos.get('last_name', '')
        if datos.get('contrasena'):
            usuario.set_password(datos['contrasena'])
    usuario.is_staff = (datos['rol'] == 'admin')
    usuario.is_active = datos.get('is_active', True)
    usuario.save()
    perfil = usuario.perfil
    perfil.tipo_documento = datos.get('tipo_documento', '')
    perfil.numero_documento = datos.get('numero_documento', '').strip()
    perfil.telefono = datos.get('telefono', '').strip()
    perfil.programa = datos.get('programa', '').strip()
    if datos.get('firma'):
        perfil.firma = datos['firma']
    perfil.save()
    return usuario


class PanelUsuariosView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        q = request.query_params.get('q', '').strip()
        rol = request.query_params.get('rol', '')
        usuarios = User.objects.select_related('perfil').order_by('-is_staff', 'username')
        if rol == 'admin':
            usuarios = usuarios.filter(is_staff=True)
        elif rol == 'estudiante':
            usuarios = usuarios.filter(is_staff=False)
        if q:
            usuarios = usuarios.filter(
                Q(username__icontains=q) | Q(email__icontains=q)
                | Q(first_name__icontains=q) | Q(last_name__icontains=q)
            )
        return Response(UsuarioSerializer(usuarios, many=True, context={'request': request}).data)

    def post(self, request):
        form = UsuarioPanelForm(request.data, request.FILES, requiere_contrasena=True)
        if not form.is_valid():
            return Response({'errores': form.errors}, status=400)
        try:
            usuario = _guardar_usuario_desde_form(form)
        except IntegrityError:
            return Response({'detail': 'Ya existe un usuario con ese nombre o correo.'}, status=409)
        return Response(UsuarioSerializer(usuario, context={'request': request}).data, status=201)


class PanelUsuarioDetalleView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        usuario = get_object_or_404(User.objects.select_related('perfil'), pk=pk)
        return Response(UsuarioSerializer(usuario, context={'request': request}).data)

    def put(self, request, pk):
        usuario = get_object_or_404(User.objects.select_related('perfil'), pk=pk)
        form = UsuarioPanelForm(request.data, request.FILES, requiere_contrasena=False)
        if not form.is_valid():
            return Response({'errores': form.errors}, status=400)
        if usuario.pk == request.user.pk and not form.cleaned_data.get('is_active', False):
            return Response({'detail': 'No puedes desactivar tu propia cuenta.'}, status=409)
        try:
            _guardar_usuario_desde_form(form, usuario=usuario)
        except IntegrityError:
            return Response({'detail': 'Ya existe otro usuario con ese nombre o correo.'}, status=409)
        return Response(UsuarioSerializer(usuario, context={'request': request}).data)


class PanelExportarCsvView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return _panel_exportar_csv_html(request._request)
