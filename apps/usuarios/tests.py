from urllib.parse import parse_qs, urlparse

from django.core import signing
from django.test import TestCase
from django.urls import reverse

from usuarios.models import Usuario
from usuarios.views import (
    RESET_PASSWORD_TOKEN_MAX_AGE,
    RESET_PASSWORD_TOKEN_SALT,
    generar_token_restablecimiento,
)


class RecuperacionPasswordTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            correo='admin@cajapulso.com',
            password='ClaveSegura2026#',
            nombre='Caja',
            apellido='Pulso',
        )

    def test_olvido_password_redirige_a_formulario_nueva_clave(self):
        response = self.client.post(
            reverse('usuarios:olvido_password'),
            {'correo': self.usuario.correo},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            response.url.startswith(reverse('usuarios:restablecer_password')),
        )

        query = parse_qs(urlparse(response.url).query)
        token = query['token'][0]
        payload = signing.loads(
            token,
            salt=RESET_PASSWORD_TOKEN_SALT,
            max_age=RESET_PASSWORD_TOKEN_MAX_AGE,
        )

        self.assertEqual(payload['user_id'], self.usuario.pk)
        self.assertEqual(payload['correo'], self.usuario.correo)

    def test_restablecer_password_actualiza_la_clave(self):
        token = generar_token_restablecimiento(self.usuario)

        response = self.client.post(
            reverse('usuarios:restablecer_password'),
            {
                'token': token,
                'nueva_password': 'CajaPulsoNueva2026#',
                'confirmar_password': 'CajaPulsoNueva2026#',
            },
        )

        self.assertRedirects(response, reverse('usuarios:login'))
        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.check_password('CajaPulsoNueva2026#'))

    def test_restablecer_password_redirige_si_token_no_es_valido(self):
        response = self.client.get(
            reverse('usuarios:restablecer_password'),
            {'token': 'token-invalido'},
        )

        self.assertRedirects(response, reverse('usuarios:olvido_password'))
