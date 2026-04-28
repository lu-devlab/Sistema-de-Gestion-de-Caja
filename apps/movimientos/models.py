from django.db import models
from usuarios.models import Usuario
from apertura.models import CajaDiaria

class CategoriaMovimiento(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre_categoria = models.CharField(max_length=100)
    tipo_categoria = models.CharField(max_length=10)
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    class Meta:
        db_table = 'categoria_movimiento'

class MovimientoCaja(models.Model):
    id_movimiento = models.AutoField(primary_key=True)
    caja = models.ForeignKey(CajaDiaria, on_delete=models.CASCADE, db_column='id_caja')
    categoria = models.ForeignKey(CategoriaMovimiento, on_delete=models.RESTRICT, db_column='id_categoria')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    tipo_movimiento = models.CharField(max_length=10)
    medio_pago = models.CharField(max_length=20, default='EFECTIVO')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.CharField(max_length=255)
    fecha_movimiento = models.DateField()
    hora_movimiento = models.TimeField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'movimiento_caja'
