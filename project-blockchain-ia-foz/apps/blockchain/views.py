from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from datetime import date, datetime, timedelta
import json

from .models import (
    Paciente, Profesional, Alergia, CondicionMedica, 
    Medicamento, Tratamiento, Antecedente, PruebaLaboratorio, 
    Cirugia, Block, MedicalRecord, BlockchainTransaction
)
from .forms import (
    PacienteForm, PacienteRegistroForm, ProfesionalForm, ProfesionalRegistroForm, AlergiaForm, 
    CondicionMedicaForm, TratamientoForm, AntecedenteForm, 
    PruebaLaboratorioForm, CirugiaForm, BuscarPacienteForm
)


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
        medical_record = MedicalRecord.objects.create(
            paciente=paciente,
            tipo_registro='alergia',
            contenido=json.dumps({
                'sustancia': alergia.sustancia,
                'descripcion': alergia.descripcion,
                'severidad': alergia.severidad,
                'fecha_diagnostico': str(alergia.fecha_diagnostico)
            })
        )
        
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
        medical_record = MedicalRecord.objects.create(
            paciente=paciente,
            tipo_registro='condicion_medica',
            contenido=json.dumps({
                'nombre': condicion.nombre,
                'descripcion': condicion.descripcion,
                'fecha_diagnostico': str(condicion.fecha_diagnostico),
                'estado': condicion.estado
            })
        )
        
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
        medical_record = MedicalRecord.objects.create(
            paciente=paciente,
            tipo_registro='tratamiento',
            contenido=json.dumps({
                'descripcion': tratamiento.descripcion,
                'dosis': tratamiento.dosis,
                'frecuencia': tratamiento.frecuencia,
                'fecha_inicio': str(tratamiento.fecha_inicio),
                'profesional': str(profesional),
                'medicamento': str(tratamiento.medicamento) if tratamiento.medicamento else None
            })
        )
        
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


def registro_profesional(request):
    """Registro de nuevo profesional"""
    if request.method == 'POST':
        user_form = ProfesionalRegistroForm(request.POST)
        profesional_form = ProfesionalForm(request.POST)
        
        if user_form.is_valid() and profesional_form.is_valid():
            # Crear el usuario
            user = user_form.save()
            
            # Crear el profesional asociado al usuario
            profesional = profesional_form.save(commit=False)
            profesional.user = user
            profesional.save()
            
            login(request, user)
            messages.success(request, '¡Registro exitoso! Bienvenido al sistema.')
            return redirect('blockchain:panel_profesional')
    else:
        user_form = ProfesionalRegistroForm()
        profesional_form = ProfesionalForm()
    
    return render(request, 'registration/registro_profesional.html', {
        'user_form': user_form,
        'profesional_form': profesional_form
    })


# VISTAS ESPECÍFICAS DE BLOCKCHAIN

@login_required
def blockchain_dashboard(request):
    """Dashboard principal del módulo blockchain"""
    context = {
        'total_blocks': Block.objects.count(),
        'total_records': MedicalRecord.objects.count(),
        'recent_blocks': Block.objects.all().order_by('-timestamp')[:5],
        'recent_records': MedicalRecord.objects.all().order_by('-timestamp')[:10],
    }
    return render(request, 'blockchain/dashboard.html', context)


@login_required
def verify_blockchain(request):
    """Verificar la integridad de la blockchain"""
    blocks = Block.objects.all().order_by('index')
    is_valid = True
    
    for i, block in enumerate(blocks):
        if i == 0:  # Genesis block
            if block.previous_hash != "0":
                is_valid = False
                break
        else:
            previous_block = blocks[i-1]
            if block.previous_hash != previous_block.hash:
                is_valid = False
                break
            
            if block.hash != block.calculate_hash():
                is_valid = False
                break
    
    return JsonResponse({
        'is_valid': is_valid,
        'total_blocks': blocks.count(),
        'message': 'Blockchain válida' if is_valid else 'Blockchain comprometida'
    })


@login_required
def get_patient_blockchain_history(request, paciente_id):
    """Obtener historial blockchain de un paciente"""
    try:
        paciente = Paciente.objects.get(id=paciente_id)
        records = MedicalRecord.objects.filter(paciente=paciente).order_by('-timestamp')
        
        history = []
        for record in records:
            history.append({
                'id': record.id,
                'tipo': record.tipo_registro,
                'timestamp': record.timestamp.isoformat(),
                'hash': record.hash_registro,
                'verificado': record.verificado,
                'block_index': record.block.index if record.block else None
            })
        
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
