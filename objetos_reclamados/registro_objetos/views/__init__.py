"""Vistas de la aplicación, agrupadas por responsabilidad:

- publico: inicio y autenticación.
- estudiante: búsqueda, detalle, solicitudes y apelaciones.
- panel_dashboard: indicadores y gráficas del panel.
- panel_objetos: CRUD de objetos y su formato de entrega.
- panel_solicitudes: revisión de solicitudes y su formato de entrega.
- panel_configuracion: instrucciones de entrega por sede y categorías.
- panel_usuarios: gestión de cuentas.
- exportar: exportación de datos a CSV.
- errores: páginas de error.

Se reexportan todos los nombres aquí para que ``urls.py`` siga usando
``from . import views`` y ``views.<nombre_de_vista>`` sin cambios.
"""
from .errores import error_500
from .estudiante import (
    apelar_solicitud,
    detalle_objeto,
    lista_objetos,
    mis_solicitudes,
    servir_foto_objeto,
    solicitar_reclamacion,
)
from .exportar import panel_exportar_csv
from .panel_configuracion import (
    panel_categoria_editar,
    panel_categoria_eliminar,
    panel_categorias,
    panel_configuracion_entrega,
)
from .panel_dashboard import panel_inicio
from .panel_objetos import (
    panel_objeto_editar,
    panel_objeto_eliminar,
    panel_objeto_estado,
    panel_objeto_formato,
    panel_objeto_nuevo,
    panel_objetos,
    panel_objetos_eliminar_seleccion,
)
from .panel_solicitudes import (
    panel_solicitud_decision,
    panel_solicitud_detalle,
    panel_solicitud_entregar,
    panel_solicitud_formato,
    panel_solicitudes,
)
from .panel_usuarios import panel_usuario_editar, panel_usuarios
from .publico import cerrar_sesion, inicio, iniciar_sesion, registro_usuario

__all__ = [
    'apelar_solicitud',
    'cerrar_sesion',
    'detalle_objeto',
    'error_500',
    'inicio',
    'iniciar_sesion',
    'lista_objetos',
    'mis_solicitudes',
    'panel_categoria_editar',
    'panel_categoria_eliminar',
    'panel_categorias',
    'panel_configuracion_entrega',
    'panel_exportar_csv',
    'panel_inicio',
    'panel_objeto_editar',
    'panel_objeto_eliminar',
    'panel_objeto_estado',
    'panel_objeto_formato',
    'panel_objeto_nuevo',
    'panel_objetos',
    'panel_objetos_eliminar_seleccion',
    'panel_solicitud_decision',
    'panel_solicitud_detalle',
    'panel_solicitud_entregar',
    'panel_solicitud_formato',
    'panel_solicitudes',
    'panel_usuario_editar',
    'panel_usuarios',
    'registro_usuario',
    'servir_foto_objeto',
    'solicitar_reclamacion',
]
