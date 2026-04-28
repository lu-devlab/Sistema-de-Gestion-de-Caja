from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from apertura.models import CajaDiaria
from cierre.models import CierreCaja
from movimientos.models import MovimientoCaja


def calcular_totales(caja):
    movimientos = MovimientoCaja.objects.filter(caja=caja).order_by(
        '-hora_movimiento',
        '-id_movimiento',
    )
    total_ingresos = Decimal('0.00')
    total_egresos = Decimal('0.00')

    for movimiento in movimientos:
        if movimiento.tipo_movimiento == 'INGRESO':
            total_ingresos += movimiento.monto
        else:
            total_egresos += movimiento.monto

    return movimientos, total_ingresos, total_egresos


def obtener_diferencia(cierre):
    if not cierre:
        return Decimal('0.00')
    return abs(cierre.diferencia)


@login_required
def inicio(request):
    hoy = timezone.localdate()
    hora_actual = timezone.localtime().strftime('%H:%M')
    fecha_seleccionada = request.GET.get('fecha', '')

    cajas = CajaDiaria.objects.filter(
        usuario=request.user,
    ).order_by('-fecha_caja')

    historial = []
    caja_detalle = None
    cierre_detalle = None
    movimientos_detalle = []
    total_ingresos_detalle = Decimal('0.00')
    total_egresos_detalle = Decimal('0.00')
    diferencia_detalle = Decimal('0.00')

    for caja in cajas:
        cierre = CierreCaja.objects.filter(caja=caja).first()
        _, total_ingresos, total_egresos = calcular_totales(caja)
        diferencia = obtener_diferencia(cierre)

        historial.append({
            'caja': caja,
            'cierre': cierre,
            'total_ingresos': total_ingresos,
            'total_egresos': total_egresos,
            'diferencia': diferencia,
        })

        fecha_texto = caja.fecha_caja.strftime('%Y-%m-%d')
        if fecha_seleccionada == fecha_texto:
            caja_detalle = caja
            cierre_detalle = cierre
            diferencia_detalle = diferencia
            (
                movimientos_detalle,
                total_ingresos_detalle,
                total_egresos_detalle,
            ) = calcular_totales(caja)

    if not caja_detalle and historial:
        primer_item = historial[0]
        caja_detalle = primer_item['caja']
        cierre_detalle = primer_item['cierre']
        diferencia_detalle = primer_item['diferencia']
        (
            movimientos_detalle,
            total_ingresos_detalle,
            total_egresos_detalle,
        ) = calcular_totales(caja_detalle)

    contexto = {
        'fecha_hoy': hoy,
        'hora_actual': hora_actual,
        'historial': historial,
        'caja_detalle': caja_detalle,
        'cierre_detalle': cierre_detalle,
        'movimientos_detalle': movimientos_detalle,
        'total_ingresos_detalle': total_ingresos_detalle,
        'total_egresos_detalle': total_egresos_detalle,
        'diferencia_detalle': diferencia_detalle,
        'fecha_seleccionada': fecha_seleccionada,
    }
    return render(request, 'historial/inicio.html', contexto)
