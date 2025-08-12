from django import forms
from .models import ObjetoReclamado

class ObjetoReclamadoForm(forms.ModelForm):
    class Meta:
        model = ObjetoReclamado
        fields = [
            'nombre_persona',
            'tipo_documento',
            'numero_documento',
            'tipo_objeto',
            'descripcion_objeto',
            'fecha_entrega',
            'telefono',
            'suministro_correo',
            'correo',
            'responsable_entrega'
        ]
        widgets = {
            'fecha_entrega': forms.DateInput(attrs={'type': 'date'}),
        }
