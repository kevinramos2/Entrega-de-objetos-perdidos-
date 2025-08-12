from django.db import models

# Create your models here.
class ObjetoReclamado(models.Model):
  nombre_persona = models.CharField(max_length=100)
  tipo_documento = models.CharField(max_length=50)
  numero_documento = models.CharField(max_length=50)
  tipo_objeto = models.CharField(max_length=50)
  descripcion_objeto = models.TextField()
  fecha_entrega = models.CharField()
  telefono = models.CharField(max_length=20)
  suministro_correo = models.BooleanField(default=False)
  correo = models.EmailField(blank=True, null=True)
  responsable_entrega = models.CharField(max_length=100)

  def __str__(self):
    return f"{self.nombre_persona} - {self.tipo_objeto}"
  
  