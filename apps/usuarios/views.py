from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import Usuario
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def cerrar_sesion(request):
    logout(request)
    return redirect('usuarios:login')

def iniciar_sesion(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        clave = request.POST.get('password')
        
        try:
            usuario_obj = Usuario.objects.get(correo=correo)
            usuario = authenticate(request, username=correo, password=clave)
            if usuario:
                login(request, usuario)
                return redirect('apertura:inicio')
            else:
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

        usuario = Usuario.objects.create_user(
            correo=datos.get('correo'),
            password=datos.get('password'),
            nombre=datos.get('nombre'),
            apellido=datos.get('apellido'),
            telefono=datos.get('telefono')
        )
        messages.success(request, '¡Su registro fue un éxito! Por favor, vuelva a iniciar sesión.')
        return redirect('usuarios:login')
    return render(request, 'usuarios/registro.html')

def olvido_password(request):
    if request.method == 'POST':
        messages.success(request, 'Si el correo existe, recibirá un enlace pronto.')
    return render(request, 'usuarios/olvido_password.html')

def restablecer_password(request):
    if request.method == 'POST':
        messages.success(request, 'Su contraseña ha sido actualizada.')

