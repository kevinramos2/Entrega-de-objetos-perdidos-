"""Pruebas de la API REST (/api/v1/). Cubren los mismos escenarios clave que
``tests.py`` cubre para las vistas HTML, pero contra los nuevos endpoints
JSON, para asegurar que la migración no cambió ninguna regla de negocio."""
from django.contrib.auth.models import User
from django.core import mail
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Categoria, ObjetoReclamado, SolicitudReclamacion


def crear_usuario(username, email, is_staff=False):
    u = User.objects.create_user(username=username, email=email, password='clave12345')
    u.first_name = username.title()
    u.is_staff = is_staff
    u.save(update_fields=['first_name', 'is_staff'])
    return u


SOLICITUD_DATOS = {
    'mensaje': 'Es mío, lo perdí en la cafetería.',
    'tipo_documento': 'CC',
    'numero_documento': '1036645213',
    'telefono': '3001234567',
}


class AutenticacionApiTest(APITestCase):
    def setUp(self):
        # El limitador de intentos vive en el cache de Django, que no se
        # limpia solo entre pruebas (no es parte de la transacción de BD).
        cache.clear()
        self.usuario = crear_usuario('carla', 'carla@unal.edu.co')

    def test_login_correcto_devuelve_access_y_cookie_de_refresh(self):
        respuesta = self.client.post(reverse('api_login'), {
            'identificador': 'carla', 'contrasena': 'clave12345',
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn('access', respuesta.data)
        self.assertEqual(respuesta.data['usuario']['username'], 'carla')
        self.assertIn('refresh_token', respuesta.cookies)
        self.assertTrue(respuesta.cookies['refresh_token']['httponly'])

    def test_login_con_correo_institucional_funciona(self):
        respuesta = self.client.post(reverse('api_login'), {
            'identificador': 'carla@unal.edu.co', 'contrasena': 'clave12345',
        })
        self.assertEqual(respuesta.status_code, 200)

    def test_login_incorrecto_rechaza(self):
        respuesta = self.client.post(reverse('api_login'), {
            'identificador': 'carla', 'contrasena': 'clave-equivocada',
        })
        self.assertEqual(respuesta.status_code, 401)

    def test_bloqueo_tras_varios_intentos_fallidos(self):
        for _ in range(5):
            self.client.post(reverse('api_login'), {
                'identificador': 'carla', 'contrasena': 'mala',
            })
        respuesta = self.client.post(reverse('api_login'), {
            'identificador': 'carla', 'contrasena': 'clave12345',
        })
        self.assertEqual(respuesta.status_code, 429)

    def test_refrescar_access_con_la_cookie(self):
        login = self.client.post(reverse('api_login'), {
            'identificador': 'carla', 'contrasena': 'clave12345',
        })
        self.client.cookies['refresh_token'] = login.cookies['refresh_token'].value
        respuesta = self.client.post(reverse('api_refresh'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn('access', respuesta.data)

    def test_refrescar_sin_cookie_falla(self):
        respuesta = self.client.post(reverse('api_refresh'))
        self.assertEqual(respuesta.status_code, 401)

    def test_me_requiere_autenticacion(self):
        respuesta = self.client.get(reverse('api_me'))
        self.assertEqual(respuesta.status_code, 401)


class FlujoSolicitudApiTest(APITestCase):
    def setUp(self):
        self.estudiante = crear_usuario('santiago', 'santiago@unal.edu.co')
        self.admin = crear_usuario('adminflujo', 'adminflujo@unal.edu.co', is_staff=True)
        self.categoria = Categoria.objects.create(nombre='Termos', color='#123456')
        self.objeto = ObjetoReclamado.objects.create(
            nombre_objeto='Termo negro', categoria=self.categoria,
            descripcion_objeto='Negro, 500 ml.', estado=ObjetoReclamado.Estados.DISPONIBLE,
        )

    def test_estudiante_no_accede_al_panel(self):
        self.client.force_authenticate(self.estudiante)
        respuesta = self.client.get(reverse('api_panel_objetos'))
        self.assertEqual(respuesta.status_code, 403)

    def test_resumen_es_publico(self):
        respuesta = self.client.get(reverse('api_resumen'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn('resumen', respuesta.data)

    def test_listar_objetos_disponibles(self):
        self.client.force_authenticate(self.estudiante)
        respuesta = self.client.get(reverse('api_objetos'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(respuesta.data), 1)
        self.assertEqual(respuesta.data[0]['nombre_objeto'], 'Termo negro')
        # Sin datos del reclamante en el listado público.
        self.assertNotIn('numero_documento', respuesta.data[0])

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_flujo_completo_solicitud_rechazo_apelacion_aprobacion(self):
        self.client.force_authenticate(self.estudiante)
        respuesta = self.client.post(
            reverse('api_solicitar', args=[self.objeto.pk]), SOLICITUD_DATOS,
        )
        self.assertEqual(respuesta.status_code, 201)
        solicitud = SolicitudReclamacion.objects.get(usuario=self.estudiante)
        self.assertEqual(solicitud.estado, SolicitudReclamacion.Estados.PENDIENTE)

        # Segunda solicitud sobre el mismo objeto: rechazada por duplicada.
        respuesta = self.client.post(
            reverse('api_solicitar', args=[self.objeto.pk]), SOLICITUD_DATOS,
        )
        self.assertEqual(respuesta.status_code, 409)

        self.client.force_authenticate(self.admin)
        respuesta = self.client.post(
            reverse('api_panel_solicitud_decidir', args=[solicitud.pk]),
            {'accion': 'rechazar', 'comentario': 'No coincide con el reporte.'},
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        solicitud.refresh_from_db()
        self.assertEqual(solicitud.estado, SolicitudReclamacion.Estados.RECHAZADA)

        self.client.force_authenticate(self.estudiante)
        respuesta = self.client.post(
            reverse('api_apelar', args=[solicitud.pk]),
            {'motivo': 'El objeto sí era mío, tengo fotos.'},
        )
        self.assertEqual(respuesta.status_code, 200)
        solicitud.refresh_from_db()
        self.assertEqual(solicitud.estado, SolicitudReclamacion.Estados.APELADA)

        self.client.force_authenticate(self.admin)
        respuesta = self.client.post(
            reverse('api_panel_solicitud_decidir', args=[solicitud.pk]),
            {'accion': 'aprobar', 'comentario': 'Verificado.'},
        )
        self.assertEqual(respuesta.status_code, 200)
        solicitud.refresh_from_db()
        self.objeto.refresh_from_db()
        self.assertEqual(solicitud.estado, SolicitudReclamacion.Estados.APROBADA)
        self.assertEqual(self.objeto.estado, ObjetoReclamado.Estados.RECLAMADO)

        # El PDF solo está disponible tras marcar la entrega.
        respuesta = self.client.get(reverse('api_panel_solicitud_formato', args=[solicitud.pk]))
        self.assertEqual(respuesta.status_code, 409)

        respuesta = self.client.post(reverse('api_panel_solicitud_entregar', args=[solicitud.pk]))
        self.assertEqual(respuesta.status_code, 200)

        respuesta = self.client.get(reverse('api_panel_solicitud_formato', args=[solicitud.pk]))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta['Content-Type'], 'application/pdf')


class PanelObjetosApiTest(APITestCase):
    def setUp(self):
        self.admin = crear_usuario('adminobj', 'adminobj@unal.edu.co', is_staff=True)
        self.categoria = Categoria.objects.create(nombre='Mochilas de prueba', color='#123456')
        self.client.force_authenticate(self.admin)

    def test_crear_objeto(self):
        respuesta = self.client.post(reverse('api_panel_objetos'), {
            'nombre_objeto': 'Cargador blanco', 'categoria': self.categoria.pk,
            'descripcion_objeto': '', 'sede': 'minas', 'lugar_encontrado': 'Biblioteca',
            'estado': 'disponible', 'fecha_registro': '',
        })
        self.assertEqual(respuesta.status_code, 201, respuesta.data)
        self.assertTrue(ObjetoReclamado.objects.filter(nombre_objeto='Cargador blanco').exists())

    def test_exportar_csv(self):
        respuesta = self.client.get(reverse('api_panel_exportar_csv'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta['Content-Type'], 'text/csv; charset=utf-8')

    def test_categorias_duplicadas_se_rechazan(self):
        respuesta = self.client.post(
            reverse('api_panel_categorias'), {'nombre': 'Mochilas de prueba', 'color': '#000000'},
        )
        self.assertEqual(respuesta.status_code, 400)
