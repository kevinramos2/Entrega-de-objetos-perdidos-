"""Panel del administrador: gestión de cuentas (crear/editar/activar/desactivar)."""
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import UsuarioPanelForm


@staff_member_required
def panel_usuarios(request):
    form = UsuarioPanelForm(request.POST or None, request.FILES or None, requiere_contrasena=True)
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
            if datos.get('firma'):
                perfil.firma = datos['firma']
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
        form = UsuarioPanelForm(request.POST, request.FILES, requiere_contrasena=False)
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
                if datos.get('firma'):
                    perfil.firma = datos['firma']
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
