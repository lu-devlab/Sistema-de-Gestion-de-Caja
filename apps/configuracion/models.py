from django.db import models
from usuarios.models import Usuario

class Configuracion(models.Model):
    id_configuracion = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    nombre_negocio = models.CharField(max_length=150)
    responsable = models.CharField(max_length=150)
    direccion = models.CharField(max_length=200, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    correo_negocio = models.EmailField(max_length=150, null=True, blank=True)
    moneda = models.CharField(max_length=10, default='PEN')
    hora_apertura = models.TimeField(null=True, blank=True)
    hora_cierre = models.TimeField(null=True, blank=True)
    monto_inicial_sugerido = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    permitir_edicion_movimientos = models.BooleanField(default=True)
    permitir_eliminacion_movimientos = models.BooleanField(default=True)
    limite_diferencia_caja = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    class Meta:
        db_table = 'configuracion'
