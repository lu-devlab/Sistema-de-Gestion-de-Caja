from datetime import timedelta
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


def obtener_rango_periodo(tipo_periodo, fecha_base, desde, hasta):
    if tipo_periodo == 'dia':
        return fecha_base, fecha_base

    if tipo_periodo == 'semana':
        inicio = fecha_base - timedelta(days=fecha_base.weekday())
        fin = inicio + timedelta(days=6)
        return inicio, fin

    if tipo_periodo == 'mes':
        inicio = fecha_base.replace(day=1)
        if inicio.month == 12:
            siguiente = inicio.replace(
                year=inicio.year + 1,
                month=1,
            )
        else:
            siguiente = inicio.replace(month=inicio.month + 1)
        fin = siguiente - timedelta(days=1)
        return inicio, fin

    if tipo_periodo == 'anio':
        inicio = fecha_base.replace(month=1, day=1)
        fin = fecha_base.replace(month=12, day=31)
        return inicio, fin

    if tipo_periodo == 'rango' and desde and hasta:
        return desde, hasta

    return fecha_base, fecha_base


def calcular_resumen_jornada(caja):
    totales = obtener_totales_caja(
        caja,
        incluir_movimientos=True,
        ordenar=True,
    )
    movimientos = totales['movimientos']
    cierre = CierreCaja.objects.filter(caja=caja).first()
    total_ingresos = totales['total_ingresos']
    total_egresos = totales['total_egresos']
    diferencia = Decimal('0.00')
    estado_cierre = ''

    if cierre:
        diferencia_firmada = calcular_diferencia_cierre(
            caja,
            cierre,
            totales,
        )
        diferencia = abs(diferencia_firmada)
        estado_cierre = obtener_estado_cierre(diferencia_firmada)

    return {
        'caja': caja,
        'movimientos': movimientos,
        'cierre': cierre,
        'total_ingresos': total_ingresos,
        'total_egresos': total_egresos,
        'saldo_movimientos': totales['saldo_movimientos'],
        'saldo_neto': totales['saldo_esperado'],
        'diferencia': diferencia,
        'estado_cierre': estado_cierre,
    }


def obtener_fecha(texto, valor_defecto):
    if not texto:
        return valor_defecto

    try:
        return timezone.datetime.strptime(
            texto,
            '%Y-%m-%d',
        ).date()
    except ValueError:
        return valor_defecto


@login_required
def inicio(request):
    hoy = timezone.localdate()
    hora_actual = timezone.localtime().strftime('%H:%M')
    tipo_periodo = request.GET.get('periodo', 'dia').strip() or 'dia'
    fecha_texto = request.GET.get('fecha', '')
    desde_texto = request.GET.get('desde', '')
    hasta_texto = request.GET.get('hasta', '')

    fecha_base = obtener_fecha(fecha_texto, hoy)
    fecha_desde = obtener_fecha(desde_texto, fecha_base)
    fecha_hasta = obtener_fecha(hasta_texto, fecha_base)

    if fecha_desde > fecha_hasta:
        fecha_desde, fecha_hasta = fecha_hasta, fecha_desde

    inicio_periodo, fin_periodo = obtener_rango_periodo(
        tipo_periodo,
        fecha_base,
        fecha_desde,
        fecha_hasta,
    )

    cajas_periodo = CajaDiaria.objects.filter(
        usuario=request.user,
        fecha_caja__range=(inicio_periodo, fin_periodo),
    ).order_by('-fecha_caja')

    jornadas = []
    total_ingresos = Decimal('0.00')
    total_egresos = Decimal('0.00')
    total_diferencia = Decimal('0.00')
    total_apertura = Decimal('0.00')
    estados_cierre = {
        'CUADRADA': 0,
        'FALTANTE': 0,
        'SOBRANTE': 0,
    }

    for caja in cajas_periodo:
        resumen = calcular_resumen_jornada(caja)
        jornadas.append(resumen)
        total_ingresos += resumen['total_ingresos']
        total_egresos += resumen['total_egresos']
        total_diferencia += resumen['diferencia']
        total_apertura += caja.monto_inicial
        if resumen['cierre']:
            estado = resumen['estado_cierre']
            estados_cierre[estado] = estados_cierre.get(estado, 0) + 1

    detalle_jornada = jornadas[0] if jornadas else None
    fecha_resumen = (
        f'{inicio_periodo.strftime("%d/%m/%Y")} - '
        f'{fin_periodo.strftime("%d/%m/%Y")}'
    )

    nombres_periodo = {
        'dia': 'Diario',
        'semana': 'Semanal',
        'mes': 'Mensual',
        'anio': 'Anual',
        'rango': 'Por rango',
    }
    jornadas_grafico = list(reversed(jornadas))
    grafico_fechas = [
        item['caja'].fecha_caja.strftime('%d/%m')
        for item in jornadas_grafico
    ]
    grafico_ingresos = [
        float(item['total_ingresos'])
        for item in jornadas_grafico
    ]
    grafico_egresos = [
        float(item['total_egresos'])
        for item in jornadas_grafico
    ]
    grafico_saldos = [
        float(item['saldo_neto'])
        for item in jornadas_grafico
    ]
    grafico_estados = [
        estados_cierre['CUADRADA'],
        estados_cierre['FALTANTE'],
        estados_cierre['SOBRANTE'],
    ]

    if not grafico_fechas:
        grafico_fechas = ['Sin datos']
        grafico_ingresos = [0.0]
        grafico_egresos = [0.0]
        grafico_saldos = [0.0]

    if sum(grafico_estados) == 0:
        grafico_estados = [1, 0, 0]

    contexto = {
        'fecha_hoy': hoy,
        'hora_actual': hora_actual,
        'tipo_periodo': tipo_periodo,
        'fecha_texto': fecha_base.strftime('%Y-%m-%d'),
        'desde_texto': inicio_periodo.strftime('%Y-%m-%d'),
        'hasta_texto': fin_periodo.strftime('%Y-%m-%d'),
        'jornadas': jornadas,
        'detalle_jornada': detalle_jornada,
        'inicio_periodo': inicio_periodo,
        'fin_periodo': fin_periodo,
        'fecha_resumen': fecha_resumen,
        'nombre_periodo': nombres_periodo.get(
            tipo_periodo,
            'Diario',
        ),
        'total_apertura': total_apertura,
        'total_ingresos': total_ingresos,
        'total_egresos': total_egresos,
        'saldo_neto': total_apertura + total_ingresos - total_egresos,
        'total_diferencia': total_diferencia,
        'grafico_fechas': grafico_fechas,
        'grafico_ingresos': grafico_ingresos,
        'grafico_egresos': grafico_egresos,
        'grafico_saldos': grafico_saldos,
        'grafico_estados': grafico_estados,
    }
    return render(request, 'reportes/inicio.html', contexto)
