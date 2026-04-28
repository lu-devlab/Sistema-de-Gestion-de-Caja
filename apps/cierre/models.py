from django.db import models
from apertura.models import CajaDiaria

class CierreCaja(models.Model):
    id_cierre = models.AutoField(primary_key=True)
    caja = models.OneToOneField(CajaDiaria, on_delete=models.CASCADE, db_column='id_caja')
    hora_cierre = models.TimeField()
    total_ingresos = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_egresos = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    saldo_esperado = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    saldo_real = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    saldo_real_digital = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    diferencia = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    estado_cierre = models.CharField(max_length=10)
    observacion = models.CharField(max_length=255, null=True, blank=True)
    class Meta:
        db_table = 'cierre_caja'
