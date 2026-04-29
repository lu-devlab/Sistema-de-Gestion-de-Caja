from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core import signing
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.urls import reverse

from .models import Usuario


RESET_PASSWORD_TOKEN_SALT = 'usuarios.restablecer_password'
RESET_PASSWORD_TOKEN_MAX_AGE = 900


def generar_token_restablecimiento(usuario):
    return signing.dumps(
        {
            'user_id': usuario.pk,
            'correo': usuario.correo,
        },
        salt=RESET_PASSWORD_TOKEN_SALT,
    )


def obtener_usuario_por_token(token):
    if not token:
        return None

    try:
        data = signing.loads(
            token,
            salt=RESET_PASSWORD_TOKEN_SALT,
            max_age=RESET_PASSWORD_TOKEN_MAX_AGE,
        )
    except signing.BadSignature:
        return None

    return Usuario.objects.filter(
        pk=data.get('user_id'),
        correo=data.get('correo'),
    ).first()


def cerrar_sesion(request):
    logout(request)
    return redirect('usuarios:login')


def iniciar_sesion(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        clave = request.POST.get('password')

        try:
            Usuario.objects.get(correo=correo)
            usuario = authenticate(request, username=correo, password=clave)
            if usuario:
                login(request, usuario)
                return redirect('apertura:inicio')

            messages.error(request, 'Contraseña incorrecta.')
        except Usuario.DoesNotExist:
            messages.error(request, 'El correo no existe.')

    return render(request, 'usuarios/login.html')


def registrar_usuario(request):
    if request.method == 'POST':
        datos = request.POST
        if datos.get('password') != datos.get('confirmar_password'):
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'usuarios/registro.html')

        if len(datos.get('password')) < 6:
            messages.error(request, 'La contraseña debe tener al menos 6 caracteres.')
            return render(request, 'usuarios/registro.html')

        if datos.get('telefono') and len(datos.get('telefono')) != 9:
            messages.error(request, 'El teléfono debe tener 9 dígitos.')
            return render(request, 'usuarios/registro.html')

        if Usuario.objects.filter(correo=datos.get('correo')).exists():
            messages.error(request, 'El correo ya está registrado.')
            return render(request, 'usuarios/registro.html')

        Usuario.objects.create_user(
            correo=datos.get('correo'),
            password=datos.get('password'),
            nombre=datos.get('nombre'),
            apellido=datos.get('apellido'),
            telefono=datos.get('telefono'),
        )
        messages.success(request, 'Tu registro fue exitoso. Vuelve a iniciar sesión.')
        return redirect('usuarios:login')

    return render(request, 'usuarios/registro.html')


def olvido_password(request):
    if request.method == 'POST':
        correo = request.POST.get('correo', '').strip()
        usuario = Usuario.objects.filter(correo__iexact=correo).first()

        if not usuario:
            messages.error(request, 'No encontramos una cuenta con ese correo.')
            return render(request, 'usuarios/olvido_password.html')

        token = generar_token_restablecimiento(usuario)
        messages.success(request, 'Ahora puedes definir una nueva contraseña.')
        return redirect(f"{reverse('usuarios:restablecer_password')}?token={token}")

    return render(request, 'usuarios/olvido_password.html')


def restablecer_password(request):
    token = request.POST.get('token') or request.GET.get('token', '')
    usuario = obtener_usuario_por_token(token)

    if not usuario:
        messages.error(request, 'El enlace de recuperación no es válido o ya venció.')
        return redirect('usuarios:olvido_password')

    if request.method == 'POST':
        nueva_password = request.POST.get('nueva_password', '')
        confirmar_password = request.POST.get('confirmar_password', '')

        if nueva_password != confirmar_password:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(
                request,
                'usuarios/restablecer_password.html',
                {'token': token},
            )

        try:
            validate_password(nueva_password, usuario)
        except ValidationError as error:
            messages.error(request, error.messages[0])
            return render(
                request,
                'usuarios/restablecer_password.html',
                {'token': token},
            )

        usuario.set_password(nueva_password)
        usuario.save(update_fields=['password'])
        messages.success(request, 'Tu contraseña ha sido actualizada.')
        return redirect('usuarios:login')

    return render(
        request,
        'usuarios/restablecer_password.html',
        {'token': token},
    )
