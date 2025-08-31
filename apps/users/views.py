# imports
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User, Group
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth import login
from django.db.models import Q

from .forms import BuscarPacienteForm, PacienteForm, PacienteRegistroForm, ProfesionalForm, ProfesionalRegistroForm, AlergiaForm, CondicionMedicaForm, TratamientoForm, PruebaLaboratorioForm, CirugiaForm
from .models import Paciente, Profesional, BlockchainHash, AccesoBlockchain, Alergia, CondicionMedica, Tratamiento, PruebaLaboratorio, Cirugia
from .blockchain_manager import BlockchainManager


def admin_index(request):
    """Vista personalizada para el index del admin con estadísticas"""
    if not request.user.is_superuser:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Acceso denegado")
    
    # Estadísticas
    total_pacientes = Paciente.objects.count()
    total_profesionales = Profesional.objects.count()
    total_hashes = BlockchainHash.objects.count() if hasattr(BlockchainHash, '_meta') else 0
    
    context = {
        'total_pacientes': total_pacientes,
        'total_profesionales': total_profesionales,
        'total_hashes': total_hashes,
    }
    
    return render(request, 'admin/index.html', context)

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
    return render(request, "users/lista_pacientes.html", {"pacientes": pacientes})

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
                    # Verificar usando los últimos 8 dígitos del hash genesis del paciente
                    try:
                        genesis_hash = BlockchainHash.objects.filter(
                            paciente=paciente,
                            categoria='genesis'
                        ).first()
                        
                        if not genesis_hash:
                            messages.error(request, 'No se encontró el hash génesis para este paciente.')
                            return redirect('users:user_list')
                        
                        if password == genesis_hash.hash_value[-8:]:
                            request.session[session_key] = True
                        else:
                            messages.error(request, 'Los últimos 8 dígitos del hash génesis son incorrectos.')
                            return render(request, 'users/perfil_paciente_password.html', {
                                'paciente': paciente,
                                'hash_parcial': genesis_hash.hash_value[:-8]
                            })
                    except Exception as e:
                        messages.error(request, f'Error al verificar hash: {str(e)}')
                        return render(request, 'users/perfil_paciente_password.html', {
                            'paciente': paciente,
                            'hash_parcial': genesis_hash.hash_value[:-8] if genesis_hash else ''
                        })
                else:
                    # Mostrar el hash parcial
                    genesis_hash = BlockchainHash.objects.filter(
                        paciente=paciente,
                        categoria='genesis'
                    ).first()
                    if not genesis_hash:
                        messages.error(request, 'No se encontró el hash génesis para este paciente.')
                        return redirect('users:user_list')
                    return render(request, 'users/perfil_paciente_password.html', {
                        'paciente': paciente,
                        'hash_parcial': genesis_hash.hash_value[:-8]
                    })
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
        'antecedentes': paciente.antecedentes.all() if hasattr(paciente, 'antecedentes') else [],
        # Hashes de blockchain organizados por categoría
        'blockchain_hashes': BlockchainManager.get_patient_hashes_by_category(paciente) if es_propio_perfil else {},
    }
    return render(request, 'users/perfil_paciente.html', context)

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
    
    # Obtener fecha actual
    from django.utils import timezone
    today = timezone.now().date()
    
    # Pacientes recientes
    pacientes_recientes = Paciente.objects.all()[:5]
    
    # Turnos de hoy
    turnos_hoy = profesional.turnos.filter(
        fecha_hora__date=today,
        estado__in=['programado', 'confirmado']
    ).select_related('paciente__user').order_by('fecha_hora')
    
    # Próximos turnos (próximos 7 días)
    from datetime import timedelta
    next_week = today + timedelta(days=7)
    turnos_proximos = profesional.turnos.filter(
        fecha_hora__date__gt=today,
        fecha_hora__date__lte=next_week,
        estado__in=['programado', 'confirmado']
    ).select_related('paciente__user').order_by('fecha_hora')[:10]
    
    context = {
        'profesional': profesional,
        'pacientes_recientes': pacientes_recientes,
        'turnos_hoy': turnos_hoy,
        'turnos_proximos': turnos_proximos,
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
            return redirect('admin:index')  # Redirigir al dashboard de admin
    else:
        user_form = ProfesionalRegistroForm()
        profesional_form = ProfesionalForm()
    
    return render(request, 'registration/registro_profesional.html', {
        'user_form': user_form,
        'profesional_form': profesional_form
    })

@login_required
def blockchain_status(request):
    """View to check blockchain integration status"""
    from .blockchain_services import MedicalBlockchainService

    service = MedicalBlockchainService()

    polygon_status = service.polygon.is_connected()
    polygon_info = service.polygon.get_network_info() if polygon_status else None

    filecoin_status = service.filecoin.is_configured()

    context = {
        'polygon_connected': polygon_status,
        'polygon_info': polygon_info,
        'filecoin_configured': filecoin_status,
    }

    return render(request, 'users/blockchain_status.html', context)


@login_required
def hash_detail(request, hash_id):
    """Vista para mostrar los detalles de un hash específico"""
    try:
        profesional = request.user.profesional
    except Profesional.DoesNotExist:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('core:index')

    # Obtener detalles del hash y registrar el acceso
    hash_details = BlockchainManager.get_hash_details(hash_id, profesional)

    if not hash_details:
        messages.error(request, 'Hash no encontrado.')
        return redirect('users:panel_profesional')

    # Obtener historial de accesos
    access_history = BlockchainManager.get_access_history(hash_details['hash_record'])

    context = {
        'hash_details': hash_details,
        'access_history': access_history,
        'profesional': profesional,
    }

    return render(request, 'users/hash_detail.html', context)


def hash_detail_by_value(request, hash_value):
    """Vista para mostrar los detalles de un hash usando el hash_value (genesis)"""
    try:
        profesional = request.user.profesional
    except Profesional.DoesNotExist:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('core:index')

    # Buscar el hash por su valor (hash_value)
    try:
        hash_record = BlockchainHash.objects.get(hash_value=hash_value)

        # Registrar el acceso
        AccesoBlockchain.objects.create(
            hash_record=hash_record,
            profesional=profesional,
            motivo_acceso="Consulta médica"
        )

        hash_details = {
            'hash_record': hash_record,
            'datos_originales': hash_record.datos_originales,
            'categoria': hash_record.get_categoria_display(),
            'fecha_creacion': hash_record.timestamp,
            'transaction_hash': hash_record.transaction_hash,
            'block_number': hash_record.block_number
        }

        # Obtener historial de accesos
        access_history = BlockchainManager.get_access_history(hash_record)

        context = {
            'hash_details': hash_details,
            'access_history': access_history,
            'profesional': profesional,
        }

        return render(request, 'users/hash_detail.html', context)

    except BlockchainHash.DoesNotExist:
        messages.error(request, 'Hash no encontrado. Verifique que el hash sea correcto.')
        return redirect('users:panel_profesional')
    except Exception as e:
        messages.error(request, f'Error al procesar el hash: {str(e)}')
        return redirect('users:panel_profesional')


@login_required
def patient_blockchain_hashes(request, paciente_id):
    """Vista para que los profesionales vean los hashes de blockchain de un paciente"""
    try:
        profesional = request.user.profesional
    except Profesional.DoesNotExist:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('core:index')

    paciente = get_object_or_404(Paciente, id=paciente_id)

    # Verificar que el profesional tenga acceso al paciente (por ahora todos los profesionales pueden ver)
    # En el futuro se puede agregar lógica de permisos más granular

    blockchain_hashes = BlockchainManager.get_patient_hashes_by_category(paciente)

    context = {
        'paciente': paciente,
        'blockchain_hashes': blockchain_hashes,
        'profesional': profesional,
    }

    return render(request, 'users/patient_blockchain_hashes.html', context)


# Vistas para ver detalles de registros médicos con registro de acceso
@login_required
def ver_alergia(request, paciente_id, alergia_id):
    """Vista para ver detalles de una alergia y registrar acceso"""
    # Verificar si el usuario es profesional o paciente propietario
    try:
        profesional = request.user.profesional
        es_profesional = True
        paciente_acceso = None
    except Profesional.DoesNotExist:
        try:
            paciente_acceso = request.user.paciente
            es_profesional = False
        except Paciente.DoesNotExist:
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('core:index')

    paciente = get_object_or_404(Paciente, id=paciente_id)
    alergia = get_object_or_404(Alergia, id=alergia_id, paciente=paciente)

    # Verificar que el paciente solo pueda ver sus propios registros
    if not es_profesional and paciente_acceso.id != paciente.id:
        messages.error(request, 'No tienes permisos para acceder a este registro.')
        return redirect('users:perfil_paciente')

    # Registrar acceso a la información médica
    BlockchainManager.registrar_acceso_medico(
        profesional=profesional if es_profesional else None,
        paciente=paciente_acceso if not es_profesional else paciente,
        tipo_registro='alergia',
        registro_id=alergia.id,
        motivo='Consulta de alergia médica por ' + ('profesional' if es_profesional else 'paciente')
    )

    context = {
        'paciente': paciente,
        'registro': alergia,
        'tipo': 'alergia',
        'es_profesional': es_profesional,
        'usuario_actual': profesional if es_profesional else paciente_acceso,
    }

    return render(request, 'users/detalle_registro_medico.html', context)


@login_required
def ver_condicion(request, paciente_id, condicion_id):
    """Vista para ver detalles de una condición médica y registrar acceso"""
    # Verificar si el usuario es profesional o paciente propietario
    try:
        profesional = request.user.profesional
        es_profesional = True
        paciente_acceso = None
    except Profesional.DoesNotExist:
        try:
            paciente_acceso = request.user.paciente
            es_profesional = False
        except Paciente.DoesNotExist:
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('core:index')

    paciente = get_object_or_404(Paciente, id=paciente_id)
    condicion = get_object_or_404(CondicionMedica, id=condicion_id, paciente=paciente)

    # Verificar que el paciente solo pueda ver sus propios registros
    if not es_profesional and paciente_acceso.id != paciente.id:
        messages.error(request, 'No tienes permisos para acceder a este registro.')
        return redirect('users:perfil_paciente')

    # Registrar acceso a la información médica
    BlockchainManager.registrar_acceso_medico(
        profesional=profesional if es_profesional else None,
        paciente=paciente_acceso if not es_profesional else paciente,
        tipo_registro='condicion',
        registro_id=condicion.id,
        motivo='Consulta de condición médica por ' + ('profesional' if es_profesional else 'paciente')
    )

    context = {
        'paciente': paciente,
        'registro': condicion,
        'tipo': 'condicion',
        'es_profesional': es_profesional,
        'usuario_actual': profesional if es_profesional else paciente_acceso,
    }

    return render(request, 'users/detalle_registro_medico.html', context)


@login_required
def ver_tratamiento(request, paciente_id, tratamiento_id):
    """Vista para ver detalles de un tratamiento y registrar acceso"""
    # Verificar si el usuario es profesional o paciente propietario
    try:
        profesional = request.user.profesional
        es_profesional = True
        paciente_acceso = None
    except Profesional.DoesNotExist:
        try:
            paciente_acceso = request.user.paciente
            es_profesional = False
        except Paciente.DoesNotExist:
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('core:index')

    paciente = get_object_or_404(Paciente, id=paciente_id)
    tratamiento = get_object_or_404(Tratamiento, id=tratamiento_id, paciente=paciente)

    # Verificar que el paciente solo pueda ver sus propios registros
    if not es_profesional and paciente_acceso.id != paciente.id:
        messages.error(request, 'No tienes permisos para acceder a este registro.')
        return redirect('users:perfil_paciente')

    # Registrar acceso a la información médica
    BlockchainManager.registrar_acceso_medico(
        profesional=profesional if es_profesional else None,
        paciente=paciente_acceso if not es_profesional else paciente,
        tipo_registro='tratamiento',
        registro_id=tratamiento.id,
        motivo='Consulta de tratamiento médico por ' + ('profesional' if es_profesional else 'paciente')
    )

    context = {
        'paciente': paciente,
        'registro': tratamiento,
        'tipo': 'tratamiento',
        'es_profesional': es_profesional,
        'usuario_actual': profesional if es_profesional else paciente_acceso,
    }

    return render(request, 'users/detalle_registro_medico.html', context)


@login_required
def ver_prueba_laboratorio(request, paciente_id, prueba_id):
    """Vista para ver detalles de una prueba de laboratorio y registrar acceso"""
    # Verificar si el usuario es profesional o paciente propietario
    try:
        profesional = request.user.profesional
        es_profesional = True
        paciente_acceso = None
    except Profesional.DoesNotExist:
        try:
            paciente_acceso = request.user.paciente
            es_profesional = False
        except Paciente.DoesNotExist:
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('core:index')

    paciente = get_object_or_404(Paciente, id=paciente_id)
    prueba = get_object_or_404(PruebaLaboratorio, id=prueba_id, paciente=paciente)

    # Verificar que el paciente solo pueda ver sus propios registros
    if not es_profesional and paciente_acceso.id != paciente.id:
        messages.error(request, 'No tienes permisos para acceder a este registro.')
        return redirect('users:perfil_paciente')

    # Registrar acceso a la información médica
    BlockchainManager.registrar_acceso_medico(
        profesional=profesional if es_profesional else None,
        paciente=paciente_acceso if not es_profesional else paciente,
        tipo_registro='prueba_laboratorio',
        registro_id=prueba.id,
        motivo='Consulta de prueba de laboratorio por ' + ('profesional' if es_profesional else 'paciente')
    )

    context = {
        'paciente': paciente,
        'registro': prueba,
        'tipo': 'prueba_laboratorio',
        'es_profesional': es_profesional,
        'usuario_actual': profesional if es_profesional else paciente_acceso,
    }

    return render(request, 'users/detalle_registro_medico.html', context)


@login_required
def ver_cirugia(request, paciente_id, cirugia_id):
    """Vista para ver detalles de una cirugía y registrar acceso"""
    # Verificar si el usuario es profesional o paciente propietario
    try:
        profesional = request.user.profesional
        es_profesional = True
        paciente_acceso = None
    except Profesional.DoesNotExist:
        try:
            paciente_acceso = request.user.paciente
            es_profesional = False
        except Paciente.DoesNotExist:
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('core:index')

    paciente = get_object_or_404(Paciente, id=paciente_id)
    cirugia = get_object_or_404(Cirugia, id=cirugia_id, paciente=paciente)

    # Verificar que el paciente solo pueda ver sus propios registros
    if not es_profesional and paciente_acceso.id != paciente.id:
        messages.error(request, 'No tienes permisos para acceder a este registro.')
        return redirect('users:perfil_paciente')

    # Registrar acceso a la información médica
    BlockchainManager.registrar_acceso_medico(
        profesional=profesional if es_profesional else None,
        paciente=paciente_acceso if not es_profesional else paciente,
        tipo_registro='cirugia',
        registro_id=cirugia.id,
        motivo='Consulta de cirugía por ' + ('profesional' if es_profesional else 'paciente')
    )

    context = {
        'paciente': paciente,
        'registro': cirugia,
        'tipo': 'cirugia',
        'es_profesional': es_profesional,
        'usuario_actual': profesional if es_profesional else paciente_acceso,
    }

    return render(request, 'users/detalle_registro_medico.html', context)


# Vistas para formularios médicos
@login_required
def agregar_alergia(request, paciente_id):
    """Vista para agregar una nueva alergia a un paciente"""
    try:
        profesional = request.user.profesional
    except Profesional.DoesNotExist:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('core:index')

    paciente = get_object_or_404(Paciente, id=paciente_id)

    if request.method == 'POST':
        form = AlergiaForm(request.POST)
        if form.is_valid():
            alergia = form.save(commit=False)
            alergia.paciente = paciente
            alergia.save()
            messages.success(request, 'Alergia agregada exitosamente y registrada en blockchain.')
            return redirect('users:perfil_paciente', paciente_id=paciente.id)
    else:
        form = AlergiaForm()

    context = {
        'form': form,
        'paciente': paciente,
        'profesional': profesional,
    }

    return render(request, 'blockchain/forms/alergia_form.html', context)


@login_required
def agregar_condicion(request, paciente_id):
    """Vista para agregar una nueva condición médica a un paciente"""
    try:
        profesional = request.user.profesional
    except Profesional.DoesNotExist:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('core:index')

    paciente = get_object_or_404(Paciente, id=paciente_id)

    if request.method == 'POST':
        form = CondicionMedicaForm(request.POST)
        if form.is_valid():
            condicion = form.save(commit=False)
            condicion.paciente = paciente
            condicion.save()
            messages.success(request, 'Condición médica agregada exitosamente y registrada en blockchain.')
            return redirect('users:perfil_paciente', paciente_id=paciente.id)
    else:
        form = CondicionMedicaForm()

    context = {
        'form': form,
        'paciente': paciente,
        'profesional': profesional,
    }

    return render(request, 'blockchain/forms/condicion_form.html', context)


@login_required
def agregar_tratamiento(request, paciente_id):
    """Vista para agregar un nuevo tratamiento a un paciente"""
    try:
        profesional = request.user.profesional
    except Profesional.DoesNotExist:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('core:index')

    paciente = get_object_or_404(Paciente, id=paciente_id)

    if request.method == 'POST':
        form = TratamientoForm(request.POST)
        if form.is_valid():
            tratamiento = form.save(commit=False)
            tratamiento.paciente = paciente
            tratamiento.profesional = profesional
            tratamiento.save()
            messages.success(request, 'Tratamiento agregado exitosamente y registrado en blockchain.')
            return redirect('users:perfil_paciente', paciente_id=paciente.id)
    else:
        form = TratamientoForm()

    context = {
        'form': form,
        'paciente': paciente,
        'profesional': profesional,
    }

    return render(request, 'blockchain/forms/tratamiento_form.html', context)


@login_required
def agregar_prueba_laboratorio(request, paciente_id):
    """Vista para agregar una nueva prueba de laboratorio a un paciente"""
    try:
        profesional = request.user.profesional
    except Profesional.DoesNotExist:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('core:index')

    paciente = get_object_or_404(Paciente, id=paciente_id)

    if request.method == 'POST':
        form = PruebaLaboratorioForm(request.POST, request.FILES)
        if form.is_valid():
            prueba = form.save(commit=False)
            prueba.paciente = paciente
            prueba.profesional = profesional
            prueba.save()
            messages.success(request, 'Prueba de laboratorio agregada exitosamente y registrada en blockchain.')
            return redirect('users:perfil_paciente', paciente_id=paciente.id)
    else:
        form = PruebaLaboratorioForm()

    context = {
        'form': form,
        'paciente': paciente,
        'profesional': profesional,
    }

    return render(request, 'blockchain/forms/prueba_laboratorio_form.html', context)


@login_required
def agregar_cirugia(request, paciente_id):
    """Vista para agregar una nueva cirugía a un paciente"""
    try:
        profesional = request.user.profesional
    except Profesional.DoesNotExist:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('core:index')

    paciente = get_object_or_404(Paciente, id=paciente_id)

    if request.method == 'POST':
        form = CirugiaForm(request.POST)
        if form.is_valid():
            cirugia = form.save(commit=False)
            cirugia.paciente = paciente
            cirugia.profesional = profesional
            cirugia.save()
            messages.success(request, 'Cirugía agregada exitosamente y registrada en blockchain.')
            return redirect('users:perfil_paciente', paciente_id=paciente.id)
    else:
        form = CirugiaForm()

    context = {
        'form': form,
        'paciente': paciente,
        'profesional': profesional,
    }

    return render(request, 'blockchain/forms/cirugia_form.html', context)
