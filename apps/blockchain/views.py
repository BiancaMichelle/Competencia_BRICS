from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import datetime
import json

from .models import (
    Alergia, CondicionMedica, 
    Medicamento, Tratamiento, Antecedente, PruebaLaboratorio, 
    Cirugia, Block, BlockchainHash, BlockchainService
)

from .forms import (
    AlergiaForm, 
    CondicionMedicaForm, TratamientoForm, AntecedenteForm, 
    PruebaLaboratorioForm, CirugiaForm
)

from apps.users.models import Paciente, Profesional

def is_superuser(user):
    return user.is_superuser

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
@require_http_methods(["GET", "POST"])
def agregar_alergia(request, paciente_id):
    """Agregar una nueva alergia a un paciente. GET renderiza el formulario; POST lo procesa."""
    paciente = get_object_or_404(Paciente, id=paciente_id)

    if request.method == 'GET':
        form = AlergiaForm()
        return render(request, 'blockchain/forms/alergia_form.html', {'form': form, 'paciente': paciente})

    # POST processing
    form = AlergiaForm(request.POST)
    if form.is_valid():
        alergia = form.save(commit=False)
        alergia.paciente = paciente
        alergia.save()

        # Crear o actualizar versión del paciente en blockchain
        BlockchainService.create_patient_version(paciente, created_by=request.user)

        messages.success(request, 'Alergia agregada exitosamente.')
        return JsonResponse({'status': 'success', 'message': 'Alergia agregada exitosamente.', 'alergia_id': alergia.id})

    return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

@login_required
@require_http_methods(["GET", "POST"])
def agregar_condicion(request, paciente_id):
    """Agregar una nueva condición médica a un paciente. GET renderiza el formulario; POST lo procesa."""
    paciente = get_object_or_404(Paciente, id=paciente_id)

    if request.method == 'GET':
        form = CondicionMedicaForm()
        return render(request, 'blockchain/forms/condicion_form.html', {'form': form, 'paciente': paciente})

    form = CondicionMedicaForm(request.POST)
    if form.is_valid():
        condicion = form.save(commit=False)
        condicion.paciente = paciente
        condicion.save()

        BlockchainService.create_patient_version(paciente, created_by=request.user)

        messages.success(request, 'Condición médica agregada exitosamente.')
        return JsonResponse({'status': 'success', 'message': 'Condición médica agregada exitosamente.', 'condicion_id': condicion.id})

    return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

@login_required
@require_http_methods(["GET", "POST"])
def agregar_tratamiento(request, paciente_id):
    """Agregar un nuevo tratamiento a un paciente. GET renderiza el formulario; POST lo procesa."""
    paciente = get_object_or_404(Paciente, id=paciente_id)

    try:
        profesional = request.user.profesional
    except Profesional.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Solo los profesionales pueden agregar tratamientos.'}, status=403)

    if request.method == 'GET':
        form = TratamientoForm()
        return render(request, 'blockchain/forms/tratamiento_form.html', {'form': form, 'paciente': paciente})

    form = TratamientoForm(request.POST)
    if form.is_valid():
        tratamiento = form.save(commit=False)
        tratamiento.paciente = paciente
        tratamiento.profesional = profesional
        tratamiento.save()

        BlockchainService.create_patient_version(paciente, created_by=request.user)

        messages.success(request, 'Tratamiento agregado exitosamente.')
        return JsonResponse({'status': 'success', 'message': 'Tratamiento agregado exitosamente.', 'tratamiento_id': tratamiento.id})

    return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)


@login_required
def blockchain_dashboard(request):
    """Dashboard principal del módulo blockchain"""
    
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
