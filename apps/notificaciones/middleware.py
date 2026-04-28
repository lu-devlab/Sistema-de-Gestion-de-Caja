from .services import sincronizar_notificaciones_usuario


class NotificacionesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)

        if user and user.is_authenticated:
            sincronizar_notificaciones_usuario(user)

        return self.get_response(request)
