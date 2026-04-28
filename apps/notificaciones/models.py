from django.db import models
from usuarios.models import Usuario

class Notificacion(models.Model):
    id_notificacion = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    titulo = models.CharField(max_length=150)
    mensaje = models.CharField(max_length=255)
    tipo_notificacion = models.CharField(max_length=20)
    fecha_notificacion = models.DateField()
    hora_notificacion = models.TimeField()
    leida = models.BooleanField(default=False)
    class Meta:
        db_table = 'notificacion'
