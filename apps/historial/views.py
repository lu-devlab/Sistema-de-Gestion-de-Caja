from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from apertura.models import CajaDiaria
from cierre.models import CierreCaja
from movimientos.calculos import (
    calcular_diferencia_cierre,
    obtener_estado_cierre,
    obtener_totales_caja,
)


def calcular_totales(caja):
    return obtener_totales_caja(
        caja,
        incluir_movimientos=True,
        ordenar=True,
    )


def obtener_diferencia(caja, cierre, totales):
    if not cierre:
        return Decimal('0.00')
    return abs(calcular_diferencia_cierre(caja, cierre, totales))


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
    saldo_esperado_detalle = Decimal('0.00')
    diferencia_detalle = Decimal('0.00')
    estado_cierre_detalle = ''

    for caja in cajas:
        cierre = CierreCaja.objects.filter(caja=caja).first()
        totales = calcular_totales(caja)
        total_ingresos = totales['total_ingresos']
        total_egresos = totales['total_egresos']
        saldo_esperado = totales['saldo_esperado']
        diferencia = obtener_diferencia(caja, cierre, totales)
        estado_cierre = ''

        if cierre:
            estado_cierre = obtener_estado_cierre(
                calcular_diferencia_cierre(caja, cierre, totales),
            )

        historial.append({
            'caja': caja,
            'cierre': cierre,
            'total_ingresos': total_ingresos,
            'total_egresos': total_egresos,
            'saldo_esperado': saldo_esperado,
            'diferencia': diferencia,
            'estado_cierre': estado_cierre,
        })

        fecha_texto = caja.fecha_caja.strftime('%Y-%m-%d')
        if fecha_seleccionada == fecha_texto:
            caja_detalle = caja
            cierre_detalle = cierre
            diferencia_detalle = diferencia
            estado_cierre_detalle = estado_cierre
            movimientos_detalle = totales['movimientos']
            total_ingresos_detalle = total_ingresos
            total_egresos_detalle = total_egresos
            saldo_esperado_detalle = saldo_esperado

    if not caja_detalle and historial:
        primer_item = historial[0]
        caja_detalle = primer_item['caja']
        cierre_detalle = primer_item['cierre']
        diferencia_detalle = primer_item['diferencia']
        estado_cierre_detalle = primer_item['estado_cierre']
        totales_detalle = calcular_totales(caja_detalle)
        movimientos_detalle = totales_detalle['movimientos']
        total_ingresos_detalle = totales_detalle['total_ingresos']
        total_egresos_detalle = totales_detalle['total_egresos']
        saldo_esperado_detalle = totales_detalle['saldo_esperado']

    contexto = {
        'fecha_hoy': hoy,
        'hora_actual': hora_actual,
        'historial': historial,
        'caja_detalle': caja_detalle,
        'cierre_detalle': cierre_detalle,
        'movimientos_detalle': movimientos_detalle,
        'total_ingresos_detalle': total_ingresos_detalle,
        'total_egresos_detalle': total_egresos_detalle,
        'saldo_esperado_detalle': saldo_esperado_detalle,
        'diferencia_detalle': diferencia_detalle,
        'estado_cierre_detalle': estado_cierre_detalle,
        'fecha_seleccionada': fecha_seleccionada,
    }
    return render(request, 'historial/inicio.html', contexto)
