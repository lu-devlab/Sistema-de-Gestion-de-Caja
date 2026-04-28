from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from usuarios.models import Usuario

@login_required(login_url='usuarios:login')
def perfil(request):
    if request.method == 'POST':
        user = request.user
        nuevo_nombre = request.POST.get('nombre')
        nuevo_apellido = request.POST.get('apellido')
        nuevo_dni = request.POST.get('dni')
        nuevo_telefono = request.POST.get('telefono')
        nuevo_correo = request.POST.get('correo')
        
        # Validación de correo único
        if nuevo_correo and nuevo_correo != user.correo:
            if Usuario.objects.filter(correo=nuevo_correo).exists():
                messages.error(request, 'El correo electrónico ya está en uso.')
                return render(request, 'configuracion/perfil.html', {'active_module': 'configuracion'})

        user.nombre = nuevo_nombre or user.nombre
        user.apellido = nuevo_apellido or user.apellido
        
        if nuevo_dni is not None:
            user.dni = nuevo_dni
        if nuevo_telefono is not None:
            user.telefono = nuevo_telefono
            
        nueva_contrasena = request.POST.get('nueva_contrasena')
        repetir_contrasena = request.POST.get('repetir_contrasena')
        
        if nueva_contrasena:
            if nueva_contrasena != repetir_contrasena:
                messages.error(request, 'Las contraseñas no coinciden.')
                return render(request, 'configuracion/perfil.html', {'active_module': 'configuracion'})
            user.set_password(nueva_contrasena)
            
        user.correo = nuevo_correo or user.correo
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
            messages.success(request, 'Fotografía actualizada correctamente.')
            return redirect('configuracion:foto')
        else:
            messages.error(request, 'No se seleccionó ninguna imagen.')
            
    return render(request, 'configuracion/foto.html', {'active_module': 'configuracion'})
