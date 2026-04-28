from django.urls import path

from . import views

app_name = 'historial'

urlpatterns = [
    path('historial/', views.inicio, name='inicio'),
]
