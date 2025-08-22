from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from datetime import date, datetime, timedelta
import json

from .models import (
    Alergia, CondicionMedica, 
    Medicamento, Tratamiento, Antecedente, PruebaLaboratorio, 
    Cirugia, Block, BlockchainHash, BlockchainService
)
# BlockchainTransaction ELIMINADO - No se usaba
# Importamos los formularios
from .forms import (
    AlergiaForm, 
    CondicionMedicaForm, TratamientoForm, AntecedenteForm, 
    PruebaLaboratorioForm, CirugiaForm, BuscarPacienteForm
)
from apps.users.forms import (
    PacienteForm, PacienteRegistroForm, ProfesionalForm, ProfesionalRegistroForm
)
from apps.users.models import Paciente, Profesional

# Función auxiliar para verificar superusuario
def is_superuser(user):
    return user.is_superuser


@login_required
def panel_paciente(request):
    """Vista principal del panel del paciente"""
    try:
        paciente = request.user.paciente
    except Paciente.DoesNotExist:
        messages.error(request, 'No tienes un perfil de paciente asociado.')
        return redirect('core:index')
    
    # Obtener todos los datos del paciente
    alergias = paciente.alergias.all()
    condiciones = paciente.condiciones.filter(estado='activa')
    tratamientos_activos = paciente.tratamientos.filter(activo=True)
    
    # Historial médico
    antecedentes = paciente.antecedentes.all()
    pruebas = paciente.pruebas.all().order_by('-fecha_realizacion')[:10]
    cirugias = paciente.cirugias.all().order_by('-fecha_cirugia')
    
    context = {
        'paciente': paciente,
        'alergias': alergias,
        'condiciones': condiciones,
        'tratamientos_activos': tratamientos_activos,
        'antecedentes': antecedentes,
        'pruebas': pruebas,
        'cirugias': cirugias,
    }
    
    return render(request, 'panel_paciente.html', context)


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
    
    return render(request, 'panel_profesional.html', context)


@login_required
def perfil_paciente(request, paciente_id=None):
    """Vista del perfil completo de un paciente"""
    if paciente_id:
        # Un profesional está viendo el perfil de un paciente
        paciente = get_object_or_404(Paciente, id=paciente_id)
        es_propio_perfil = False
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
        'alergias': paciente.alergias.all(),
        'condiciones': paciente.condiciones.all(),
        'tratamientos': paciente.tratamientos.all().order_by('-fecha_inicio'),
        'antecedentes': paciente.antecedentes.all(),
        'pruebas': paciente.pruebas.all().order_by('-fecha_realizacion'),
        'cirugias': paciente.cirugias.all().order_by('-fecha_cirugia'),
    }
    
    return render(request, 'perfil_paciente.html', context)


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
    
    return render(request, 'buscar_pacientes.html', context)


# APIs para obtener datos dinámicos
@login_required
def api_historial_paciente(request):
    """API para obtener historial médico del paciente"""
    try:
        paciente = request.user.paciente
        
        historial = {
            'antecedentes': [str(ant) for ant in paciente.antecedentes.all()],
            'pruebas': [
                {
                    'nombre': prueba.nombre_prueba,
                    'fecha': prueba.fecha_realizacion.strftime('%d/%m/%Y'),
                    'resultados': prueba.resultados
                } for prueba in paciente.pruebas.all().order_by('-fecha_realizacion')[:5]
            ],
            'cirugias': [
                {
                    'nombre': cirugia.nombre_cirugia,
                    'fecha': cirugia.fecha_cirugia.strftime('%d/%m/%Y'),
                    'estado': cirugia.get_estado_display()
                } for cirugia in paciente.cirugias.all().order_by('-fecha_cirugia')
            ]
        }
        
        return JsonResponse({'historial': historial})
    except Paciente.DoesNotExist:
        return JsonResponse({'error': 'Paciente no encontrado'}, status=404)


# Vistas para agregar registros médicos
@login_required
@require_http_methods(["POST"])
def agregar_alergia(request, paciente_id):
    """Agregar una nueva alergia a un paciente"""
    paciente = get_object_or_404(Paciente, id=paciente_id)
    form = AlergiaForm(request.POST)
    
    if form.is_valid():
        alergia = form.save(commit=False)
        alergia.paciente = paciente
        alergia.save()
        
        # Crear registro en blockchain
        blockchain_service = BlockchainService()
        blockchain_data = {
            'paciente_id': paciente.id,
            'tipo_registro': 'alergia',
            'contenido': {
                'sustancia': alergia.sustancia,
                'descripcion': alergia.descripcion,
                'severidad': alergia.severidad,
                'fecha_diagnostico': str(alergia.fecha_diagnostico)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # Crear hash y almacenar en blockchain
        hash_record = blockchain_service.create_hash(json.dumps(blockchain_data, ensure_ascii=False))
        
        messages.success(request, 'Alergia agregada exitosamente.')
        return JsonResponse({
            'status': 'success',
            'message': 'Alergia agregada exitosamente.',
            'alergia_id': alergia.id
        })
    else:
        return JsonResponse({
            'status': 'error',
            'errors': form.errors
        })


@login_required
@require_http_methods(["POST"])
def agregar_condicion(request, paciente_id):
    """Agregar una nueva condición médica a un paciente"""
    paciente = get_object_or_404(Paciente, id=paciente_id)
    form = CondicionMedicaForm(request.POST)
    
    if form.is_valid():
        condicion = form.save(commit=False)
        condicion.paciente = paciente
        condicion.save()
        
        # Crear registro en blockchain
        blockchain_service = BlockchainService()
        blockchain_data = {
            'paciente_id': paciente.id,
            'tipo_registro': 'condicion_medica',
            'contenido': {
                'codigo': condicion.codigo,
                'descripcion': condicion.descripcion,
                'fecha_diagnostico': str(condicion.fecha_diagnostico),
                'estado': condicion.estado
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # Crear hash y almacenar en blockchain
        hash_record = blockchain_service.create_hash(json.dumps(blockchain_data, ensure_ascii=False))
        
        messages.success(request, 'Condición médica agregada exitosamente.')
        return JsonResponse({
            'status': 'success',
            'message': 'Condición médica agregada exitosamente.',
            'condicion_id': condicion.id
        })
    else:
        return JsonResponse({
            'status': 'error',
            'errors': form.errors
        })


@login_required
@require_http_methods(["POST"])
def agregar_tratamiento(request, paciente_id):
    """Agregar un nuevo tratamiento a un paciente"""
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    try:
        profesional = request.user.profesional
    except Profesional.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Solo los profesionales pueden agregar tratamientos.'
        })
    
    form = TratamientoForm(request.POST)
    
    if form.is_valid():
        tratamiento = form.save(commit=False)
        tratamiento.paciente = paciente
        tratamiento.profesional = profesional
        tratamiento.save()
        
        # Crear registro en blockchain
        blockchain_service = BlockchainService()
        blockchain_data = {
            'paciente_id': paciente.id,
            'tipo_registro': 'tratamiento',
            'contenido': {
                'descripcion': tratamiento.descripcion,
                'dosis': tratamiento.dosis,
                'frecuencia': tratamiento.frecuencia,
                'fecha_inicio': str(tratamiento.fecha_inicio),
                'profesional': str(profesional),
                'medicamento': str(tratamiento.medicamento) if tratamiento.medicamento else None
            },
            'timestamp': datetime.now().isoformat()
        }
        
        # Crear hash y almacenar en blockchain
        hash_record = blockchain_service.create_hash(json.dumps(blockchain_data, ensure_ascii=False))
        
        messages.success(request, 'Tratamiento agregado exitosamente.')
        return JsonResponse({
            'status': 'success',
            'message': 'Tratamiento agregado exitosamente.',
            'tratamiento_id': tratamiento.id
        })
    else:
        return JsonResponse({
            'status': 'error',
            'errors': form.errors
        })


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
            return redirect('blockchain:panel_paciente')
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
    
    return render(request, 'blockchain/admin/registro_profesional.html', {
        'user_form': user_form,
        'profesional_form': profesional_form
    })


# VISTAS ESPECÍFICAS DE BLOCKCHAIN

@login_required
def blockchain_dashboard(request):
    """Dashboard principal del módulo blockchain"""
    from datetime import datetime, timedelta
    from django.db.models import Count
    
    # Estadísticas principales
    total_pacientes = Paciente.objects.count()
    total_hashes = BlockchainHash.objects.count()
    total_profesionales = Profesional.objects.count()
    
    # Registros médicos totales (suma de todos los tipos)
    total_alergias = Alergia.objects.count()
    total_condiciones = CondicionMedica.objects.count()
    total_tratamientos = Tratamiento.objects.count()
    total_pruebas = PruebaLaboratorio.objects.count()
    total_cirugias = Cirugia.objects.count()
    total_registros_medicos = total_alergias + total_condiciones + total_tratamientos + total_pruebas + total_cirugias
    
    # Pacientes nuevos este mes
    mes_actual = datetime.now().replace(day=1)
    nuevos_pacientes_mes = Paciente.objects.filter(user__date_joined__gte=mes_actual).count()
    
    # Hashes blockchain recientes
    recent_hashes = BlockchainHash.objects.all().order_by('-timestamp')[:10]
    
    # Verificar integridad de la cadena
    from .models import BlockchainService
    is_valid, message = BlockchainService.verify_chain_integrity()
    integridad_cadena = "Cadena íntegra" if is_valid else f"Error: {message}"
    
    # Hashes verificados
    hashes_verificados = BlockchainHash.objects.filter(is_verified=True).count()
    
    # Último hash
    ultimo_hash_obj = BlockchainHash.objects.order_by('-timestamp').first()
    ultimo_hash = ultimo_hash_obj.hash_value if ultimo_hash_obj else None
    
    # Actividad reciente (simulada - puedes expandir esto)
    actividad_reciente = []
    
    # Añadir actividad de pacientes recientes
    pacientes_recientes = Paciente.objects.order_by('-user__date_joined')[:3]
    for paciente in pacientes_recientes:
        actividad_reciente.append({
            'titulo': f'Nuevo paciente registrado',
            'descripcion': f'{paciente.get_full_name()} se registró en el sistema',
            'timestamp': paciente.user.date_joined
        })
    
    # Añadir actividad de hashes recientes
    hashes_recientes_actividad = BlockchainHash.objects.order_by('-timestamp')[:3]
    for hash_obj in hashes_recientes_actividad:
        actividad_reciente.append({
            'titulo': f'Hash blockchain creado',
            'descripcion': f'Nuevo hash para {hash_obj.content_type} ID:{hash_obj.object_id}',
            'timestamp': hash_obj.timestamp
        })
    
    # Ordenar actividad por timestamp
    actividad_reciente.sort(key=lambda x: x['timestamp'], reverse=True)
    actividad_reciente = actividad_reciente[:5]  # Limitar a 5 elementos
    
    context = {
        'total_pacientes': total_pacientes,
        'total_hashes': total_hashes,
        'total_profesionales': total_profesionales,
        'total_registros_medicos': total_registros_medicos,
        'nuevos_pacientes_mes': nuevos_pacientes_mes,
        'recent_hashes': recent_hashes,
        'integridad_cadena': integridad_cadena,
        'hashes_verificados': hashes_verificados,
        'ultimo_hash': ultimo_hash,
        'actividad_reciente': actividad_reciente,
        'total_blocks': Block.objects.count(),
    }
    return render(request, 'blockchain/dashboard.html', context)


@login_required
def verify_blockchain(request):
    """Verificar la integridad de la blockchain usando BlockchainHash"""
    from django.http import JsonResponse
    
    try:
        # Verificar integridad usando el servicio
        is_valid, message = BlockchainService.verify_chain_integrity()
        
        # Estadísticas adicionales
        total_hashes = BlockchainHash.objects.count()
        hashes_verificados = BlockchainHash.objects.filter(is_verified=True).count()
        
        return JsonResponse({
            'is_valid': is_valid,
            'total_hashes': total_hashes,
            'hashes_verificados': hashes_verificados,
            'message': message
        })
        
    except Exception as e:
        return JsonResponse({
            'is_valid': False,
            'error': str(e),
            'message': 'Error al verificar la blockchain'
        }, status=500)


@login_required
def blockchain_hashes_list(request):
    """Lista completa de hashes blockchain"""
    hashes = BlockchainHash.objects.all().order_by('-timestamp')
    
    # Filtros opcionales
    content_type = request.GET.get('type')
    if content_type:
        hashes = hashes.filter(content_type=content_type)
    
    # Paginación
    from django.core.paginator import Paginator
    paginator = Paginator(hashes, 20)  # 20 hashes por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Tipos disponibles para filtro
    content_types = BlockchainHash.objects.values_list('content_type', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'content_types': content_types,
        'selected_type': content_type,
        'total_hashes': hashes.count(),
    }
    
    return render(request, 'blockchain/hashes_list.html', context)


@login_required
def get_patient_blockchain_history(request, paciente_id):
    """Obtener historial blockchain de un paciente"""
    try:
        paciente = Paciente.objects.get(id=paciente_id)
        # Buscar hashes relacionados con este paciente
        records = BlockchainHash.objects.filter(
            data__contains=f'"paciente_id": {paciente_id}'
        ).order_by('-timestamp')
        
        history = []
        for record in records:
            try:
                data_dict = json.loads(record.data) if isinstance(record.data, str) else record.data
                history.append({
                    'id': record.id,
                    'tipo': data_dict.get('tipo_registro', 'desconocido'),
                    'timestamp': record.timestamp.isoformat(),
                    'hash': record.hash_value,
                    'verificado': record.verified,
                    'data': data_dict.get('contenido', {})
                })
            except json.JSONDecodeError:
                continue
        
        return JsonResponse({
            'success': True,
            'paciente': paciente.user.get_full_name(),
            'history': history
        })
        
    except Paciente.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Paciente no encontrado'
        })


# Funciones auxiliares para la blockchain
def create_genesis_block():
    """Crear el bloque génesis si no existe"""
    if not Block.objects.exists():
        genesis_block = Block(
            index=0,
            data='{"message": "Genesis Block"}',
            previous_hash="0"
        )
        genesis_block.hash = genesis_block.calculate_hash()
        genesis_block.save()
        return genesis_block
    return Block.objects.first()


def get_latest_block():
    """Obtener el último bloque de la cadena"""
    return Block.objects.last()


def validate_chain():
    """Validar toda la cadena de bloques"""
    blocks = Block.objects.all().order_by('index')
    
    for i in range(1, len(blocks)):
        current_block = blocks[i]
        previous_block = blocks[i-1]
        
        if current_block.hash != current_block.calculate_hash():
            return False
            
        if current_block.previous_hash != previous_block.hash:
            return False
    
    return True
