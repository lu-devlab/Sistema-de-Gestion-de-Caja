from django.db import models
from usuarios.models import Usuario

class CajaDiaria(models.Model):
    id_caja = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    fecha_caja = models.DateField()
    hora_apertura = models.TimeField()
    monto_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    estado_caja = models.CharField(max_length=10, default='ABIERTA')
    observacion = models.CharField(max_length=255, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'caja_diaria'
        unique_together = ('usuario', 'fecha_caja')
