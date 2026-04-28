from django.test import TestCase
from django.urls import reverse

from configuracion.models import Configuracion
from usuarios.models import Usuario


class ConfiguracionViewsTests(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            correo='admin@cajapulso.com',
            password='ClaveSegura2026#',
            nombre='Caja',
            apellido='Pulso',
        )
        self.client.force_login(self.user)

    def test_perfil_actualiza_datos_personales(self):
        response = self.client.post(
            reverse('configuracion:perfil'),
            {
                'nombre': 'Lucia',
                'apellido': 'Perez',
                'dni': '12345678',
                'telefono': '987654321',
            },
        )

        self.assertRedirects(response, reverse('configuracion:perfil'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.nombre, 'Lucia')
        self.assertEqual(self.user.apellido, 'Perez')
        self.assertEqual(self.user.dni, '12345678')
        self.assertEqual(self.user.telefono, '987654321')

    def test_moneda_crea_configuracion_y_actualiza_moneda(self):
        response = self.client.post(
            reverse('configuracion:moneda'),
            {'moneda': 'COP'},
        )

        self.assertRedirects(response, reverse('configuracion:moneda'))
        configuracion = Configuracion.objects.get(usuario=self.user)
        self.assertEqual(configuracion.moneda, 'COP')

    def test_acceso_actualiza_correo_y_contrasena(self):
        response = self.client.post(
            reverse('configuracion:acceso'),
            {
                'correo': 'nuevo@cajapulso.com',
                'password_actual': 'ClaveSegura2026#',
                'nueva_contrasena': 'CajaPulsoSegura2026#',
                'repetir_contrasena': 'CajaPulsoSegura2026#',
            },
        )

        self.assertRedirects(response, reverse('configuracion:acceso'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.correo, 'nuevo@cajapulso.com')
        self.assertTrue(self.user.check_password('CajaPulsoSegura2026#'))
