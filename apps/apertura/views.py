from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from .models import CajaDiaria


def url_resumen_apertura():
    return f"{reverse('apertura:inicio')}#resumen-apertura"


@login_required
def inicio(request):
    hoy = timezone.localdate()
    hora_actual = timezone.localtime().strftime('%H:%M')
    caja_hoy = CajaDiaria.objects.filter(
        usuario=request.user,
        fecha_caja=hoy,
    ).first()

    if request.method == 'POST' and caja_hoy:
        monto_texto = request.POST.get('monto_inicial', '0').strip()

        try:
            monto_inicial = Decimal(monto_texto)
        except InvalidOperation:
            return redirect(url_resumen_apertura())
        else:
            if monto_inicial < 0:
                return redirect(url_resumen_apertura())
            else:
                caja_hoy.monto_inicial = monto_inicial
                caja_hoy.save(update_fields=['monto_inicial'])
                return redirect(url_resumen_apertura())

    contexto = {
        'caja_hoy': caja_hoy,
        'fecha_hoy': hoy,
        'hora_actual': hora_actual,
    }
    return render(request, 'apertura/inicio.html', contexto)


@login_required
def abrir_caja(request):
    hoy = timezone.localdate()
    caja_hoy = CajaDiaria.objects.filter(
        usuario=request.user,
        fecha_caja=hoy,
    ).first()

    if caja_hoy:
        return redirect('apertura:inicio')

    if request.method == 'POST':
        monto_texto = request.POST.get('monto_inicial', '0').strip()
        observacion = request.POST.get('observacion', '').strip()

        try:
            monto_inicial = Decimal(monto_texto)
        except InvalidOperation:
            return redirect('apertura:abrir_caja')

        if monto_inicial < 0:
            return redirect('apertura:abrir_caja')

        hora_actual = timezone.localtime().time().replace(microsecond=0)

        CajaDiaria.objects.create(
            usuario=request.user,
            fecha_caja=hoy,
            hora_apertura=hora_actual,
            monto_inicial=monto_inicial,
            estado_caja='ABIERTA',
            observacion=observacion or None,
        )

        return redirect(url_resumen_apertura())

    contexto = {
        'fecha_hoy': hoy,
        'hora_actual': timezone.localtime().time().strftime('%H:%M'),
    }
    return render(request, 'apertura/abrir_caja.html', contexto)
