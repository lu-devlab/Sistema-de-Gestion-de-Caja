from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from apertura.models import CajaDiaria
from configuracion.models import Configuracion

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


def obtener_caja_abierta(usuario, fecha_hoy):
    return CajaDiaria.objects.filter(
        usuario=usuario,
        fecha_caja=fecha_hoy,
        estado_caja='ABIERTA',
    ).first()


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


@login_required
def inicio(request):
    hoy = timezone.localdate()
    hora_actual = timezone.localtime().strftime('%H:%M')
    caja_hoy = obtener_caja_abierta(request.user, hoy)
    configuracion = obtener_configuracion(request.user)
    movimiento_editar = None

    permite_editar = True
    permite_eliminar = True

    if configuracion:
        permite_editar = configuracion.permitir_edicion_movimientos
        permite_eliminar = configuracion.permitir_eliminacion_movimientos

    editar_id = request.GET.get('editar', '').strip()

    if editar_id:
        movimiento_editar = get_object_or_404(
            MovimientoCaja,
            id_movimiento=editar_id,
            usuario=request.user,
        )

    if request.method == 'POST':
        accion = request.POST.get('accion', 'registrar')

        if not caja_hoy:
            return redirect('movimientos:inicio')

        if accion == 'registrar':
            return registrar_movimiento(request, caja_hoy)

        if accion == 'editar':
            return editar_movimiento(request, permite_editar)

        if accion == 'eliminar':
            return eliminar_movimiento(request, permite_eliminar)

    movimientos_hoy = MovimientoCaja.objects.filter(
        usuario=request.user,
        fecha_movimiento=hoy,
    ).order_by('-hora_movimiento', '-id_movimiento')

    total_ingresos = Decimal('0.00')
    total_egresos = Decimal('0.00')
    total_efectivo = Decimal('0.00')
    total_digital = Decimal('0.00')

    for movimiento in movimientos_hoy:
        if movimiento.tipo_movimiento == 'INGRESO':
            total_ingresos += movimiento.monto
        else:
            total_egresos += movimiento.monto

        if movimiento.medio_pago == 'EFECTIVO':
            total_efectivo += movimiento.monto
        else:
            total_digital += movimiento.monto

    contexto = {
        'caja_hoy': caja_hoy,
        'fecha_hoy': hoy,
        'hora_actual': hora_actual,
        'movimientos_hoy': movimientos_hoy,
        'movimiento_editar': movimiento_editar,
        'permite_editar': permite_editar,
        'permite_eliminar': permite_eliminar,
        'medios_pago': MEDIOS_PAGO,
        'total_ingresos': total_ingresos,
        'total_egresos': total_egresos,
        'saldo_movimientos': total_ingresos - total_egresos,
        'total_efectivo': total_efectivo,
        'total_digital': total_digital,
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


def editar_movimiento(request, permite_editar):
    if not permite_editar:
        return redirect('movimientos:inicio')

    movimiento = get_object_or_404(
        MovimientoCaja,
        id_movimiento=request.POST.get('id_movimiento'),
        usuario=request.user,
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


def eliminar_movimiento(request, permite_eliminar):
    if not permite_eliminar:
        return redirect('movimientos:inicio')

    movimiento = get_object_or_404(
        MovimientoCaja,
        id_movimiento=request.POST.get('id_movimiento'),
        usuario=request.user,
    )
    movimiento.delete()

    return redirect('movimientos:inicio')
