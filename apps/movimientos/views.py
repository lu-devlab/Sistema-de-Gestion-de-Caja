from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from apertura.models import CajaDiaria
from configuracion.models import Configuracion

from .calculos import obtener_totales_caja
from .models import CategoriaMovimiento, MovimientoCaja

MEDIOS_PAGO = [
    'EFECTIVO',
    'YAPE',
    'PLIN',
    'TRANSFERENCIA',
    'OTRO',
]


def obtener_configuracion(usuario):
    return Configuracion.objects.filter(usuario=usuario).first()


def obtener_caja_dia(usuario, fecha_hoy):
    return CajaDiaria.objects.filter(
        usuario=usuario,
        fecha_caja=fecha_hoy,
    ).first()


def obtener_estado_caja(caja):
    if not caja:
        return ''
    return (caja.estado_caja or '').strip().upper()


def caja_esta_abierta(caja):
    return obtener_estado_caja(caja) == 'ABIERTA'


def caja_esta_cerrada(caja):
    return obtener_estado_caja(caja) == 'CERRADA'


def obtener_categoria(tipo_movimiento):
    nombre = 'Ingreso general'
    if tipo_movimiento == 'EGRESO':
        nombre = 'Egreso general'

    categoria, _ = CategoriaMovimiento.objects.get_or_create(
        nombre_categoria=nombre,
        tipo_categoria=tipo_movimiento,
        defaults={'descripcion': nombre},
    )
    return categoria


def url_editar_movimiento(movimiento_id):
    return (
        f"{reverse('movimientos:inicio')}"
        f"?editar={movimiento_id}#form-movimiento"
    )


def calcular_saldo_disponible(caja, movimiento_omitido=None):
    saldo_disponible = obtener_totales_caja(caja)['saldo_esperado']

    if movimiento_omitido:
        if movimiento_omitido.tipo_movimiento == 'INGRESO':
            saldo_disponible -= movimiento_omitido.monto
        else:
            saldo_disponible += movimiento_omitido.monto

    return saldo_disponible


def validar_egreso_disponible(request, caja, tipo_movimiento, monto, movimiento=None):
    if tipo_movimiento != 'EGRESO':
        return True

    saldo_disponible = calcular_saldo_disponible(
        caja,
        movimiento_omitido=movimiento,
    )

    if monto <= saldo_disponible:
        return True

    messages.error(
        request,
        (
            'Ojo: estas registrando un egreso mayor al saldo disponible. '
            f'Disponible: {saldo_disponible:.2f}. No se registro el movimiento.'
        ),
    )
    return False


@login_required
def inicio(request):
    hoy = timezone.localdate()
    hora_actual = timezone.localtime().strftime('%H:%M')
    caja_dia = obtener_caja_dia(request.user, hoy)
    caja_hoy = caja_dia if caja_esta_abierta(caja_dia) else None
    caja_cerrada = caja_esta_cerrada(caja_dia)
    configuracion = obtener_configuracion(request.user)
    movimiento_editar = None

    permite_editar = True
    permite_eliminar = True

    if configuracion:
        permite_editar = configuracion.permitir_edicion_movimientos
        permite_eliminar = configuracion.permitir_eliminacion_movimientos

    editar_id = request.GET.get('editar', '').strip()

    if editar_id and caja_hoy:
        movimiento_editar = get_object_or_404(
            MovimientoCaja,
            id_movimiento=editar_id,
            usuario=request.user,
            caja=caja_hoy,
        )

    if request.method == 'POST':
        accion = request.POST.get('accion', 'registrar')

        if not caja_hoy:
            if caja_cerrada:
                messages.error(
                    request,
                    'La caja del dia ya esta cerrada. No se pueden registrar movimientos.',
                )
            else:
                messages.error(
                    request,
                    'Primero debe abrir la caja para registrar movimientos',
                )
            return redirect('movimientos:inicio')

        if accion == 'registrar':
            return registrar_movimiento(request, caja_hoy)

        if accion == 'editar':
            return editar_movimiento(request, permite_editar, caja_hoy)

        if accion == 'eliminar':
            return eliminar_movimiento(request, permite_eliminar, caja_hoy)

    total_ingresos = Decimal('0.00')
    total_egresos = Decimal('0.00')
    saldo_efectivo = Decimal('0.00')
    saldo_digital = Decimal('0.00')
    movimiento_efectivo = Decimal('0.00')
    movimiento_digital = Decimal('0.00')
    saldo_movimientos = Decimal('0.00')
    saldo_total = Decimal('0.00')
    saldo_disponible_form = Decimal('0.00')

    if caja_dia:
        totales = obtener_totales_caja(
            caja_dia,
            incluir_movimientos=True,
            ordenar=True,
        )
        movimientos_hoy = totales['movimientos']
        total_ingresos = totales['total_ingresos']
        total_egresos = totales['total_egresos']
        saldo_efectivo = totales['saldo_efectivo_esperado']
        saldo_digital = totales['saldo_digital_esperado']
        movimiento_efectivo = totales['movimiento_efectivo']
        movimiento_digital = totales['movimiento_digital']
        saldo_movimientos = totales['saldo_movimientos']
        saldo_total = totales['saldo_esperado']
        saldo_disponible_form = saldo_total
    else:
        movimientos_hoy = MovimientoCaja.objects.none()

    if caja_dia and movimiento_editar:
        saldo_disponible_form = calcular_saldo_disponible(
            caja_dia,
            movimiento_omitido=movimiento_editar,
        )

    contexto = {
        'caja_hoy': caja_hoy,
        'caja_dia': caja_dia,
        'caja_cerrada': caja_cerrada,
        'fecha_hoy': hoy,
        'hora_actual': hora_actual,
        'movimientos_hoy': movimientos_hoy,
        'movimiento_editar': movimiento_editar,
        'permite_editar': permite_editar,
        'permite_eliminar': permite_eliminar,
        'medios_pago': MEDIOS_PAGO,
        'total_ingresos': total_ingresos,
        'total_egresos': total_egresos,
        'saldo_movimientos': saldo_movimientos,
        'saldo_total': saldo_total,
        'saldo_disponible_form': saldo_disponible_form,
        'total_efectivo': saldo_efectivo,
        'total_digital': saldo_digital,
        'movimiento_efectivo': movimiento_efectivo,
        'movimiento_digital': movimiento_digital,
    }
    return render(request, 'movimientos/inicio.html', contexto)


def registrar_movimiento(request, caja_hoy):
    tipo_movimiento = request.POST.get('tipo_movimiento', '').strip()
    medio_pago = request.POST.get('medio_pago', '').strip()
    descripcion = request.POST.get('descripcion', '').strip()
    monto_texto = request.POST.get('monto', '0').strip()

    if tipo_movimiento not in ['INGRESO', 'EGRESO']:
        return redirect('movimientos:inicio')

    if medio_pago not in MEDIOS_PAGO:
        return redirect('movimientos:inicio')

    if not descripcion:
        return redirect('movimientos:inicio')

    try:
        monto = Decimal(monto_texto)
    except InvalidOperation:
        return redirect('movimientos:inicio')

    if monto <= 0:
        return redirect('movimientos:inicio')

    if not validar_egreso_disponible(
        request,
        caja_hoy,
        tipo_movimiento,
        monto,
    ):
        return redirect('movimientos:inicio')

    ahora = timezone.localtime()
    categoria = obtener_categoria(tipo_movimiento)

    MovimientoCaja.objects.create(
        caja=caja_hoy,
        categoria=categoria,
        usuario=request.user,
        tipo_movimiento=tipo_movimiento,
        medio_pago=medio_pago,
        monto=monto,
        descripcion=descripcion,
        fecha_movimiento=ahora.date(),
        hora_movimiento=ahora.time().replace(microsecond=0),
    )

    return redirect('movimientos:inicio')


def editar_movimiento(request, permite_editar, caja_hoy):
    if not permite_editar:
        return redirect('movimientos:inicio')

    movimiento = get_object_or_404(
        MovimientoCaja,
        id_movimiento=request.POST.get('id_movimiento'),
        usuario=request.user,
        caja=caja_hoy,
    )

    tipo_movimiento = request.POST.get('tipo_movimiento', '').strip()
    medio_pago = request.POST.get('medio_pago', '').strip()
    descripcion = request.POST.get('descripcion', '').strip()
    monto_texto = request.POST.get('monto', '0').strip()

    if tipo_movimiento not in ['INGRESO', 'EGRESO']:
        return redirect(url_editar_movimiento(movimiento.id_movimiento))

    if medio_pago not in MEDIOS_PAGO:
        return redirect(url_editar_movimiento(movimiento.id_movimiento))

    if not descripcion:
        return redirect(url_editar_movimiento(movimiento.id_movimiento))

    try:
        monto = Decimal(monto_texto)
    except InvalidOperation:
        return redirect(url_editar_movimiento(movimiento.id_movimiento))

    if monto <= 0:
        return redirect(url_editar_movimiento(movimiento.id_movimiento))

    if not validar_egreso_disponible(
        request,
        caja_hoy,
        tipo_movimiento,
        monto,
        movimiento=movimiento,
    ):
        return redirect(url_editar_movimiento(movimiento.id_movimiento))

    movimiento.tipo_movimiento = tipo_movimiento
    movimiento.categoria = obtener_categoria(tipo_movimiento)
    movimiento.medio_pago = medio_pago
    movimiento.descripcion = descripcion
    movimiento.monto = monto
    movimiento.save(
        update_fields=[
            'tipo_movimiento',
            'categoria',
            'medio_pago',
            'descripcion',
            'monto',
        ]
    )

    return redirect('movimientos:inicio')


def eliminar_movimiento(request, permite_eliminar, caja_hoy):
    if not permite_eliminar:
        return redirect('movimientos:inicio')

    movimiento = get_object_or_404(
        MovimientoCaja,
        id_movimiento=request.POST.get('id_movimiento'),
        usuario=request.user,
        caja=caja_hoy,
    )
    movimiento.delete()

    return redirect('movimientos:inicio')
