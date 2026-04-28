from django.contrib import admin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('correo', 'nombre', 'apellido', 'is_staff')
    search_fields = ('correo', 'nombre', 'apellido')
