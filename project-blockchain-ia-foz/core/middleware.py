from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils.deprecation import MiddlewareMixin
from django.contrib import messages


class AdminAccessMiddleware(MiddlewareMixin):
    """
    Middleware para restringir el acceso al panel de administración solo a superusuarios.
    """
    
    def process_request(self, request):
        # Verificar si la URL es del admin
        if request.path.startswith('/admin/'):
            # Permitir acceso a la página de login del admin
            if request.path == '/admin/login/':
                return None
                
            # Si no está autenticado, redirigir al login
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Si está autenticado pero no es superusuario, denegar acceso
            if not request.user.is_superuser:
                messages.error(request, 'No tienes permisos para acceder al panel de administración.')
                return redirect('core:admin_access_denied')
        
        return None
