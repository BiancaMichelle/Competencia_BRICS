from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, 'index.html')


def admin_access_denied(request):
    """Vista para mostrar acceso denegado al panel de administración."""
    messages.error(request, 'No tienes permisos para acceder al panel de administración. Solo los superusuarios pueden acceder.')
    return render(request, 'admin_access_denied.html')

