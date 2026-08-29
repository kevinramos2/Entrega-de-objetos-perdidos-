import csv

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import IntegrityError
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_POST

import json

from . import estadisticas as stats
from .forms import (
    CategoriaForm,
    InicioSesionForm,
    ObjetoReclamadoForm,
    SolicitudForm,
    UsuarioPanelForm,
)
from .models import (
    Categoria,
    ObjetoReclamado,
    PerfilUsuario,
    SolicitudReclamacion,
)

# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

MAX_INTENTOS_FALLIDOS = 5
VENTANA_BLOQUEO_SEG = 900  # 15 minutos


def redirigir_por_rol(user):
    if user.is_staff:
        return redirect('panel_inicio')
    return redirect('lista_objetos')


def _clave_login(identificador):
    return f'login_fallos:{identificador.lower()}'


def _clave_ip(direccion):
    return f'login_fallos_ip:{direccion}'


def intentos_bloqueados(*claves):
    return any(cache.get(c, 0) >= MAX_INTENTOS_FALLIDOS for c in claves)


def registrar_intento_fallido(*claves):
    for clave in claves:
        cache.set(clave, cache.get(clave, 0) + 1, VENTANA_BLOQUEO_SEG)


def limpiar_intentos(*claves):
    for clave in claves:
        cache.delete(clave)


def obtener_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def serializar_json(datos):
    return mark_safe(json.dumps(datos, ensure_ascii=False))

# ---------------------------------------------------------------------------
# Público / Autenticación
# ---------------------------------------------------------------------------


def inicio(request):
    if request.user.is_authenticated:
        return redirigir_por_rol(request.user)
    resumen = stats.resumen_global()
    recientes = (
        ObjetoReclamado.objects
        .select_related('categoria')
        .filter(estado=ObjetoReclamado.Estados.DISPONIBLE)[:3]
    )
    return render(request, 'objetos/home.html', {
        'resumen': resumen,
        'recientes': recientes,
        'mensajes': stats.informacion_para_estudiantes()[:3],
    })


def registro_usuario(request):
    """El registro manual se deshabilitó: el acceso es con correo institucional."""
    if request.user.is_authenticated:
        return redirigir_por_rol(request.user)
    return redirect('login')


def iniciar_sesion(request):
    if request.user.is_authenticated:
        return redirigir_por_rol(request.user)

    form = InicioSesionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        identificador = form.cleaned_data['identificador'].strip()
        clave = form.cleaned_data['contrasena']
        ip = obtener_ip(request)
        claves = [_clave_login(identificador), _clave_ip(ip)]

        if intentos_bloqueados(*claves):
            messages.error(
                request,
                'Demasiados intentos fallidos. Espera unos minutos e inténtalo de nuevo.',
            )
        else:
            usuario = authenticate(request, username=identificador, password=clave)
            if usuario is None and '@' in identificador:
                # Permitir iniciar sesión también con el correo institucional
                try:
                    cuenta = User.objects.get(email__iexact=identificador)
                    usuario = authenticate(request, username=cuenta.username, password=clave)
                except User.DoesNotExist:
                    usuario = None

            if usuario is not None and usuario.is_active:
                login(request, usuario)
                limpiar_intentos(*claves)
                messages.success(
                    request,
                    f'¡Hola de nuevo, {usuario.first_name or usuario.username}!',
                )
                return redirigir_por_rol(usuario)

            registrar_intento_fallido(*claves)
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'registro/login.html', {'form': form})


@require_POST
def cerrar_sesion(request):
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect('inicio')

# ---------------------------------------------------------------------------
# Estudiante
# ---------------------------------------------------------------------------


@login_required
def lista_objetos(request):
    q = request.GET.get('q', '').strip()
    categoria_id = request.GET.get('categoria', '') or None
    objetos = stats.buscar_objetos(q, categoria_id, solo_disponibles=True)
    return render(request, 'objetos/listado.html', {
        'objetos': objetos,
        'categorias': Categoria.objects.all(),
        'categoria_actual': categoria_id,
        'q': q,
        'resumen': stats.resumen_global(),
        'mensajes': stats.informacion_para_estudiantes(),
    })


@login_required
def detalle_objeto(request, pk):
    objeto = get_object_or_404(
        ObjetoReclamado.objects.select_related('categoria'),
        pk=pk,
        estado=ObjetoReclamado.Estados.DISPONIBLE,
    )
    ya_solicito = SolicitudReclamacion.objects.filter(
        usuario=request.user, objeto=objeto,
        estado=SolicitudReclamacion.Estados.PENDIENTE,
    ).exists()
    return render(request, 'objetos/detalle.html', {
        'objeto': objeto,
        'form': SolicitudForm(),
        'ya_solicito': ya_solicito,
    })


@login_required
@require_POST
def solicitar_reclamacion(request, pk):
    objeto = get_object_or_404(ObjetoReclamado, pk=pk)
    if not objeto.esta_disponible:
        messages.info(request, 'Este objeto ya no está disponible.')
        return redirect('mis_solicitudes')

    ya_existe = SolicitudReclamacion.objects.filter(
        usuario=request.user, objeto=objeto,
        estado=SolicitudReclamacion.Estados.PENDIENTE,
    ).exists()
    if ya_existe:
        messages.warning(request, 'Ya tienes una solicitud pendiente para este objeto.')
        return redirect('mis_solicitudes')

    form = SolicitudForm(request.POST)
    if form.is_valid():
        SolicitudReclamacion.objects.create(
            usuario=request.user,
            objeto=objeto,
            mensaje=form.cleaned_data['mensaje'].strip(),
        )
        messages.success(
            request,
            '¡Listo! Tu solicitud fue enviada. La coordinación revisará que sea '
            'tu objeto y te contactará por el medio que registraste.',
        )
    else:
        messages.error(request, 'No pudimos procesar la solicitud. Intenta de nuevo.')
    return redirect('mis_solicitudes')


@login_required
def mis_solicitudes(request):
    solicitudes = (
        request.user.solicitudes
        .select_related('objeto', 'objeto__categoria')
    )
    return render(request, 'objetos/mis_solicitudes.html', {
        'solicitudes': solicitudes,
    })

# ---------------------------------------------------------------------------
# Panel del administrador
# ---------------------------------------------------------------------------


@staff_member_required
def panel_inicio(request):
    resumen = stats.resumen_global()
    por_categoria = stats.objetos_por_categoria()
    por_estado = stats.objetos_por_estado()
    por_mes = stats.objetos_por_mes()
    actividad = stats.actividad_reciente(limite=8)

    nombres_estado = dict(ObjetoReclamado.Estados.choices)

    def iniciales_categoria(nombre):
        return (nombre or '—').strip()[:2].upper() or '—'

    context = {
        'resumen': resumen,
        'actividad': actividad,
        'chart_categoria_labels': serializar_json([c['categoria__nombre'] or 'Sin categoría' for c in por_categoria]),
        'chart_categoria_iconos': serializar_json([iniciales_categoria(c['categoria__nombre']) for c in por_categoria]),
        'chart_categoria_values': serializar_json([c['total'] for c in por_categoria]),
        'chart_estado_labels': serializar_json([nombres_estado.get(e['estado'], e['estado']) for e in por_estado]),
        'chart_estado_values': serializar_json([e['total'] for e in por_estado]),
        'chart_mes_labels': serializar_json([m['mes'].strftime('%Y-%m') if m['mes'] else '' for m in por_mes]),
        'chart_mes_values': serializar_json([m['total'] for m in por_mes]),
    }
    return render(request, 'panel/inicio.html', context)


@staff_member_required
def panel_objetos(request):
    q = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '')
    categoria_id = request.GET.get('categoria', '') or None
    qs = ObjetoReclamado.objects.select_related('categoria', 'registrado_por').all()
    if estado:
        qs = qs.filter(estado=estado)
    if categoria_id:
        qs = qs.filter(categoria_id=categoria_id)
    if q:
        qs = stats.buscar_objetos(q)
    return render(request, 'panel/objetos_lista.html', {
        'objetos': qs,
        'categorias': Categoria.objects.all(),
        'estados': ObjetoReclamado.Estados.choices,
        'q': q, 'estado': estado, 'categoria_id': categoria_id,
    })


@staff_member_required
def panel_objeto_nuevo(request):
    form = ObjetoReclamadoForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        objeto = form.save(commit=False)
        objeto.registrado_por = request.user
        objeto.save()
        messages.success(request, f'Objeto «{objeto}» registrado correctamente.')
        return redirect('panel_objetos')
    return render(request, 'panel/objeto_form.html', {
        'form': form, 'titulo': 'Registrar nuevo objeto', 'es_nuevo': True,
    })


@staff_member_required
def panel_objeto_editar(request, pk):
    objeto = get_object_or_404(ObjetoReclamado, pk=pk)
    form = ObjetoReclamadoForm(
        request.POST or None, request.FILES or None, instance=objeto,
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Los cambios fueron guardados.')
        return redirect('panel_objetos')
    return render(request, 'panel/objeto_form.html', {
        'form': form, 'titulo': 'Editar objeto', 'es_nuevo': False, 'objeto': objeto,
    })


@staff_member_required
@require_POST
def panel_objeto_eliminar(request, pk):
    objeto = get_object_or_404(ObjetoReclamado, pk=pk)
    nombre = str(objeto)
    objeto.delete()
    messages.success(request, f'Se eliminó el registro «{nombre}».')
    return redirect('panel_objetos')


@staff_member_required
@require_POST
def panel_objeto_estado(request, pk):
    objeto = get_object_or_404(ObjetoReclamado, pk=pk)
    nuevo = request.POST.get('estado')
    valores = ObjetoReclamado.Estados.values
    if nuevo not in valores:
        messages.error(request, 'Estado no válido.')
        return redirect('panel_objetos')

    if nuevo in (ObjetoReclamado.Estados.RECLAMADO, ObjetoReclamado.Estados.ENTREGADO):
        if not objeto.nombre_persona:
            messages.error(
                request,
                'Para marcar el objeto como reclamado o entregado primero debes '
                'registrar los datos de la persona que reclama.',
            )
            return redirect('panel_objeto_editar', pk=objeto.pk)

    if nuevo == ObjetoReclamado.Estados.RECLAMADO and not objeto.fecha_reclamo:
        objeto.fecha_reclamo = timezone.now()
        if not objeto.reclamado_por:
            objeto.reclamado_por = request.user
    if nuevo == ObjetoReclamado.Estados.ENTREGADO:
        if not objeto.fecha_entrega:
            objeto.fecha_entrega = timezone.now().strftime('%Y-%m-%d')
        if not objeto.responsable_entrega:
            objeto.responsable_entrega = request.user.get_full_name() or request.user.username
    objeto.estado = nuevo
    objeto.save()
    messages.success(request, f'El objeto pasó a estado «{objeto.get_estado_display()}».')
    return redirect('panel_objetos')


@staff_member_required
def panel_solicitudes(request):
    estado = request.GET.get('estado', '') or ''
    qs = SolicitudReclamacion.objects.select_related('usuario', 'objeto', 'objeto__categoria')
    if estado:
        qs = qs.filter(estado=estado)
    else:
        qs = qs.filter(estado=SolicitudReclamacion.Estados.PENDIENTE)
    return render(request, 'panel/solicitudes.html', {
        'solicitudes': qs,
        'estado': estado,
        'estados': SolicitudReclamacion.Estados.choices,
        'conteos': {
            'pendiente': SolicitudReclamacion.objects.filter(estado=SolicitudReclamacion.Estados.PENDIENTE).count(),
            'aprobada': SolicitudReclamacion.objects.filter(estado=SolicitudReclamacion.Estados.APROBADA).count(),
            'rechazada': SolicitudReclamacion.objects.filter(estado=SolicitudReclamacion.Estados.RECHAZADA).count(),
        },
    })


@staff_member_required
def panel_solicitud_detalle(request, pk):
    solicitud = get_object_or_404(
        SolicitudReclamacion.objects.select_related('usuario', 'objeto', 'objeto__categoria'),
        pk=pk,
    )
    return render(request, 'panel/solicitud_detalle.html', {
        'solicitud': solicitud,
    })


@staff_member_required
@require_POST
def panel_solicitud_decision(request, pk, accion):
    solicitud = get_object_or_404(SolicitudReclamacion, pk=pk)
    if solicitud.estado != SolicitudReclamacion.Estados.PENDIENTE:
        messages.warning(request, 'Esta solicitud ya fue respondida.')
    elif accion == 'aprobar':
        solicitud.aprobar(request.user)
        messages.success(
            request,
            f'Solicitud aprobada. El objeto pasó a «reclamado» y se vinculó '
            f'el perfil de {solicitud.usuario.get_full_name() or solicitud.usuario.username}.',
        )
    elif accion == 'rechazar':
        solicitud.rechazar(request.user)
        messages.info(request, 'La solicitud fue rechazada.')
    else:
        messages.error(request, 'Acción no válida.')
    return redirect('panel_solicitud_detalle', pk=solicitud.pk)


@staff_member_required
def panel_categorias(request):
    form = CategoriaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Categoría creada.')
        return redirect('panel_categorias')
    return render(request, 'panel/categorias.html', {
        'form': form,
        'categorias': Categoria.objects.annotate(total_objetos=Count('objetos')),
    })


@staff_member_required
def panel_categoria_editar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    form = CategoriaForm(request.POST or None, instance=categoria)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Categoría actualizada.')
        return redirect('panel_categorias')
    return render(request, 'panel/categoria_form.html', {'form': form, 'categoria': categoria})


@staff_member_required
@require_POST
def panel_categoria_eliminar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if categoria.objetos.exists():
        messages.error(request, 'No puedes eliminar una categoría que tiene objetos.')
    else:
        categoria.delete()
        messages.success(request, 'Categoría eliminada.')
    return redirect('panel_categorias')


@staff_member_required
def panel_usuarios(request):
    form = UsuarioPanelForm(request.POST or None, requiere_contrasena=True)
    if request.method == 'POST' and form.is_valid():
        datos = form.cleaned_data
        try:
            usuario = User.objects.create_user(
                username=datos['username'],
                email=datos['email'],
                password=datos['contrasena'],
                first_name=datos.get('first_name', ''),
                last_name=datos.get('last_name', ''),
            )
            usuario.is_staff = (datos['rol'] == 'admin')
            usuario.is_active = datos.get('is_active', True)
            usuario.save()
            perfil = usuario.perfil
            perfil.tipo_documento = datos.get('tipo_documento', '')
            perfil.numero_documento = datos.get('numero_documento', '').strip()
            perfil.telefono = datos.get('telefono', '').strip()
            perfil.programa = datos.get('programa', '').strip()
            perfil.save()
            messages.success(request, f'Cuenta de {usuario.username} creada.')
            return redirect('panel_usuarios')
        except IntegrityError:
            messages.error(request, 'Ya existe un usuario con ese nombre o correo.')

    q = request.GET.get('q', '').strip()
    rol = request.GET.get('rol', '')
    usuarios = User.objects.select_related('perfil').order_by('-is_staff', 'username')
    if rol == 'admin':
        usuarios = usuarios.filter(is_staff=True)
    elif rol == 'estudiante':
        usuarios = usuarios.filter(is_staff=False)
    if q:
        usuarios = usuarios.filter(
            Q(username__icontains=q)
            | Q(email__icontains=q)
            | Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
        )
    return render(request, 'panel/usuarios.html', {
        'form': form,
        'usuarios': usuarios,
        'q': q, 'rol': rol,
    })


@staff_member_required
def panel_usuario_editar(request, pk):
    usuario = get_object_or_404(User.objects.select_related('perfil'), pk=pk)
    if request.method == 'POST':
        form = UsuarioPanelForm(request.POST, requiere_contrasena=False)
        if form.is_valid():
            datos = form.cleaned_data
            try:
                usuario.username = datos['username']
                usuario.email = datos['email']
                usuario.first_name = datos.get('first_name', '')
                usuario.last_name = datos.get('last_name', '')
                usuario.is_staff = (datos['rol'] == 'admin')
                usuario.is_active = datos.get('is_active', False)
                if datos['contrasena']:
                    usuario.set_password(datos['contrasena'])
                if usuario.pk == request.user.pk and not usuario.is_active:
                    messages.error(request, 'No puedes desactivar tu propia cuenta.')
                    return redirect('panel_usuario_editar', pk=pk)
                usuario.save()
                perfil = usuario.perfil
                perfil.tipo_documento = datos.get('tipo_documento', '')
                perfil.numero_documento = datos.get('numero_documento', '').strip()
                perfil.telefono = datos.get('telefono', '').strip()
                perfil.programa = datos.get('programa', '').strip()
                perfil.save()
                messages.success(request, 'Cuenta actualizada.')
                return redirect('panel_usuarios')
            except IntegrityError:
                messages.error(request, 'Ya existe otro usuario con ese nombre o correo.')
        return render(request, 'panel/usuario_form.html', {
            'form': form, 'usuario': usuario, 'es_self': usuario.pk == request.user.pk,
        })

    perfil = getattr(usuario, 'perfil', None)
    form = UsuarioPanelForm(initial={
        'username': usuario.username,
        'email': usuario.email,
        'first_name': usuario.first_name,
        'last_name': usuario.last_name,
        'rol': 'admin' if usuario.is_staff else 'estudiante',
        'is_active': usuario.is_active,
        'tipo_documento': perfil.tipo_documento if perfil else '',
        'numero_documento': perfil.numero_documento if perfil else '',
        'telefono': perfil.telefono if perfil else '',
        'programa': perfil.programa if perfil else '',
    }, requiere_contrasena=False)
    return render(request, 'panel/usuario_form.html', {
        'form': form, 'usuario': usuario, 'es_self': usuario.pk == request.user.pk,
    })


@staff_member_required
def panel_exportar_csv(request):
    """Exporta los datos para su análisis en Excel o Power BI."""
    respuesta = HttpResponse(content_type='text/csv; charset=utf-8')
    respuesta['Content-Disposition'] = (
        f'attachment; filename="objetos_{timezone.now().strftime("%Y%m%d")}.csv"'
    )
    respuesta.write('\ufeff')  # BOM para que Excel/Power BI lean UTF-8

    escritor = csv.writer(respuesta)
    escritor.writerow([
        'id', 'fecha_registro', 'nombre_objeto', 'categoria', 'estado',
        'lugar_encontrado', 'descripcion', 'registrado_por', 'fecha_reclamo',
        'reclamado_por', 'nombre_persona', 'tipo_documento', 'numero_documento',
        'telefono', 'correo', 'suministro_correo', 'fecha_entrega',
        'responsable_entrega',
    ])
    for obj in ObjetoReclamado.objects.select_related('categoria').prefetch_related('solicitudes'):
        escritor.writerow([
            obj.id,
            obj.fecha_registro.isoformat() if obj.fecha_registro else '',
            obj.nombre_objeto,
            obj.etiqueta_categoria,
            obj.get_estado_display(),
            obj.lugar_encontrado,
            obj.descripcion_objeto,
            obj.registrado_por.username if obj.registrado_por else '',
            obj.fecha_reclamo.strftime('%Y-%m-%d %H:%M') if obj.fecha_reclamo else '',
            obj.reclamado_por.username if obj.reclamado_por else '',
            obj.nombre_persona,
            obj.tipo_documento,
            obj.numero_documento,
            obj.telefono,
            obj.correo or '',
            'Sí' if obj.suministro_correo else 'No',
            obj.fecha_entrega,
            obj.responsable_entrega,
        ])
    return respuesta