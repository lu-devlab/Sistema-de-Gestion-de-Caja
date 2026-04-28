from django.urls import path
from . import views

app_name = 'apertura'

urlpatterns = [
    path('apertura/', views.inicio, name='inicio'),
    path('apertura/abrir/', views.abrir_caja, name='abrir_caja'),
]
