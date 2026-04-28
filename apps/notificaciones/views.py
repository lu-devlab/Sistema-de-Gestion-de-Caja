from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Notificacion
from .services import obtener_tipo_label, sincronizar_notificaciones_usuario


@login_required(login_url='usuarios:login')
def inicio(request):
    sincronizar_notificaciones_usuario(request.user)

    ids_sin_revisar = list(
        Notificacion.objects.filter(
            usuario=request.user,
            leida=False,
        ).values_list('id_notificacion', flat=True)
    )

    if ids_sin_revisar:
        Notificacion.objects.filter(
            id_notificacion__in=ids_sin_revisar,
        ).update(leida=True)

    notificaciones = list(
        Notificacion.objects.filter(
            usuario=request.user,
        ).order_by('-fecha_notificacion', '-hora_notificacion', '-id_notificacion')
    )

    for notificacion in notificaciones:
        notificacion.tipo_label = obtener_tipo_label(notificacion.tipo_notificacion)
        notificacion.recien_revisada = (
            notificacion.id_notificacion in ids_sin_revisar
        )

    contexto = {
        'active_module': 'notificaciones',
        'notificaciones': notificaciones,
        'notificaciones_revisadas_ahora': len(ids_sin_revisar),
        'total_notificaciones': len(notificaciones),
        'ultima_notificacion': notificaciones[0] if notificaciones else None,
    }
    return render(request, 'notificaciones/inicio.html', contexto)
