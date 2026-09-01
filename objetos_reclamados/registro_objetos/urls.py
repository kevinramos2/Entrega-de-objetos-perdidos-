from django.urls import path

from . import views

handler500 = 'registro_objetos.views.error_500'

urlpatterns = [
    # Público / autenticación
    path('', views.inicio, name='inicio'),
    path('registro/', views.registro_usuario, name='registro'),
    path('login/', views.iniciar_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),

    # Estudiante
    path('objetos/', views.lista_objetos, name='lista_objetos'),
    path('objetos/<int:pk>/', views.detalle_objeto, name='detalle_objeto'),
    path('objetos/<int:pk>/solicitar/', views.solicitar_reclamacion, name='solicitar_reclamacion'),
    path('mis-solicitudes/', views.mis_solicitudes, name='mis_solicitudes'),
    path('solicitudes/<int:pk>/apelar/', views.apelar_solicitud, name='apelar_solicitud'),

    # Panel del administrador
    path('panel/', views.panel_inicio, name='panel_inicio'),
    path('panel/objetos/', views.panel_objetos, name='panel_objetos'),
    path('panel/objetos/nuevo/', views.panel_objeto_nuevo, name='panel_objeto_nuevo'),
    path('panel/objetos/eliminar-seleccion/', views.panel_objetos_eliminar_seleccion, name='panel_objetos_eliminar_seleccion'),
    path('panel/objetos/<int:pk>/editar/', views.panel_objeto_editar, name='panel_objeto_editar'),
    path('panel/objetos/<int:pk>/eliminar/', views.panel_objeto_eliminar, name='panel_objeto_eliminar'),
    path('panel/objetos/<int:pk>/estado/', views.panel_objeto_estado, name='panel_objeto_estado'),
    path('panel/solicitudes/', views.panel_solicitudes, name='panel_solicitudes'),
    path('panel/solicitudes/<int:pk>/', views.panel_solicitud_detalle, name='panel_solicitud_detalle'),
    path('panel/solicitudes/<int:pk>/decidir/', views.panel_solicitud_decision, name='panel_solicitud_decidir'),
    path('panel/solicitudes/<int:pk>/formato/', views.panel_solicitud_formato, name='panel_solicitud_formato'),
    path('panel/solicitudes/<int:pk>/entregar/', views.panel_solicitud_entregar, name='panel_solicitud_entregar'),
    path('panel/solicitudes/<int:pk>/<str:accion>/', views.panel_solicitud_decision, name='panel_solicitud_decision'),
    path('panel/configuracion-entrega/', views.panel_configuracion_entrega, name='panel_configuracion_entrega'),
    path('panel/categorias/', views.panel_categorias, name='panel_categorias'),
    path('panel/categorias/<int:pk>/', views.panel_categoria_editar, name='panel_categoria_editar'),
    path('panel/categorias/<int:pk>/eliminar/', views.panel_categoria_eliminar, name='panel_categoria_eliminar'),
    path('panel/usuarios/', views.panel_usuarios, name='panel_usuarios'),
    path('panel/usuarios/<int:pk>/', views.panel_usuario_editar, name='panel_usuario_editar'),
    path('panel/exportar-csv/', views.panel_exportar_csv, name='panel_exportar_csv'),
]