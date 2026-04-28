from configuracion.monedas import MONEDA_PREDETERMINADA, obtener_detalle_moneda
from configuracion.models import Configuracion


def moneda_actual(request):
    codigo = MONEDA_PREDETERMINADA

    user = getattr(request, 'user', None)
    if user and user.is_authenticated:
        try:
            codigo = user.configuracion.moneda or MONEDA_PREDETERMINADA
        except Configuracion.DoesNotExist:
            codigo = MONEDA_PREDETERMINADA

    detalle = obtener_detalle_moneda(codigo)
    return {
        'app_currency_code': codigo,
        'app_currency_name': detalle['nombre'],
        'app_currency_symbol': detalle['simbolo'],
    }
