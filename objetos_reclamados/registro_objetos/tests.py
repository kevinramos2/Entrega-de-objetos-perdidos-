from django.contrib.auth.models import User
from django.core import mail
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


class FlujoSolicitudApelacionTest(TestCase):
    def setUp(self):
        self.estudiante = crear_usuario('santiago', 'santiago@unal.edu.co')
        self.admin = crear_usuario('keramosl', 'keramosl@unal.edu.co', is_staff=True)
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
            {'mensaje': 'Es mío, lo perdí en la cafetería.'},
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

    def test_contador_de_respuesta_nueva_en_mis_reclamos(self):
        self._solicitar()
        self.solicitud = SolicitudReclamacion.objects.get(usuario=self.estudiante)
        self._rechazar(comentario='Revisamos y no coincide.')
        self.solicitud.refresh_from_db()
        self.assertFalse(self.solicitud.respuesta_vista)

        # La pestaña "Mis reclamos" muestra la señal con la respuesta sin leer.
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
            {'mensaje': 'Es mío.'},
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
            {'mensaje': 'Es mío.'},
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
            {'mensaje': 'Es mía.'},
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
            {'mensaje': 'Es mía.'},
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
            {'mensaje': 'Perdí una carpeta azul.'},
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