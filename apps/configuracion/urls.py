from django.urls import path
from . import views

app_name = 'configuracion'

urlpatterns = [
    path('perfil/', views.perfil, name='perfil'),
    path('foto/', views.gestionar_foto, name='foto'),
]
