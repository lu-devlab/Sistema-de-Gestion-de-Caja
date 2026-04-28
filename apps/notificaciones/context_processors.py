from .models import Notificacion


def contador_notificaciones(request):
    cantidad = 0

    user = getattr(request, 'user', None)
    if user and user.is_authenticated:
        cantidad = Notificacion.objects.filter(usuario=user, leida=False).count()

    return {
        'app_notifications_unread_count': cantidad,
        'app_notifications_unread_display': '99+' if cantidad > 99 else str(cantidad),
    }
