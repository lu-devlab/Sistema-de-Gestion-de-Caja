from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render

from configuracion.monedas import MONEDAS_DISPONIBLES
from configuracion.models import Configuracion
from usuarios.models import Usuario


def obtener_o_crear_configuracion(usuario):
    responsable = f'{usuario.nombre} {usuario.apellido}'.strip() or usuario.correo
    return Configuracion.objects.get_or_create(
        usuario=usuario,
        defaults={
            'nombre_negocio': 'Mi negocio',
            'responsable': responsable,
        },
    )


@login_required(login_url='usuarios:login')
def perfil(request):
    if request.method == 'POST':
        user = request.user
        user.nombre = request.POST.get('nombre', '').strip() or user.nombre
        user.apellido = request.POST.get('apellido', '').strip() or user.apellido
        user.dni = request.POST.get('dni', '').strip()
        user.telefono = request.POST.get('telefono', '').strip()
        user.save()

        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('configuracion:perfil')

    return render(request, 'configuracion/perfil.html', {'active_module': 'configuracion'})


@login_required(login_url='usuarios:login')
def gestionar_foto(request):
    if request.method == 'POST':
        if 'foto_perfil' in request.FILES:
            user = request.user
            user.foto_perfil = request.FILES['foto_perfil']
            user.save()
            messages.success(request, 'Fotografia actualizada correctamente.')
            return redirect('configuracion:foto')

        messages.error(request, 'No se selecciono ninguna imagen.')

    return render(request, 'configuracion/foto.html', {'active_module': 'configuracion'})


@login_required(login_url='usuarios:login')
def moneda(request):
    configuracion, _ = obtener_o_crear_configuracion(request.user)
    monedas_validas = {codigo for codigo, _ in MONEDAS_DISPONIBLES}

    if request.method == 'POST':
        nueva_moneda = request.POST.get('moneda', '').strip().upper()

        if nueva_moneda not in monedas_validas:
            messages.error(request, 'Selecciona una moneda valida.')
        else:
            configuracion.moneda = nueva_moneda
            configuracion.save(update_fields=['moneda'])
            messages.success(request, 'Moneda actualizada correctamente.')
            return redirect('configuracion:moneda')

    contexto = {
        'active_module': 'configuracion',
        'configuracion': configuracion,
        'monedas_disponibles': MONEDAS_DISPONIBLES,
    }
    return render(request, 'configuracion/moneda.html', contexto)


@login_required(login_url='usuarios:login')
def acceso_cuenta(request):
    if request.method == 'POST':
        user = request.user
        nuevo_correo = Usuario.objects.normalize_email(
            request.POST.get('correo', '').strip()
        )
        password_actual = request.POST.get('password_actual', '').strip()
        nueva_contrasena = request.POST.get('nueva_contrasena', '').strip()
        repetir_contrasena = request.POST.get('repetir_contrasena', '').strip()

        cambios = False
        cambio_password = False

        if nuevo_correo and nuevo_correo != user.correo:
            correo_en_uso = Usuario.objects.filter(correo=nuevo_correo).exclude(
                pk=user.pk
            )
            if correo_en_uso.exists():
                messages.error(request, 'El correo electronico ya esta en uso.')
                return render(
                    request,
                    'configuracion/acceso.html',
                    {'active_module': 'configuracion'},
                )

            user.correo = nuevo_correo
            cambios = True

        if password_actual or nueva_contrasena or repetir_contrasena:
            if not password_actual:
                messages.error(request, 'Debes ingresar tu contrasena actual.')
                return render(
                    request,
                    'configuracion/acceso.html',
                    {'active_module': 'configuracion'},
                )

            if not user.check_password(password_actual):
                messages.error(request, 'La contrasena actual es incorrecta.')
                return render(
                    request,
                    'configuracion/acceso.html',
                    {'active_module': 'configuracion'},
                )

            if not nueva_contrasena or not repetir_contrasena:
                messages.error(request, 'Completa la nueva contrasena y su confirmacion.')
                return render(
                    request,
                    'configuracion/acceso.html',
                    {'active_module': 'configuracion'},
                )

            if nueva_contrasena != repetir_contrasena:
                messages.error(request, 'Las contrasenas no coinciden.')
                return render(
                    request,
                    'configuracion/acceso.html',
                    {'active_module': 'configuracion'},
                )

            try:
                validate_password(nueva_contrasena, user=user)
            except ValidationError as error:
                messages.error(request, ' '.join(error.messages))
                return render(
                    request,
                    'configuracion/acceso.html',
                    {'active_module': 'configuracion'},
                )

            user.set_password(nueva_contrasena)
            cambios = True
            cambio_password = True

        if cambios:
            user.save()
            if cambio_password:
                update_session_auth_hash(request, user)
            messages.success(request, 'Datos de acceso actualizados correctamente.')
        else:
            messages.success(request, 'No hubo cambios para guardar.')

        return redirect('configuracion:acceso')

    return render(request, 'configuracion/acceso.html', {'active_module': 'configuracion'})
