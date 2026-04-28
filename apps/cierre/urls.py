from django.urls import path

from . import views

app_name = 'cierre'

urlpatterns = [
    path('cierre/', views.inicio, name='inicio'),
]
