import os

from django import forms
from django.conf import settings
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone

from .iconos import OPCIONES_ICONO
from .models import Categoria, InstruccionesEntrega, ObjetoReclamado, PerfilUsuario

MAX_IMAGEN_MB = 5


def dominio_permitido(correo):
    """Valida que el correo pertenezca a un dominio institucional autorizado."""
    if not correo or '@' not in correo:
        return False
    dominio = correo.rsplit('@', 1)[1].strip().lower()
    return dominio in settings.ALLOWED_EMAIL_DOMAINS


def validar_imagen(archivo):
    """Rechaza archivos que no sean imágenes o que superen el tamaño máximo."""
    if archivo is None:
        return
    nombre = (archivo.name or '').lower()
    if not nombre.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
        raise ValidationError('Solo se permiten imágenes (JPG, PNG, GIF o WEBP).')
    if archivo.size and archivo.size > MAX_IMAGEN_MB * 1024 * 1024:
        raise ValidationError(f'La imagen no puede superar los {MAX_IMAGEN_MB} MB.')


class ObjetoReclamadoForm(forms.ModelForm):
    """Formulario para registrar o editar un objeto en el panel del administrador."""

    class Meta:
        model = ObjetoReclamado
        fields = [
            'nombre_objeto', 'categoria', 'descripcion_objeto',
            'sede', 'lugar_encontrado', 'foto', 'estado', 'fecha_registro',
            'nombre_persona', 'tipo_documento', 'numero_documento',
            'telefono', 'suministro_correo', 'correo',
            'fecha_entrega', 'responsable_entrega',
        ]
        widgets = {
            'descripcion_objeto': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe el objeto: color, marca, señas particulares…'}),
            'nombre_objeto': forms.TextInput(attrs={'placeholder': 'Ej. Termo negro 500 ml'}),
            'lugar_encontrado': forms.TextInput(attrs={'placeholder': 'Ej. Biblioteca, bloque 2, cafetería…'}),
            'foto': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            'fecha_registro': forms.DateInput(
                attrs={'type': 'text', 'autocomplete': 'off'},
                format='%Y-%m-%d',
            ),
            'tipo_documento': forms.Select(
                choices=[('', 'Tipo de documento')] + ObjetoReclamado.TiposDocumento.choices,
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categoria'].empty_label = 'Selecciona una categoría'
        self.fields['categoria'].required = True
        for campo in self.fields:
            self.fields[campo].widget.attrs.setdefault('class', '')
        if not self.instance.pk and not self.is_bound:
            self.fields['fecha_registro'].initial = timezone.localdate()

    def clean_foto(self):
        foto = self.cleaned_data.get('foto')
        validar_imagen(foto)
        return foto

    def _requiere_datos_reclamo(self):
        estado = self.cleaned_data.get('estado')
        return estado in (ObjetoReclamado.Estados.RECLAMADO, ObjetoReclamado.Estados.ENTREGADO)

    def clean(self):
        cleaned = super().clean()
        if self._requiere_datos_reclamo():
            if not cleaned.get('nombre_persona'):
                self.add_error('nombre_persona', 'Debes registrar quién reclama el objeto.')
            if not cleaned.get('telefono'):
                self.add_error('telefono', 'Debes registrar un teléfono de contacto.')
        else:
            # Los datos del reclamante solo aplican a objetos reclamados/entregados
            for campo in ['nombre_persona', 'tipo_documento', 'numero_documento',
                          'telefono', 'correo', 'fecha_entrega', 'responsable_entrega']:
                if campo in cleaned:
                    cleaned[campo] = cleaned[campo] or ''
            cleaned['suministro_correo'] = bool(cleaned.get('suministro_correo'))
        return cleaned

    def _mime_de(self, nombre):
        nombre = (nombre or '').lower()
        if nombre.endswith('.png'):
            return 'image/png'
        if nombre.endswith('.gif'):
            return 'image/gif'
        if nombre.endswith('.webp'):
            return 'image/webp'
        return 'image/jpeg'

    def save(self, commit=True):
        foto = self.cleaned_data.get('foto')
        if foto:
            import base64 as _base64
            import io
            from PIL import Image
            contenido = foto.read()
            mime = 'image/jpeg'
            try:
                img = Image.open(io.BytesIO(contenido))
                img = img.convert('RGB')
                if img.width > 900:
                    h = round(img.height * 900 / img.width)
                    img = img.resize((900, h), Image.LANCZOS)
                buf = io.BytesIO()
                img.save(buf, 'JPEG', quality=78, optimize=True)
                datos = buf.getvalue()
            except Exception:
                datos = contenido
            self.instance.foto_base64 = 'data:%s;base64,%s' % (mime, _base64.b64encode(datos).decode('ascii'))
            self.instance.foto = None
            self.cleaned_data['foto'] = None
        return super().save(commit)


class RegistroUsuarioForm(forms.Form):
    """Registro de estudiantes con correo institucional obligatorio."""
    email = forms.EmailField(
        label='Correo institucional',
        widget=forms.EmailInput(attrs={'placeholder': 'tu.correo@unal.edu.co', 'autocomplete': 'email'}),
    )
    primera_contrasena = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    segunda_contrasena = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    first_name = forms.CharField(label='Nombres', max_length=150,
                                 widget=forms.TextInput(attrs={'autocomplete': 'given-name'}))
    last_name = forms.CharField(label='Apellidos', max_length=150,
                                widget=forms.TextInput(attrs={'autocomplete': 'family-name'}))
    tipo_documento = forms.ChoiceField(label='Tipo de documento', choices=PerfilUsuario.TiposDocumento.choices)
    numero_documento = forms.CharField(label='Número de documento', max_length=50)
    telefono = forms.CharField(label='Teléfono', max_length=20)
    programa = forms.CharField(label='Programa / Carrera', max_length=120, required=False)

    def clean_email(self):
        correo = self.cleaned_data['email'].strip().lower()
        if not dominio_permitido(correo):
            dominios = ', '.join(settings.ALLOWED_EMAIL_DOMAINS)
            raise ValidationError(
                f'Debes usar un correo institucional autorizado ({dominios}).'
            )
        if User.objects.filter(email=correo).exists():
            raise ValidationError('Ya existe una cuenta con este correo.')
        return correo

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('primera_contrasena')
        p2 = cleaned.get('segunda_contrasena')
        if p1 and p2 and p1 != p2:
            self.add_error('segunda_contrasena', 'Las contraseñas no coinciden.')
        if p1:
            validate_password(p1, self.cleaned_data.get('email') or None)
        return cleaned


class InicioSesionForm(forms.Form):
    """Login flexible: acepta correo institucional o nombre de usuario."""
    identificador = forms.CharField(
        label='Usuario o correo institucional',
        widget=forms.TextInput(attrs={'placeholder': 'correo@unal.edu.co', 'autocomplete': 'username'}),
    )
    contrasena = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )


class SolicitudForm(forms.Form):
    mensaje = forms.CharField(
        label='¿Por qué crees que es tuyo? (opcional)',
        required=False,
        max_length=500,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ej. Es azul, tiene un sticker de… y lo perdí el lunes en la cafetería.'}),
    )
    tipo_documento = forms.ChoiceField(
        label='Tipo de documento',
        choices=PerfilUsuario.TiposDocumento.choices,
        widget=forms.Select,
        error_messages={'required': 'Selecciona tu tipo de documento.'},
    )
    numero_documento = forms.CharField(
        label='Número de documento',
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Ej. 1036645213', 'autocomplete': 'off'}),
        error_messages={'required': 'Escribe tu número de documento. Sin este dato no podemos emitir el formato de entrega.'},
    )
    telefono = forms.CharField(
        label='Teléfono de contacto',
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': 'Ej. 300 123 4567'}),
        error_messages={'required': 'Escribe tu teléfono de contacto.'},
    )


class ApelacionForm(forms.Form):
    """Motivo del estudiante al apelar una solicitud rechazada."""
    motivo = forms.CharField(
        label='¿Por qué no estás de acuerdo con la decisión?',
        max_length=500,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Explica por qué crees que el objeto sí es tuyo o por qué la respuesta no es correcta…',
        }),
    )


class InstruccionesEntregaForm(forms.ModelForm):
    class Meta:
        model = InstruccionesEntrega
        fields = ['texto_minas', 'texto_volador']
        widgets = {
            'texto_minas': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Ej. Reclama tu objeto en Bienestar de la Sede '
                               'Minas, edificio 2, piso 1, entre 8:00 a.m. y '
                               '5:00 p.m. Lleva tu documento de identidad.',
            }),
            'texto_volador': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Ej. Reclama tu objeto en la portería principal '
                               'de la Sede El Volador, entre 8:00 a.m. y '
                               '6:00 p.m. Lleva tu documento de identidad.',
            }),
        }


class CategoriaForm(forms.ModelForm):
    orden = forms.IntegerField(label='Orden', required=False)

    class Meta:
        model = Categoria
        fields = ['nombre', 'icono', 'color', 'orden']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
            'icono': forms.Select(
                choices=[('', 'Genérico')] + OPCIONES_ICONO,
            ),
        }

    def clean_nombre(self):
        nombre = (self.cleaned_data.get('nombre') or '').strip()
        if not nombre:
            raise forms.ValidationError('Escribe un nombre para la categoría.')
        return nombre

    def clean_orden(self):
        return self.cleaned_data.get('orden') or 0


class UsuarioPanelForm(forms.Form):
    """Creación y edición de cuentas desde el panel del administrador."""

    def __init__(self, *args, **kwargs):
        self.requiere_contrasena = kwargs.pop('requiere_contrasena', False)
        super().__init__(*args, **kwargs)

    username = forms.CharField(label='Usuario', max_length=150,
                               widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    email = forms.EmailField(label='Correo institucional')
    first_name = forms.CharField(label='Nombres', max_length=150, required=False)
    last_name = forms.CharField(label='Apellidos', max_length=150, required=False)
    rol = forms.ChoiceField(label='Rol', choices=[('estudiante', 'Estudiante'), ('admin', 'Administrador')])
    is_active = forms.BooleanField(label='Cuenta activa', required=False, initial=True)
    contrasena = forms.CharField(
        label='Contraseña (dejar vacía para no cambiarla)', max_length=128,
        required=False, widget=forms.PasswordInput(render_value=False),
    )
    tipo_documento = forms.ChoiceField(label='Tipo de documento', required=False,
                                       choices=PerfilUsuario.TiposDocumento.choices)
    numero_documento = forms.CharField(label='Número de documento', max_length=50, required=False)
    telefono = forms.CharField(label='Teléfono', max_length=20, required=False)
    programa = forms.CharField(label='Programa / Carrera', max_length=120, required=False)
    firma = forms.ImageField(
        label='Firma digital (solo administradores)· PNG con fondo transparente',
        required=False,
        help_text='Se estampa en los formatos de entrega para impresión. '
                  'Déjalo vacío para conservar la firma actual.',
    )

    def clean_email(self):
        correo = self.cleaned_data['email'].strip().lower()
        # Los administradores pueden usar cualquier correo; los estudiantes,
        # solo el institucional.
        if self.cleaned_data.get('rol', 'estudiante') == 'estudiante' and not dominio_permitido(correo):
            dominios = ', '.join(settings.ALLOWED_EMAIL_DOMAINS)
            raise ValidationError(f'Debe ser un correo institucional autorizado ({dominios}).')
        return correo

    def clean_username(self):
        nombre = self.cleaned_data['username'].strip()
        return nombre

    def clean_contrasena(self):
        contrasena = self.cleaned_data.get('contrasena')
        if self.requiere_contrasena and not contrasena:
            raise ValidationError('Debes asignar una contraseña al crear la cuenta.')
        if contrasena:
            validate_password(contrasena)
        return contrasena