"""Configuración de URLs del proyecto objetos_reclamados."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    # Autenticación social (login con Google / correo institucional)
    path('accounts/', include('allauth.urls')),
    # Aplicación principal
    path('', include('registro_objetos.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)