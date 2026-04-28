from django.urls import path, re_path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('entrar/', views.iniciar_sesion, name='login'),
    path('recuperar/', views.olvido_password, name='olvido_password'),
    path('nueva-clave/', views.restablecer_password, name='restablecer_password'),
    path('registro/', views.registrar_usuario, name='registro'),
    path('salir/', views.cerrar_sesion, name='logout'),
]
