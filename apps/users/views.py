# imports
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User, Group
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth import login
from django.db.models import Q

from .forms import BuscarPacienteForm, PacienteForm, PacienteRegistroForm, ProfesionalForm, ProfesionalRegistroForm
from .models import Paciente, Profesional
from apps.blockchain.models import BlockchainHash

def is_superuser(user):
    return user.is_superuser

# Restricción: solo admin puede acceder
def admin_required(user):
    # Allow staff/superuser or users linked to a Profesional profile
    try:
        is_profesional = hasattr(user, 'profesional') and user.profesional is not None
    except Exception:
        is_profesional = False
    return user.is_staff or user.is_superuser or is_profesional

@user_passes_test(admin_required)
def user_list(request):
    # Mostrar solo los pacientes (relacionados con User)
    pacientes = Paciente.objects.select_related('user').all()
    return render(request, "blockchain/pacientes/lista_pacientes.html", {"pacientes": pacientes})

@login_required
def perfil_paciente(request, paciente_id=None):
    """Vista del perfil completo de un paciente.

    - Si `paciente_id` está presente se intenta ver el perfil indicado.
      Solo administradores/staff pueden ver cualquier perfil; los usuarios
      normales solo pueden ver su propio perfil.
    - Si `paciente_id` es None, asumimos que el usuario quiere ver su propio perfil.
    """
    if paciente_id:
        paciente = get_object_or_404(Paciente, id=paciente_id)
        # autorización: admin/staff (usando admin_required) o propietario
        is_owner = getattr(request.user, 'paciente', None) and request.user.paciente.id == paciente.id
        if not is_owner:
            # Check if verified via session
            session_key = f'verified_paciente_{paciente.id}'
            if not request.session.get(session_key, False):
                if request.method == 'POST' and 'password' in request.POST:
                    password = request.POST['password']
                    first_hash = BlockchainHash.objects.filter(content_type='Patient', object_id=paciente.id).order_by('timestamp').first()
                    if first_hash and first_hash.hash_value == password:
                        request.session[session_key] = True
                    else:
                        messages.error(request, 'Clave incorrecta.')
                        return render(request, 'blockchain/pacientes/perfil_paciente_password.html', {'paciente': paciente})
                else:
                    return render(request, 'blockchain/pacientes/perfil_paciente_password.html', {'paciente': paciente})
        es_propio_perfil = bool(is_owner)
    else:
        # El paciente está viendo su propio perfil
        try:
            paciente = request.user.paciente
            es_propio_perfil = True
        except Paciente.DoesNotExist:
            messages.error(request, 'No tienes un perfil de paciente asociado.')
            return redirect('core:index')

    context = {
        'paciente': paciente,
        'es_propio_perfil': es_propio_perfil,
        # Pasar relaciones para que la plantilla muestre registros médicos
        'alergias': paciente.alergias.all(),
        'condiciones': paciente.condiciones.all() if hasattr(paciente, 'condiciones') else [],
        'tratamientos': paciente.tratamientos.all() if hasattr(paciente, 'tratamientos') else [],
        'pruebas': paciente.pruebas.all() if hasattr(paciente, 'pruebas') else [],
        'cirugias': paciente.cirugias.all() if hasattr(paciente, 'cirugias') else [],
        # Primer hash del paciente (solo para el propietario)
        'primer_hash': BlockchainHash.objects.filter(content_type='Patient', object_id=paciente.id).order_by('timestamp').first() if es_propio_perfil else None,
    }
    return render(request, 'blockchain/pacientes/perfil_paciente.html', context)

# @user_passes_test(is_superuser)
# def user_delete(request, user_id):
#     user = get_object_or_404(User, pk=user_id)
#     user.delete()
#     return redirect("users:user_list")


@login_required
def panel_profesional(request):
    """Vista principal del panel del profesional"""
    try:
        profesional = request.user.profesional
    except Profesional.DoesNotExist:
        messages.error(request, 'No tienes un perfil de profesional asociado.')
        return redirect('core:index')
    
    # Pacientes recientes
    pacientes_recientes = Paciente.objects.all()[:5]
    
    context = {
        'profesional': profesional,
        'pacientes_recientes': pacientes_recientes,
    }
    
    return render(request, 'blockchain/profesional/panel_profesional.html', context)

@login_required
def buscar_pacientes(request):
    """Vista para buscar pacientes (solo para profesionales)"""
    try:
        profesional = request.user.profesional
    except Profesional.DoesNotExist:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('core:index')
    
    form = BuscarPacienteForm(request.GET or None)
    pacientes = []
    
    if form.is_valid():
        cedula = form.cleaned_data.get('cedula')
        nombre = form.cleaned_data.get('nombre')
        
        query = Q()
        if cedula:
            query |= Q(cedula__icontains=cedula)
        if nombre:
            query |= Q(user__first_name__icontains=nombre) | Q(user__last_name__icontains=nombre)
        
        if query:
            pacientes = Paciente.objects.filter(query)
    
    context = {
        'form': form,
        'pacientes': pacientes,
        'profesional': profesional,
    }
    
    return render(request, 'blockchain/pacientes/buscar_pacientes.html', context)

# Vistas de registro
def registro_paciente(request):
    """Registro de nuevo paciente"""
    if request.method == 'POST':
        user_form = PacienteRegistroForm(request.POST)
        paciente_form = PacienteForm(request.POST)
        
        if user_form.is_valid() and paciente_form.is_valid():
            # Crear el usuario
            user = user_form.save()
            
            # Crear el paciente asociado al usuario
            paciente = paciente_form.save(commit=False)
            paciente.user = user
            paciente.save()
            
            login(request, user)
            messages.success(request, '¡Registro exitoso! Bienvenido al sistema.')
            return redirect('core:index')
    else:
        user_form = PacienteRegistroForm()
        paciente_form = PacienteForm()
    
    return render(request, 'registration/registro_paciente.html', {
        'user_form': user_form,
        'paciente_form': paciente_form
    })

@user_passes_test(is_superuser)
def registro_profesional(request):
    """Registro de nuevo profesional - Solo accesible para superadmin"""
    if request.method == 'POST':
        user_form = ProfesionalRegistroForm(request.POST)
        profesional_form = ProfesionalForm(request.POST)
        
        if user_form.is_valid() and profesional_form.is_valid():
            # Crear el usuario
            user = user_form.save()
            
            # Asignar al grupo de profesionales
            profesional_group, created = Group.objects.get_or_create(name='Profesionales')
            user.groups.add(profesional_group)
            
            # Crear el profesional asociado al usuario
            profesional = profesional_form.save(commit=False)
            profesional.user = user
            profesional.save()
            
            messages.success(request, 'Profesional registrado exitosamente por el administrador.')
            return redirect('blockchain:dashboard')  # Redirigir al dashboard de admin
    else:
        user_form = ProfesionalRegistroForm()
        profesional_form = ProfesionalForm()
    
    return render(request, 'registration/registro_profesional.html', {
        'user_form': user_form,
        'profesional_form': profesional_form
    })
