MONEDAS_DISPONIBLES = [
    ('PEN', 'Sol peruano (PEN)'),
    ('COP', 'Peso colombiano (COP)'),
    ('USD', 'Dolar estadounidense (USD)'),
    ('EUR', 'Euro (EUR)'),
    ('MXN', 'Peso mexicano (MXN)'),
]

MONEDAS_CONFIG = {
    'PEN': {
        'nombre': 'Sol peruano',
        'simbolo': 'S/',
    },
    'COP': {
        'nombre': 'Peso colombiano',
        'simbolo': 'COP $',
    },
    'USD': {
        'nombre': 'Dolar estadounidense',
        'simbolo': 'US$',
    },
    'EUR': {
        'nombre': 'Euro',
        'simbolo': 'EUR',
    },
    'MXN': {
        'nombre': 'Peso mexicano',
        'simbolo': 'MX$',
    },
}

MONEDA_PREDETERMINADA = 'PEN'


def obtener_detalle_moneda(codigo):
    codigo_normalizado = (codigo or MONEDA_PREDETERMINADA).upper()
    return MONEDAS_CONFIG.get(
        codigo_normalizado,
        MONEDAS_CONFIG[MONEDA_PREDETERMINADA],
    )
