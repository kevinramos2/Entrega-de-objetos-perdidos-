import io
from PIL import Image
from django.contrib.auth.models import User
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import (
    Categoria,
    InstruccionesEntrega,
    ObjetoReclamado,
    SolicitudReclamacion,
    obtener_instrucciones_entrega,
)


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


class FlujoSolicitudApelacionTest(TestCase):
    def setUp(self):
        self.estudiante = crear_usuario('santiago', 'santiago@unal.edu.co')
        self.admin = crear_usuario('adminflujo', 'adminflujo@unal.edu.co', is_staff=True)
        self.categoria = Categoria.objects.create(nombre='Termos', color='#123456')
        self.objeto = ObjetoReclamado.objects.create(
            nombre_objeto='Termo negro',
            categoria=self.categoria,
            descripcion_objeto='Negro, 500 ml.',
            estado=ObjetoReclamado.Estados.DISPONIBLE,
        )

    def _solicitar(self):
        self.client.force_login(self.estudiante)
        return self.client.post(
            reverse('solicitar_reclamacion', args=[self.objeto.pk]),
            SOLICITUD_DATOS,
        )

    def _rechazar(self, comentario='No coincide con el reporte.'):
        self.client.force_login(self.admin)
        return self.client.post(
            reverse('panel_solicitud_decidir', args=[self.solicitud.pk]),
            {'accion': 'rechazar', 'comentario': comentario},
        )

    def test_flujo_completo_apelacion(self):
        self._solicitar()
        self.solicitud = SolicitudReclamacion.objects.get(usuario=self.estudiante)
        self.assertEqual(self.solicitud.estado, SolicitudReclamacion.Estados.PENDIENTE)

        # Rechazo con comentario
        self._rechazar()
        self.solicitud.refresh_from_db()
        self.assertEqual(self.solicitud.estado, SolicitudReclamacion.Estados.RECHAZADA)
        self.assertEqual(self.solicitud.comentario_admin, 'No coincide con el reporte.')
        self.objeto.refresh_from_db()
        self.assertTrue(self.objeto.esta_disponible)

        # Apelación del estudiante
        self.client.force_login(self.estudiante)
        self.client.post(
            reverse('apelar_solicitud', args=[self.solicitud.pk]),
            {'motivo': 'El objeto sí era mío, tengo fotos de cuando lo perdí.'},
        )
        self.solicitud.refresh_from_db()
        self.assertEqual(self.solicitud.estado, SolicitudReclamacion.Estados.APELADA)
        self.assertTrue(self.solicitud.fue_apelada)
        self.assertTrue(self.solicitud.apelacion)

        # No puede apelar una segunda vez
        self.client.post(
            reverse('apelar_solicitud', args=[self.solicitud.pk]),
            {'motivo': 'Otro intento.'},
        )
        self.solicitud.refresh_from_db()
        self.assertEqual(self.solicitud.estado, SolicitudReclamacion.Estados.APELADA)
        self.assertEqual(self.solicitud.apelacion, 'El objeto sí era mío, tengo fotos de cuando lo perdí.')

        # El admin aprueba la apelación
        self._rechazar = None
        self.client.force_login(self.admin)
        self.client.post(
            reverse('panel_solicitud_decidir', args=[self.solicitud.pk]),
            {'accion': 'aprobar', 'comentario': 'Verificamos y sí coincide. Pasa a recogerlo.'},
        )
        self.solicitud.refresh_from_db()
        self.assertEqual(self.solicitud.estado, SolicitudReclamacion.Estados.APROBADA)
        self.objeto.refresh_from_db()
        self.assertEqual(self.objeto.estado, ObjetoReclamado.Estados.RECLAMADO)
        self.assertEqual(self.objeto.reclamado_por, self.estudiante)

    def test_solo_el_dueno_puede_apelar(self):
        otro = crear_usuario('maria', 'maria@unal.edu.co')
        self._solicitar()
        self.solicitud = SolicitudReclamacion.objects.get(usuario=self.estudiante)
        self._rechazar()
        self.client.force_login(otro)
        respuesta = self.client.post(
            reverse('apelar_solicitud', args=[self.solicitud.pk]),
            {'motivo': 'Inválido.'},
        )
        self.assertEqual(respuesta.status_code, 404)
        self.solicitud.refresh_from_db()
        self.assertEqual(self.solicitud.estado, SolicitudReclamacion.Estados.RECHAZADA)

    def test_solicitud_requiere_documento_y_telefono(self):
        self.client.force_login(self.estudiante)
        self.client.post(
            reverse('solicitar_reclamacion', args=[self.objeto.pk]),
            {'mensaje': 'Es mío, sin datos.'},
        )
        self.assertFalse(
            SolicitudReclamacion.objects.filter(usuario=self.estudiante).exists()
        )

    def test_contador_de_respuesta_nueva_en_mis_reclamos(self):
        self._solicitar()
        self.solicitud = SolicitudReclamacion.objects.get(usuario=self.estudiante)
        self._rechazar(comentario='Revisamos y no coincide.')
        self.solicitud.refresh_from_db()
        self.assertFalse(self.solicitud.respuesta_vista)

        # La pestaña "Mis reclamos" (a través de la lista) muestra la señal.
        self.client.force_login(self.estudiante)
        respuesta = self.client.get(reverse('lista_objetos'))
        self.assertContains(respuesta, 'contador')
        self.assertContains(respuesta, '>1<')

        # Al visitar "Mis reclamos" la respuesta se marca como vista.
        self.client.get(reverse('mis_solicitudes'))
        self.solicitud.refresh_from_db()
        self.assertTrue(self.solicitud.respuesta_vista)
        respuesta = self.client.get(reverse('lista_objetos'))
        self.assertNotContains(respuesta, 'contador')


class InstruccionesEntregaTest(TestCase):
    def test_mis_solicitudes_muestra_donde_reclamar_al_aprobar(self):
        estudiante = crear_usuario('camilo', 'camilo@unal.edu.co')
        admin = crear_usuario('admin2', 'admin2@unal.edu.co', is_staff=True)
        objeto = ObjetoReclamado.objects.create(
            nombre_objeto='Cargador',
            estado=ObjetoReclamado.Estados.DISPONIBLE,
        )
        config = obtener_instrucciones_entrega()
        config.texto_minas = 'Reclama en Bienestar, edificio 2, piso 1, lunes a viernes 8-5.'
        config.save()

        self.client.force_login(estudiante)
        self.client.post(
            reverse('solicitar_reclamacion', args=[objeto.pk]),
            SOLICITUD_DATOS,
        )
        solicitud = SolicitudReclamacion.objects.get(usuario=estudiante)
        self.client.force_login(admin)
        self.client.post(
            reverse('panel_solicitud_decidir', args=[solicitud.pk]),
            {'accion': 'aprobar', 'comentario': 'Confirmado.'},
        )

        self.client.force_login(estudiante)
        respuesta = self.client.get(reverse('mis_solicitudes'))
        self.assertContains(respuesta, '¿Cómo reclamar tu objeto?')
        self.assertContains(respuesta, 'Bienestar, edificio 2, piso 1')

    def test_datos_de_entrega_especificos_del_admin_tienen_prioridad(self):
        estudiante = crear_usuario('diana', 'diana@unal.edu.co')
        admin = crear_usuario('admin4', 'admin4@unal.edu.co', is_staff=True)
        objeto = ObjetoReclamado.objects.create(
            nombre_objeto='Libro de cálculo',
            estado=ObjetoReclamado.Estados.DISPONIBLE,
        )
        config = obtener_instrucciones_entrega()
        config.texto_minas = 'Texto general de configuración.'
        config.save()

        self.client.force_login(estudiante)
        self.client.post(
            reverse('solicitar_reclamacion', args=[objeto.pk]),
            SOLICITUD_DATOS,
        )
        solicitud = SolicitudReclamacion.objects.get(usuario=estudiante)
        self.client.force_login(admin)
        self.client.post(
            reverse('panel_solicitud_decidir', args=[solicitud.pk]),
            {
                'accion': 'aprobar',
                'comentario': 'Confirmado.',
                'datos_entrega': 'Recógelo en la oficina 301, edificio 4, hoy 2-4 p.m.',
            },
        )

        self.client.force_login(estudiante)
        respuesta = self.client.get(reverse('mis_solicitudes'))
        self.assertContains(respuesta, 'Recógelo en la oficina 301, edificio 4')
        self.assertNotContains(respuesta, 'Texto general de configuración.')

    def test_vista_panel_guarda_instrucciones_por_sede(self):
        admin = crear_usuario('admin3', 'admin3@unal.edu.co', is_staff=True)
        self.client.force_login(admin)
        respuesta = self.client.post(
            reverse('panel_configuracion_entrega'),
            {
                'texto_minas': 'Entrega en oficina central de Minas, 9-12.',
                'texto_volador': 'Entrega en Volador, portería principal.',
            },
        )
        self.assertEqual(respuesta.status_code, 302)
        config = InstruccionesEntrega.objects.get(pk=1)
        self.assertEqual(config.texto_minas, 'Entrega en oficina central de Minas, 9-12.')
        self.assertEqual(config.texto_volador, 'Entrega en Volador, portería principal.')

    def test_aprobacion_usa_instruccion_de_la_sede_elegida(self):
        estudiante = crear_usuario('sofia', 'sofia@unal.edu.co')
        admin = crear_usuario('admin5', 'admin5@unal.edu.co', is_staff=True)
        config = obtener_instrucciones_entrega()
        config.texto_minas = 'Instrucciones de la Sede Minas.'
        config.texto_volador = 'Instrucciones de la Sede El Volador.'
        config.save()
        objeto = ObjetoReclamado.objects.create(
            nombre_objeto='Carpeta negra',
            estado=ObjetoReclamado.Estados.DISPONIBLE,
            sede=ObjetoReclamado.Sedes.MINAS,
        )

        self.client.force_login(estudiante)
        self.client.post(
            reverse('solicitar_reclamacion', args=[objeto.pk]),
            SOLICITUD_DATOS,
        )
        solicitud = SolicitudReclamacion.objects.get(usuario=estudiante)
        self.client.force_login(admin)
        self.client.post(
            reverse('panel_solicitud_decidir', args=[solicitud.pk]),
            {'accion': 'aprobar', 'sede': ObjetoReclamado.Sedes.VOLADOR},
        )

        solicitud.refresh_from_db()
        self.assertEqual(solicitud.datos_entrega, 'Instrucciones de la Sede El Volador.')
        self.client.force_login(estudiante)
        respuesta = self.client.get(reverse('mis_solicitudes'))
        self.assertContains(respuesta, 'Instrucciones de la Sede El Volador.')
        self.assertNotContains(respuesta, 'Instrucciones de la Sede Minas.')

    def test_panel_muestra_selector_de_sede_y_config_por_sede(self):
        admin = crear_usuario('admin6', 'admin6@unal.edu.co', is_staff=True)
        self.client.force_login(admin)
        config = obtener_instrucciones_entrega()
        config.texto_minas = 'Entrega en Bienestar Minas.'
        config.texto_volador = 'Entrega en portería Volador.'
        config.save()

        respuesta = self.client.get(reverse('panel_configuracion_entrega'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'texto_minas')
        self.assertContains(respuesta, 'texto_volador')

        objeto = ObjetoReclamado.objects.create(
            nombre_objeto='Billetera',
            estado=ObjetoReclamado.Estados.DISPONIBLE,
        )
        estudiante = crear_usuario('valeria', 'valeria@unal.edu.co')
        self.client.force_login(estudiante)
        self.client.post(
            reverse('solicitar_reclamacion', args=[objeto.pk]),
            SOLICITUD_DATOS,
        )
        solicitud = SolicitudReclamacion.objects.get(usuario=estudiante)
        self.client.force_login(admin)
        respuesta = self.client.get(reverse('panel_solicitud_detalle', args=[solicitud.pk]))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'name="sede"')
        self.assertContains(respuesta, 'textos-entrega-sedes')
        self.assertContains(respuesta, 'Entrega en Bienestar Minas.')


class NotificacionCorreoTest(TestCase):
    def setUp(self):
        self.estudiante = crear_usuario('laura', 'laura@unal.edu.co')
        self.admin = crear_usuario('adminmail', 'adminmail@unal.edu.co', is_staff=True)
        self.categoria = Categoria.objects.create(nombre='Papelería', color='#123456')
        self.objeto = ObjetoReclamado.objects.create(
            nombre_objeto='Carpeta azul',
            categoria=self.categoria,
            estado=ObjetoReclamado.Estados.DISPONIBLE,
        )

    def _solicitar(self):
        self.client.force_login(self.estudiante)
        self.client.post(
            reverse('solicitar_reclamacion', args=[self.objeto.pk]),
            SOLICITUD_DATOS,
        )
        return SolicitudReclamacion.objects.get(usuario=self.estudiante)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_aprobar_envia_correo_con_comentario_y_datos_de_entrega(self):
        solicitud = self._solicitar()
        self.client.force_login(self.admin)
        self.client.post(
            reverse('panel_solicitud_decidir', args=[solicitud.pk]),
            {
                'accion': 'aprobar',
                'comentario': 'Verificamos y sí es tuyo.',
                'datos_entrega': 'Recógelo en Bienestar, edificio 2.',
            },
        )
        self.assertEqual(len(mail.outbox), 1)
        correo = mail.outbox[0]
        self.assertEqual(correo.to, ['laura@unal.edu.co'])
        self.assertIn('aprobada', correo.subject.lower())
        contenido = ' '.join(correo.body.split()) + correo.alternatives[0][0]
        self.assertIn('Verificamos y sí es tuyo.', contenido)
        self.assertIn('Recógelo en Bienestar, edificio 2.', contenido)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_rechazar_envia_correo_sin_datos_de_entrega(self):
        solicitud = self._solicitar()
        self.client.force_login(self.admin)
        self.client.post(
            reverse('panel_solicitud_decidir', args=[solicitud.pk]),
            {'accion': 'rechazar', 'comentario': 'No coincide con el reporte.'},
        )
        self.assertEqual(len(mail.outbox), 1)
        correo = mail.outbox[0]
        self.assertIn('rechazada', correo.subject.lower())
        self.assertIn('No coincide con el reporte.', correo.body)

    def test_sin_email_del_estudiante_no_envia(self):
        self.estudiante.email = ''
        self.estudiante.save(update_fields=['email'])
        solicitud = self._solicitar()
        self.client.force_login(self.admin)
        with override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            self.client.post(
                reverse('panel_solicitud_decidir', args=[solicitud.pk]),
                {'accion': 'aprobar', 'comentario': 'ok'},
            )
        self.assertEqual(len(mail.outbox), 0)


class FiltroSedeTest(TestCase):
    def setUp(self):
        self.estudiante = crear_usuario('pedro', 'pedro@unal.edu.co')
        self.categoria = Categoria.objects.create(nombre='Gafas', color='#123456')
        self.minas = ObjetoReclamado.objects.create(
            nombre_objeto='Llaves en Minas', categoria=self.categoria,
            sede=ObjetoReclamado.Sedes.MINAS,
            estado=ObjetoReclamado.Estados.DISPONIBLE,
        )
        self.volador = ObjetoReclamado.objects.create(
            nombre_objeto='Llaves en Volador', categoria=self.categoria,
            sede=ObjetoReclamado.Sedes.VOLADOR,
            estado=ObjetoReclamado.Estados.DISPONIBLE,
        )

    def test_lista_filtra_por_sede(self):
        self.client.force_login(self.estudiante)
        respuesta = self.client.get(reverse('lista_objetos'), {'sede': 'minas'})
        self.assertContains(respuesta, 'Llaves en Minas')
        self.assertNotContains(respuesta, 'Llaves en Volador')

        respuesta = self.client.get(reverse('lista_objetos'), {'sede': 'volador'})
        self.assertContains(respuesta, 'Llaves en Volador')
        self.assertNotContains(respuesta, 'Llaves en Minas')

    def test_sin_filtro_muestra_ambas(self):
        self.client.force_login(self.estudiante)
        respuesta = self.client.get(reverse('lista_objetos'))
        self.assertContains(respuesta, 'Llaves en Minas')
        self.assertContains(respuesta, 'Llaves en Volador')

    def test_panel_filtra_por_sede(self):
        admin = crear_usuario('adminse', 'adminse@unal.edu.co', is_staff=True)
        self.client.force_login(admin)
        respuesta = self.client.get(reverse('panel_objetos'), {'sede': 'volador'})
        self.assertContains(respuesta, 'Llaves en Volador')
        self.assertNotContains(respuesta, 'Llaves en Minas')


class FormatoEntregaTest(TestCase):
    """Formato de entrega en PDF, disponible solo para el administrador y
    únicamente cuando el objeto ya fue marcado como entregado."""

    @classmethod
    def _png(cls, color=(0, 123, 84)):
        buf = io.BytesIO()
        Image.new('RGBA', (40, 22), color).save(buf, 'PNG')
        return buf.getvalue()

    def _solicitud(self, estado=SolicitudReclamacion.Estados.APROBADA, entregada=False):
        estudiante = crear_usuario('pablo', 'pablo@unal.edu.co')
        admin = crear_usuario('adminform', 'adminform@unal.edu.co', is_staff=True)
        from .models import PerfilUsuario
        perfil, _ = PerfilUsuario.objects.get_or_create(usuario=estudiante)
        perfil.tipo_documento = 'CC'
        perfil.numero_documento = '1036645213'
        perfil.telefono = '3001234567'
        perfil.save()
        objeto = ObjetoReclamado.objects.create(
            nombre_objeto='Gafas', estado=ObjetoReclamado.Estados.DISPONIBLE,
            lugar_encontrado='Biblioteca', sede=ObjetoReclamado.Sedes.MINAS,
        )
        solicitud = SolicitudReclamacion.objects.create(
            usuario=estudiante, objeto=objeto, estado=estado,
            respondida_por=admin, tipo_documento='CC',
            numero_documento='1036645213', telefono='3001234567',
            datos_entrega='Reclama en Bienestar, edificio 2.',
        )
        if entregada:
            solicitud.marcar_entregado(admin)
        return solicitud, estudiante, admin

    def test_admin_no_ve_formato_si_no_esta_entregado(self):
        solicitud, _estudiante, admin = self._solicitud(entregada=False)
        self.client.force_login(admin)
        respuesta = self.client.get(reverse('panel_solicitud_formato', args=[solicitud.pk]))
        self.assertEqual(respuesta.status_code, 302)
        self.assertRedirects(
            respuesta, reverse('panel_solicitud_detalle', args=[solicitud.pk]),
        )

    def test_admin_no_ve_formato_si_no_esta_aprobada(self):
        admin = crear_usuario('adminf2', 'adminf2@unal.edu.co', is_staff=True)
        objeto = ObjetoReclamado.objects.create(
            nombre_objeto='Cubo', estado=ObjetoReclamado.Estados.DISPONIBLE,
        )
        solicitud = SolicitudReclamacion.objects.create(
            usuario=admin, objeto=objeto,
            estado=SolicitudReclamacion.Estados.PENDIENTE,
        )
        self.client.force_login(admin)
        respuesta = self.client.get(reverse('panel_solicitud_formato', args=[solicitud.pk]))
        self.assertEqual(respuesta.status_code, 302)
        self.assertRedirects(
            respuesta, reverse('panel_solicitud_detalle', args=[solicitud.pk]),
        )

    def test_admin_descarga_formato_entregado(self):
        solicitud, _estudiante, admin = self._solicitud(entregada=True)
        self.client.force_login(admin)
        respuesta = self.client.get(reverse('panel_solicitud_formato', args=[solicitud.pk]))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta['Content-Type'], 'application/pdf')
        self.assertIn('formato_entrega', respuesta['Content-Disposition'])
        self.assertGreater(len(respuesta.content), 1000)

    def test_estudiante_no_puede_descargar_el_formato(self):
        """El PDF es exclusivo del administrador: el estudiante no lo ve."""
        solicitud, estudiante, _admin = self._solicitud(entregada=True)
        self.client.force_login(estudiante)
        respuesta = self.client.get(reverse('panel_solicitud_formato', args=[solicitud.pk]))
        self.assertEqual(respuesta.status_code, 302)  # redirigido a login (staff)
        self.assertIn('/login/', respuesta.url)

    def test_marcar_entregado_desde_el_panel(self):
        solicitud, _estudiante, admin = self._solicitud()
        self.client.force_login(admin)
        respuesta = self.client.post(
            reverse('panel_solicitud_entregar', args=[solicitud.pk]), {},
        )
        self.assertEqual(respuesta.status_code, 302)
        solicitud.refresh_from_db()
        self.assertEqual(solicitud.objeto.estado, ObjetoReclamado.Estados.ENTREGADO)
        self.assertIsNotNone(solicitud.fecha_entrega)
        self.assertEqual(solicitud.entregado_por, admin)

    def test_no_se_puede_entregar_una_no_aprobada(self):
        solicitud, _estudiante, admin = self._solicitud(
            estado=SolicitudReclamacion.Estados.PENDIENTE, entregada=False,
        )
        self.client.force_login(admin)
        respuesta = self.client.post(
            reverse('panel_solicitud_entregar', args=[solicitud.pk]), {},
        )
        self.assertEqual(respuesta.status_code, 302)
        solicitud.refresh_from_db()
        self.assertEqual(solicitud.objeto.estado, ObjetoReclamado.Estados.DISPONIBLE)

    def test_subir_firma_desde_el_panel(self):
        admin = crear_usuario('adminfir', 'adminfir@unal.edu.co', is_staff=True)
        self.client.force_login(admin)
        respuesta = self.client.post(
            reverse('panel_usuario_editar', args=[admin.pk]),
            {
                'username': admin.username,
                'email': admin.email,
                'first_name': admin.first_name,
                'last_name': admin.last_name,
                'rol': 'admin',
                'is_active': 'on',
                'firma': SimpleUploadedFile('firma.png', self._png()),
            },
        )
        self.assertEqual(respuesta.status_code, 302)
        admin.perfil.refresh_from_db()
        self.assertTrue(admin.perfil.firma)
        self.assertTrue(admin.perfil.firma.name.endswith('.png'))


class RegistroObjetoTipoDocumentoYFechaTest(TestCase):
    def setUp(self):
        self.admin = crear_usuario('adminfech', 'adminfech@unal.edu.co', is_staff=True)
        self.categoria = Categoria.objects.create(nombre='Credenciales', color='#123456')

    def _post(self, **campos):
        datos = {
            'nombre_objeto': 'Carnet',
            'categoria': self.categoria.pk,
            'descripcion_objeto': '',
            'sede': 'minas',
            'lugar_encontrado': 'Biblioteca',
            'estado': 'disponible',
            'tipo_documento': '',
            'numero_documento': '',
            'telefono': '',
            'suministro_correo': '',
            'correo': '',
            'fecha_entrega': '',
            'responsable_entrega': '',
        }
        datos.update(campos)
        self.client.force_login(self.admin)
        return self.client.post(reverse('panel_objeto_nuevo'), datos)

    def test_se_guarda_la_fecha_antigua_ingresada(self):
        self._post(fecha_registro='2025-04-12')
        objeto = ObjetoReclamado.objects.get(nombre_objeto='Carnet')
        self.assertEqual(objeto.fecha_registro.strftime('%Y-%m-%d'), '2025-04-12')
        self.assertEqual(objeto.tipo_documento, '')
        self.assertEqual(objeto.estado, ObjetoReclamado.Estados.DISPONIBLE)

    def test_sin_fecha_usa_el_dia_actual(self):
        from django.utils import timezone
        self._post(fecha_registro='')
        objeto = ObjetoReclamado.objects.get(nombre_objeto='Carnet')
        self.assertEqual(objeto.fecha_registro, timezone.localdate())
        self.assertEqual(objeto.tipo_documento, '')
        self.assertEqual(objeto.estado, ObjetoReclamado.Estados.DISPONIBLE)

    def test_la_foto_se_guarda_con_dos_inputs_camara_y_galeria(self):
        import io
        from PIL import Image
        buf = io.BytesIO()
        Image.new('RGBA', (30, 20), (10, 90, 40)).save(buf, 'PNG')
        self.client.force_login(self.admin)
        datos = {
            'nombre_objeto': 'Carnet con foto',
            'categoria': self.categoria.pk,
            'descripcion_objeto': '',
            'sede': 'minas',
            'lugar_encontrado': 'Biblioteca',
            'estado': 'disponible',
            'fecha_registro': '',
            'foto': [SimpleUploadedFile('foto_camara.png', buf.getvalue())],
        }
        respuesta = self.client.post(reverse('panel_objeto_nuevo'), datos, follow=True)
        self.assertEqual(respuesta.status_code, 200)
        objeto = ObjetoReclamado.objects.get(nombre_objeto='Carnet con foto')
        self.assertTrue(objeto.foto_base64)
        self.assertTrue(objeto.foto_base64.startswith('data:image/png;base64,'))
        self.assertIn('base64', objeto.foto_data)

    def test_formulario_muestra_botones_camara_y_galeria(self):
        self.client.force_login(self.admin)
        contenido = self.client.get(reverse('panel_objeto_nuevo')).content.decode('utf-8', 'ignore')
        self.assertIn('Tomar foto', contenido)
        self.assertIn('Galería', contenido)
        self.assertIn('data-btn-camara', contenido)
        self.assertIn('data-btn-galeria', contenido)

    def test_formulario_incluye_calendario_y_oculta_reclamante_al_registrar(self):
        self.client.force_login(self.admin)
        contenido = self.client.get(reverse('panel_objeto_nuevo')).content.decode('utf-8', 'ignore')
        self.assertIn('class="campo-fecha"', contenido)
        self.assertIn('campo-fecha-texto', contenido)
        # El bloque de reclamante NO aparece al registrar un objeto nuevo.
        self.assertNotIn('Datos de la persona que reclama', contenido)
        self.assertNotIn('value="CC"', contenido)

    def test_editar_objeto_reclamado_muestra_campos_de_reclamante(self):
        self.client.force_login(self.admin)
        objeto = ObjetoReclamado.objects.create(
            nombre_objeto='Carnet', categoria=self.categoria, estado=ObjetoReclamado.Estados.RECLAMADO,
        )
        contenido = self.client.get(reverse('panel_objeto_editar', args=[objeto.pk])).content.decode('utf-8', 'ignore')
        self.assertIn('Datos de la persona que reclama', contenido)
        for valor in ('value="CC"', 'value="TI"', 'value="CE"'):
            self.assertIn(valor, contenido)


class InicioYNavegacionTest(TestCase):
    def setUp(self):
        self.estudiante = crear_usuario('camila', 'camila@unal.edu.co')
        self.admin = crear_usuario('adminnav', 'adminnav@unal.edu.co', is_staff=True)

    def test_inicio_visible_para_estudiante_logueado(self):
        self.client.force_login(self.estudiante)
        respuesta = self.client.get(reverse('inicio'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Perdiste algo')

    def test_inicio_visible_para_administrador(self):
        self.client.force_login(self.admin)
        respuesta = self.client.get(reverse('inicio'))
        self.assertEqual(respuesta.status_code, 200)

    def test_mis_solicitudes_visible_para_administrador(self):
        self.client.force_login(self.admin)
        respuesta = self.client.get(reverse('mis_solicitudes'))
        self.assertEqual(respuesta.status_code, 200)

    def test_hero_muestra_objetos_perdidos_cuando_esta_logueado(self):
        self.client.force_login(self.estudiante)
        contenido = self.client.get(reverse('inicio')).content.decode('utf-8', 'ignore')
        self.assertIn('Ver objetos perdidos', contenido)
        self.assertNotIn('Ingresar con tu correo institucional', contenido)