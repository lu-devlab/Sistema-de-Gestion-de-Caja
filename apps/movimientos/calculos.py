from decimal import Decimal

from .models import MovimientoCaja


def obtener_estado_cierre(diferencia):
    if diferencia == Decimal('0.00'):
        return 'CUADRADA'
    if diferencia < 0:
        return 'FALTANTE'
    return 'SOBRANTE'


def obtener_totales_caja(caja, *, incluir_movimientos=False, ordenar=False):
    movimientos = MovimientoCaja.objects.filter(caja=caja)

    if ordenar:
        movimientos = movimientos.order_by('-hora_movimiento', '-id_movimiento')

    movimientos = list(movimientos)
    total_ingresos = Decimal('0.00')
    total_egresos = Decimal('0.00')
    ingresos_efectivo = Decimal('0.00')
    ingresos_digitales = Decimal('0.00')
    egresos_efectivo = Decimal('0.00')
    egresos_digitales = Decimal('0.00')

    for movimiento in movimientos:
        es_efectivo = movimiento.medio_pago == 'EFECTIVO'

        if movimiento.tipo_movimiento == 'INGRESO':
            total_ingresos += movimiento.monto
            if es_efectivo:
                ingresos_efectivo += movimiento.monto
            else:
                ingresos_digitales += movimiento.monto
        else:
            total_egresos += movimiento.monto
            if es_efectivo:
                egresos_efectivo += movimiento.monto
            else:
                egresos_digitales += movimiento.monto

    saldo_efectivo_esperado = (
        caja.monto_inicial
        + ingresos_efectivo
        - egresos_efectivo
    )
    saldo_digital_esperado = ingresos_digitales - egresos_digitales
    movimiento_efectivo = ingresos_efectivo - egresos_efectivo
    movimiento_digital = ingresos_digitales - egresos_digitales
    saldo_movimientos = total_ingresos - total_egresos
    saldo_esperado = saldo_efectivo_esperado + saldo_digital_esperado

    totales = {
        'total_ingresos': total_ingresos,
        'total_egresos': total_egresos,
        'ingresos_efectivo': ingresos_efectivo,
        'ingresos_digitales': ingresos_digitales,
        'egresos_efectivo': egresos_efectivo,
        'egresos_digitales': egresos_digitales,
        'movimiento_efectivo': movimiento_efectivo,
        'movimiento_digital': movimiento_digital,
        'saldo_efectivo_esperado': saldo_efectivo_esperado,
        'saldo_digital_esperado': saldo_digital_esperado,
        'saldo_movimientos': saldo_movimientos,
        'saldo_esperado': saldo_esperado,
    }

    if incluir_movimientos:
        totales['movimientos'] = movimientos

    return totales


def calcular_diferencia_cierre(caja, cierre, totales=None):
    if not cierre:
        return Decimal('0.00')

    if totales is None:
        totales = obtener_totales_caja(caja)

    saldo_real_total = cierre.saldo_real + cierre.saldo_real_digital
    return saldo_real_total - totales['saldo_esperado']
