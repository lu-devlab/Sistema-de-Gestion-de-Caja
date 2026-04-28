from django.urls import path

from . import views

app_name = 'movimientos'

urlpatterns = [
    path('movimientos/', views.inicio, name='inicio'),
]
