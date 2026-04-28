from decimal import Decimal

from django.utils import timezone

from apertura.models import CajaDiaria
from cierre.models import CierreCaja

from .models import Notificacion

TIPOS_NOTIFICACION = {
    'APERTURA_PENDIENTE': 'Apertura pendiente',
    'CIERRE_PENDIENTE': 'Cierre pendiente',
    'DIFERENCIA_CAJA': 'Diferencia de caja',
    'GASTO_ELEVADO': 'Gasto elevado',
}


def obtener_tipo_label(tipo_notificacion):
    return TIPOS_NOTIFICACION.get(tipo_notificacion, 'Aviso del sistema')


def crear_o_actualizar_notificacion(
    usuario,
    tipo_notificacion,
    fecha_notificacion,
    titulo,
    mensaje,
    *,
    reabrir_si_cambia=False,
):
    hora_actual = timezone.localtime().time().replace(microsecond=0)
    notificacion, creada = Notificacion.objects.get_or_create(
        usuario=usuario,
        tipo_notificacion=tipo_notificacion,
        fecha_notificacion=fecha_notificacion,
        defaults={
            'titulo': titulo,
            'mensaje': mensaje,
            'hora_notificacion': hora_actual,
            'leida': False,
        },
    )

    if creada:
        return notificacion

    cambios = []
    contenido_cambio = False

    if notificacion.titulo != titulo:
        notificacion.titulo = titulo
        cambios.append('titulo')
        contenido_cambio = True

    if notificacion.mensaje != mensaje:
        notificacion.mensaje = mensaje
        cambios.append('mensaje')
        contenido_cambio = True

    if notificacion.hora_notificacion != hora_actual:
        notificacion.hora_notificacion = hora_actual
        cambios.append('hora_notificacion')

    if reabrir_si_cambia and contenido_cambio and notificacion.leida:
        notificacion.leida = False
        cambios.append('leida')

    if cambios:
        notificacion.save(update_fields=cambios)

    return notificacion


def eliminar_notificacion(usuario, tipo_notificacion, fecha_notificacion):
    Notificacion.objects.filter(
        usuario=usuario,
        tipo_notificacion=tipo_notificacion,
        fecha_notificacion=fecha_notificacion,
    ).delete()


def construir_mensaje_diferencia(diferencia):
    diferencia_visible = abs(diferencia)
    monto = f'{diferencia_visible:.2f}'

    if diferencia < 0:
        return (
            'Se detecto un faltante en el cierre diario. '
            f'Revisa la diferencia registrada: {monto}'
        )

    return (
        'Se detecto un sobrante en el cierre diario. '
        f'Revisa la diferencia registrada: {monto}'
    )


def sincronizar_notificaciones_usuario(usuario):
    hoy = timezone.localdate()
    caja_hoy = CajaDiaria.objects.filter(
        usuario=usuario,
        fecha_caja=hoy,
    ).first()

    cierre_hoy = None
    if caja_hoy:
        cierre_hoy = CierreCaja.objects.filter(caja=caja_hoy).first()

    if caja_hoy is None:
        crear_o_actualizar_notificacion(
            usuario,
            'APERTURA_PENDIENTE',
            hoy,
            'Apertura pendiente',
            'Todavia no registraste la apertura de caja del dia',
        )
    else:
        eliminar_notificacion(usuario, 'APERTURA_PENDIENTE', hoy)

    if caja_hoy and cierre_hoy is None and caja_hoy.estado_caja == 'ABIERTA':
        crear_o_actualizar_notificacion(
            usuario,
            'CIERRE_PENDIENTE',
            hoy,
            'Cierre pendiente',
            'La caja sigue abierta. Falta registrar el cierre diario',
        )
    else:
        eliminar_notificacion(usuario, 'CIERRE_PENDIENTE', hoy)

    if cierre_hoy and cierre_hoy.diferencia != Decimal('0.00'):
        crear_o_actualizar_notificacion(
            usuario,
            'DIFERENCIA_CAJA',
            hoy,
            'Diferencia detectada en caja',
            construir_mensaje_diferencia(cierre_hoy.diferencia),
            reabrir_si_cambia=True,
        )
    else:
        eliminar_notificacion(usuario, 'DIFERENCIA_CAJA', hoy)
