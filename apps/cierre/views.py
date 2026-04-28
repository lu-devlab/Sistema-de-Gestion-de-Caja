from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from apertura.models import CajaDiaria
from configuracion.models import Configuracion
from movimientos.models import MovimientoCaja

from .models import CierreCaja
def obtener_caja_hoy(usuario, hoy):
    return CajaDiaria.objects.filter(
        usuario=usuario,
        fecha_caja=hoy,
    ).first()


def obtener_totales(caja):
    movimientos = MovimientoCaja.objects.filter(caja=caja)
    total_ingresos = Decimal('0.00')
    total_egresos = Decimal('0.00')
    ingresos_efectivo = Decimal('0.00')
    ingresos_digitales = Decimal('0.00')
    egresos_efectivo = Decimal('0.00')
    egresos_digitales = Decimal('0.00')

    for movimiento in movimientos:
        if movimiento.tipo_movimiento == 'INGRESO':
            total_ingresos += movimiento.monto
            if movimiento.medio_pago == 'EFECTIVO':
                ingresos_efectivo += movimiento.monto
            else:
                ingresos_digitales += movimiento.monto
        else:
            total_egresos += movimiento.monto
            if movimiento.medio_pago == 'EFECTIVO':
                egresos_efectivo += movimiento.monto
            else:
                egresos_digitales += movimiento.monto

    saldo_esperado = caja.monto_inicial + ingresos_efectivo - egresos_efectivo

    return {
        'total_ingresos': total_ingresos,
        'total_egresos': total_egresos,
        'ingresos_efectivo': ingresos_efectivo,
        'ingresos_digitales': ingresos_digitales,
        'egresos_efectivo': egresos_efectivo,
        'egresos_digitales': egresos_digitales,
        'saldo_esperado': saldo_esperado,
    }


def obtener_estado_cierre(diferencia):
    if diferencia == Decimal('0.00'):
        return 'CUADRADA'
    if diferencia < 0:
        return 'FALTANTE'
    return 'SOBRANTE'


def obtener_diferencia_visible(diferencia):
    return abs(diferencia)


@login_required
def inicio(request):
    hoy = timezone.localdate()
    hora_actual = timezone.localtime().strftime('%H:%M')
    caja_hoy = obtener_caja_hoy(request.user, hoy)
    cierre_hoy = None
    total_ingresos = Decimal('0.00')
    total_egresos = Decimal('0.00')
    saldo_esperado = Decimal('0.00')
    ingresos_efectivo = Decimal('0.00')
    ingresos_digitales = Decimal('0.00')
    egresos_efectivo = Decimal('0.00')
    egresos_digitales = Decimal('0.00')
    saldo_digital_esperado = Decimal('0.00')
    diferencia_visible = Decimal('0.00')
    limite_diferencia = Decimal('0.00')
    limite_superado = False

    configuracion = Configuracion.objects.filter(usuario=request.user).first()
    if configuracion:
        limite_diferencia = configuracion.limite_diferencia_caja

    if caja_hoy:
        cierre_hoy = CierreCaja.objects.filter(caja=caja_hoy).first()
        totales = obtener_totales(caja_hoy)
        total_ingresos = totales['total_ingresos']
        total_egresos = totales['total_egresos']
        ingresos_efectivo = totales['ingresos_efectivo']
        ingresos_digitales = totales['ingresos_digitales']
        egresos_efectivo = totales['egresos_efectivo']
        egresos_digitales = totales['egresos_digitales']
        saldo_esperado = totales['saldo_esperado']
        saldo_digital_esperado = ingresos_digitales - egresos_digitales
        if cierre_hoy:
            diferencia_visible = obtener_diferencia_visible(
                cierre_hoy.diferencia,
            )
            limite_superado = diferencia_visible > limite_diferencia

    if request.method == 'POST':
        accion = request.POST.get('accion', 'registrar')

        if accion == 'editar':
            return editar_cierre(request, caja_hoy, cierre_hoy, saldo_esperado)

        if accion == 'eliminar':
            return eliminar_cierre(request, caja_hoy, cierre_hoy)

        if not caja_hoy:
            return redirect('cierre:inicio')

        if cierre_hoy:
            return redirect('cierre:inicio')

        saldo_real_texto = request.POST.get('saldo_real', '0').strip()
        saldo_real_digital_texto = request.POST.get(
            'saldo_real_digital',
            '0',
        ).strip()
        observacion = request.POST.get('observacion', '').strip()

        try:
            saldo_real = Decimal(saldo_real_texto)
        except InvalidOperation:
            return redirect('cierre:inicio')

        try:
            saldo_real_digital = Decimal(saldo_real_digital_texto)
        except InvalidOperation:
            return redirect('cierre:inicio')

        if saldo_real < 0 or saldo_real_digital < 0:
            return redirect('cierre:inicio')

        diferencia = saldo_real - saldo_esperado
        estado_cierre = obtener_estado_cierre(diferencia)

        CierreCaja.objects.create(
            caja=caja_hoy,
            hora_cierre=timezone.localtime().time().replace(microsecond=0),
            total_ingresos=total_ingresos,
            total_egresos=total_egresos,
            saldo_esperado=saldo_esperado,
            saldo_real=saldo_real,
            saldo_real_digital=saldo_real_digital,
            diferencia=diferencia,
            estado_cierre=estado_cierre,
            observacion=observacion or None,
        )

        caja_hoy.estado_caja = 'CERRADA'
        caja_hoy.save(update_fields=['estado_caja'])

        return redirect('cierre:inicio')

    contexto = {
        'fecha_hoy': hoy,
        'hora_actual': hora_actual,
        'caja_hoy': caja_hoy,
        'cierre_hoy': cierre_hoy,
        'total_ingresos': total_ingresos,
        'total_egresos': total_egresos,
        'saldo_esperado': saldo_esperado,
        'ingresos_efectivo': ingresos_efectivo,
        'ingresos_digitales': ingresos_digitales,
        'egresos_efectivo': egresos_efectivo,
        'egresos_digitales': egresos_digitales,
        'saldo_digital_esperado': saldo_digital_esperado,
        'diferencia_visible': diferencia_visible,
        'limite_diferencia': limite_diferencia,
        'limite_superado': limite_superado,
    }
    return render(request, 'cierre/inicio.html', contexto)


def editar_cierre(request, caja_hoy, cierre_hoy, saldo_esperado):
    if not caja_hoy or not cierre_hoy:
        return redirect('cierre:inicio')

    saldo_real_texto = request.POST.get('saldo_real', '0').strip()
    saldo_real_digital_texto = request.POST.get(
        'saldo_real_digital',
        '0',
    ).strip()
    observacion = request.POST.get('observacion', '').strip()

    try:
        saldo_real = Decimal(saldo_real_texto)
    except InvalidOperation:
        return redirect('cierre:inicio')

    try:
        saldo_real_digital = Decimal(saldo_real_digital_texto)
    except InvalidOperation:
        return redirect('cierre:inicio')

    if saldo_real < 0 or saldo_real_digital < 0:
        return redirect('cierre:inicio')

    diferencia = saldo_real - saldo_esperado
    estado_cierre = obtener_estado_cierre(diferencia)

    cierre_hoy.saldo_real = saldo_real
    cierre_hoy.saldo_real_digital = saldo_real_digital
    cierre_hoy.diferencia = diferencia
    cierre_hoy.estado_cierre = estado_cierre
    cierre_hoy.observacion = observacion or None
    cierre_hoy.hora_cierre = timezone.localtime().time().replace(microsecond=0)
    cierre_hoy.save(
        update_fields=[
            'saldo_real',
            'saldo_real_digital',
            'diferencia',
            'estado_cierre',
            'observacion',
            'hora_cierre',
        ]
    )

    return redirect('cierre:inicio')


def eliminar_cierre(request, caja_hoy, cierre_hoy):
    if not caja_hoy or not cierre_hoy:
        return redirect('cierre:inicio')

    cierre_hoy.delete()
    caja_hoy.estado_caja = 'ABIERTA'
    caja_hoy.save(update_fields=['estado_caja'])

    return redirect('cierre:inicio')
