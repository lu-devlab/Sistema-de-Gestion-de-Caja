"""
URL configuration for config project.

The 'urlpatterns' list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.templatetags.static import static as static_url
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('favicon.ico', RedirectView.as_view(url=static_url('favicon.svg'), permanent=False)),
    path('', RedirectView.as_view(url='/entrar/')),
    path('', include('usuarios.urls')),
    path('notificaciones/', include('notificaciones.urls')),
    path('configuracion/', include('configuracion.urls')),
    path('caja/', include('apertura.urls')),
    path('caja/', include('movimientos.urls')),
    path('caja/', include('cierre.urls')),
    path('caja/', include('historial.urls')),
    path('caja/', include('reportes.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
