from django.urls import path

from . import auth_views, views_estudiante, views_panel

urlpatterns = [
    # Autenticación
    path('auth/login/', auth_views.LoginView.as_view(), name='api_login'),
    path('auth/refresh/', auth_views.RefreshView.as_view(), name='api_refresh'),
    path('auth/logout/', auth_views.LogoutView.as_view(), name='api_logout'),
    path('auth/me/', auth_views.MeView.as_view(), name='api_me'),
    path('auth/google/bridge/', auth_views.google_auth_bridge, name='api_google_bridge'),

    # Estudiante
    path('resumen/', views_estudiante.ResumenView.as_view(), name='api_resumen'),
    path('categorias/', views_estudiante.CategoriasView.as_view(), name='api_categorias'),
    path('objetos/', views_estudiante.ObjetosDisponiblesView.as_view(), name='api_objetos'),
    path('objetos/<int:pk>/', views_estudiante.ObjetoDetalleView.as_view(), name='api_objeto_detalle'),
    path('objetos/<int:pk>/solicitar/', views_estudiante.SolicitarReclamacionView.as_view(), name='api_solicitar'),
    path('mis-solicitudes/', views_estudiante.MisSolicitudesView.as_view(), name='api_mis_solicitudes'),
    path('solicitudes/<int:pk>/apelar/', views_estudiante.ApelarSolicitudView.as_view(), name='api_apelar'),

    # Panel del administrador
    path('panel/dashboard/', views_panel.PanelDashboardView.as_view(), name='api_panel_dashboard'),
    path('panel/objetos/', views_panel.PanelObjetosView.as_view(), name='api_panel_objetos'),
    path('panel/objetos/eliminar-seleccion/', views_panel.PanelObjetosEliminarSeleccionView.as_view(), name='api_panel_objetos_eliminar_seleccion'),
    path('panel/objetos/<int:pk>/', views_panel.PanelObjetoDetalleView.as_view(), name='api_panel_objeto_detalle'),
    path('panel/objetos/<int:pk>/estado/', views_panel.PanelObjetoEstadoView.as_view(), name='api_panel_objeto_estado'),
    path('panel/objetos/<int:pk>/formato/', views_panel.PanelObjetoFormatoView.as_view(), name='api_panel_objeto_formato'),
    path('panel/solicitudes/', views_panel.PanelSolicitudesView.as_view(), name='api_panel_solicitudes'),
    path('panel/solicitudes/<int:pk>/', views_panel.PanelSolicitudDetalleView.as_view(), name='api_panel_solicitud_detalle'),
    path('panel/solicitudes/<int:pk>/decidir/', views_panel.PanelSolicitudDecisionView.as_view(), name='api_panel_solicitud_decidir'),
    path('panel/solicitudes/<int:pk>/formato/', views_panel.PanelSolicitudFormatoView.as_view(), name='api_panel_solicitud_formato'),
    path('panel/solicitudes/<int:pk>/entregar/', views_panel.PanelSolicitudEntregarView.as_view(), name='api_panel_solicitud_entregar'),
    path('panel/configuracion-entrega/', views_panel.PanelConfiguracionEntregaView.as_view(), name='api_panel_configuracion_entrega'),
    path('panel/categorias/', views_panel.PanelCategoriasView.as_view(), name='api_panel_categorias'),
    path('panel/categorias/<int:pk>/', views_panel.PanelCategoriaDetalleView.as_view(), name='api_panel_categoria_detalle'),
    path('panel/usuarios/', views_panel.PanelUsuariosView.as_view(), name='api_panel_usuarios'),
    path('panel/usuarios/<int:pk>/', views_panel.PanelUsuarioDetalleView.as_view(), name='api_panel_usuario_detalle'),
    path('panel/exportar-csv/', views_panel.PanelExportarCsvView.as_view(), name='api_panel_exportar_csv'),
]
