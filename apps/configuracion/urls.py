from django.urls import path

from . import views

app_name = 'configuracion'

urlpatterns = [
    path('perfil/', views.perfil, name='perfil'),
    path('foto/', views.gestionar_foto, name='foto'),
    path('moneda/', views.moneda, name='moneda'),
    path('acceso/', views.acceso_cuenta, name='acceso'),
]
