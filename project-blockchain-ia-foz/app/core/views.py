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
    Cirugia, Turno
)
from .forms import (
    PacienteForm, PacienteRegistroForm, ProfesionalForm, ProfesionalRegistroForm,
    AlergiaForm, CondicionMedicaForm, MedicamentoForm, TratamientoForm,
    AntecedenteForm, PruebaLaboratorioForm, CirugiaForm, TurnoForm,
    TurnoPacienteForm, BuscarPacienteForm
)


def index(request):
    return render(request, 'inicio/index.html')


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
    turnos_proximos = paciente.turnos.filter(
        fecha_hora__gte=datetime.now(),
        estado__in=['programado', 'confirmado']
    ).order_by('fecha_hora')[:5]
    
    # Historial médico
    antecedentes = paciente.antecedentes.all()
    pruebas = paciente.pruebas.all().order_by('-fecha_realizacion')[:10]
    cirugias = paciente.cirugias.all().order_by('-fecha_cirugia')
    
    context = {
        'paciente': paciente,
        'alergias': alergias,
        'condiciones': condiciones,
        'tratamientos_activos': tratamientos_activos,
        'turnos_proximos': turnos_proximos,
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
    
    # Turnos del día
    hoy = date.today()
    turnos_hoy = profesional.turnos.filter(
        fecha_hora__date=hoy
    ).order_by('fecha_hora')
    
    # Próximos turnos
    turnos_proximos = profesional.turnos.filter(
        fecha_hora__gt=datetime.now(),
        estado__in=['programado', 'confirmado']
    ).order_by('fecha_hora')[:10]
    
    # Pacientes recientes
    pacientes_recientes = Paciente.objects.filter(
        turnos__profesional=profesional,
        turnos__fecha_hora__gte=datetime.now() - timedelta(days=30)
    ).distinct()[:5]
    
    context = {
        'profesional': profesional,
        'turnos_hoy': turnos_hoy,
        'turnos_proximos': turnos_proximos,
        'pacientes_recientes': pacientes_recientes,
        'today': hoy,
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
        'turnos': paciente.turnos.all().order_by('-fecha_hora')[:10],
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


# APIs para obtener datos dinámicos (para usar con AJAX)
@login_required
def api_turnos_paciente(request):
    """API para obtener turnos del paciente logueado"""
    try:
        paciente = request.user.paciente
        turnos = []
        
        for turno in paciente.turnos.filter(fecha_hora__gte=datetime.now()).order_by('fecha_hora'):
            turnos.append({
                'id': turno.id,
                'profesional': str(turno.profesional),
                'especialidad': turno.profesional.get_especialidad_display(),
                'fecha': turno.fecha_hora.strftime('%d de %B de %Y'),
                'hora': turno.fecha_hora.strftime('%I:%M %p'),
                'estado': turno.get_estado_display(),
                'motivo': turno.motivo
            })
        
        return JsonResponse({'turnos': turnos})
    except Paciente.DoesNotExist:
        return JsonResponse({'error': 'Paciente no encontrado'}, status=404)


@login_required
def api_historial_paciente(request):
    """API para obtener historial médico del paciente"""
    try:
        paciente = request.user.paciente
        
        historial = {
            'antecedentes': [str(ant) for ant in paciente.antecedentes.all()],
            'pruebas': [
                f"{prueba.nombre_prueba} ({prueba.fecha_realizacion.strftime('%Y-%m-%d')}): {prueba.resultados[:100]}..."
                for prueba in paciente.pruebas.all().order_by('-fecha_realizacion')[:10]
            ],
            'tratamientos': [
                f"{trat.descripcion} - {trat.dosis} {trat.frecuencia}"
                for trat in paciente.tratamientos.filter(activo=True)
            ],
            'cirugias': [
                f"{cirugia.nombre_cirugia} ({cirugia.fecha_cirugia.year})"
                for cirugia in paciente.cirugias.all().order_by('-fecha_cirugia')
            ]
        }
        
        return JsonResponse(historial)
    except Paciente.DoesNotExist:
        return JsonResponse({'error': 'Paciente no encontrado'}, status=404)


@login_required
def api_turnos_profesional(request):
    """API para obtener turnos del profesional logueado"""
    try:
        profesional = request.user.profesional
        fecha = request.GET.get('fecha', date.today().isoformat())
        
        try:
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
        except ValueError:
            fecha_obj = date.today()
        
        turnos = []
        for turno in profesional.turnos.filter(fecha_hora__date=fecha_obj).order_by('fecha_hora'):
            turnos.append({
                'id': turno.id,
                'paciente': str(turno.paciente),
                'hora': turno.fecha_hora.strftime('%H:%M'),
                'motivo': turno.motivo,
                'estado': turno.get_estado_display(),
                'telefono': turno.paciente.telefono
            })
        
        return JsonResponse({'turnos': turnos})
    except Profesional.DoesNotExist:
        return JsonResponse({'error': 'Profesional no encontrado'}, status=404)


# Formularios para agregar/editar información médica
@login_required
def agregar_alergia(request, paciente_id):
    """Vista para agregar una nueva alergia"""
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    # Verificar permisos
    if not (request.user == paciente.user or hasattr(request.user, 'profesional')):
        messages.error(request, 'No tienes permisos para modificar esta información.')
        return redirect('core:perfil_paciente', paciente_id=paciente_id)
    
    if request.method == 'POST':
        form = AlergiaForm(request.POST)
        if form.is_valid():
            alergia = form.save(commit=False)
            alergia.paciente = paciente
            # Generar hash para blockchain
            alergia.blockchain_hash = paciente.generar_hash_blockchain()
            alergia.save()
            messages.success(request, 'Alergia agregada exitosamente.')
            return redirect('core:perfil_paciente', paciente_id=paciente_id)
    else:
        form = AlergiaForm()
    
    context = {
        'form': form,
        'paciente': paciente,
        'titulo': 'Agregar Alergia'
    }
    return render(request, 'forms/alergia_form.html', context)


@login_required
def agregar_condicion(request, paciente_id):
    """Vista para agregar una nueva condición médica"""
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    # Verificar permisos
    if not (request.user == paciente.user or hasattr(request.user, 'profesional')):
        messages.error(request, 'No tienes permisos para modificar esta información.')
        return redirect('core:perfil_paciente', paciente_id=paciente_id)
    
    if request.method == 'POST':
        form = CondicionMedicaForm(request.POST)
        if form.is_valid():
            condicion = form.save(commit=False)
            condicion.paciente = paciente
            condicion.blockchain_hash = paciente.generar_hash_blockchain()
            condicion.save()
            messages.success(request, 'Condición médica agregada exitosamente.')
            return redirect('core:perfil_paciente', paciente_id=paciente_id)
    else:
        form = CondicionMedicaForm()
    
    context = {
        'form': form,
        'paciente': paciente,
        'titulo': 'Agregar Condición Médica'
    }
    return render(request, 'forms/condicion_form.html', context)


@login_required
def agregar_tratamiento(request, paciente_id):
    """Vista para agregar un nuevo tratamiento"""
    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    # Solo profesionales pueden agregar tratamientos
    try:
        profesional = request.user.profesional
    except Profesional.DoesNotExist:
        messages.error(request, 'Solo los profesionales pueden agregar tratamientos.')
        return redirect('core:perfil_paciente', paciente_id=paciente_id)
    
    if request.method == 'POST':
        form = TratamientoForm(request.POST)
        if form.is_valid():
            tratamiento = form.save(commit=False)
            tratamiento.paciente = paciente
            tratamiento.profesional = profesional
            tratamiento.blockchain_hash = paciente.generar_hash_blockchain()
            tratamiento.save()
            messages.success(request, 'Tratamiento agregado exitosamente.')
            return redirect('core:perfil_paciente', paciente_id=paciente_id)
    else:
        form = TratamientoForm()
    
    context = {
        'form': form,
        'paciente': paciente,
        'titulo': 'Agregar Tratamiento'
    }
    return render(request, 'forms/tratamiento_form.html', context)


# Vista para registro de nuevos usuarios
def registro_paciente(request):
    """Vista para registro de nuevos pacientes"""
    if request.method == 'POST':
        user_form = PacienteRegistroForm(request.POST)
        paciente_form = PacienteForm(request.POST)
        
        if user_form.is_valid() and paciente_form.is_valid():
            user = user_form.save()
            paciente = paciente_form.save(commit=False)
            paciente.user = user
            paciente.save()  # Guardar primero para tener todos los datos
            paciente.blockchain_hash = paciente.generar_hash_blockchain()
            paciente.save()  # Guardar nuevamente con el hash
            
            login(request, user)
            messages.success(request, 'Registro exitoso. Bienvenido al sistema.')
            return redirect('core:panel_paciente')
    else:
        user_form = PacienteRegistroForm()
        paciente_form = PacienteForm()
    
    context = {
        'user_form': user_form,
        'paciente_form': paciente_form,
    }
    return render(request, 'registration/registro_paciente.html', context)


def registro_profesional(request):
    """Vista para registro de nuevos profesionales"""
    if request.method == 'POST':
        user_form = ProfesionalRegistroForm(request.POST)
        profesional_form = ProfesionalForm(request.POST)
        
        if user_form.is_valid() and profesional_form.is_valid():
            user = user_form.save()
            profesional = profesional_form.save(commit=False)
            profesional.user = user
            profesional.save()
            
            login(request, user)
            messages.success(request, 'Registro exitoso. Bienvenido al sistema.')
            return redirect('core:panel_profesional')
    else:
        user_form = ProfesionalRegistroForm()
        profesional_form = ProfesionalForm()
    
    context = {
        'user_form': user_form,
        'profesional_form': profesional_form,
    }
    return render(request, 'registration/registro_profesional.html', context)


@login_required
@require_http_methods(["GET"])
def obtener_turnos_fecha(request):
    """Vista AJAX para obtener turnos de una fecha específica"""
    try:
        profesional = request.user.profesional
    except Profesional.DoesNotExist:
        return JsonResponse({'error': 'No tienes un perfil de profesional asociado.'}, status=403)
    
    fecha_str = request.GET.get('fecha')
    if not fecha_str:
        return JsonResponse({'error': 'Fecha no proporcionada.'}, status=400)
    
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Formato de fecha inválido.'}, status=400)
    
    # Obtener turnos del día para el profesional
    turnos = profesional.turnos.filter(
        fecha_hora__date=fecha
    ).order_by('fecha_hora')
    
    turnos_data = []
    for turno in turnos:
        turnos_data.append({
            'id': turno.id,
            'fecha_hora': turno.fecha_hora.isoformat(),
            'motivo': turno.motivo,
            'estado': turno.estado,
            'paciente_nombre': f"{turno.paciente.user.first_name} {turno.paciente.user.last_name}",
            'paciente_cedula': turno.paciente.cedula,
            'paciente_telefono': turno.paciente.telefono,
        })
    
    return JsonResponse({'turnos': turnos_data})


@login_required
@require_http_methods(["POST"])
def marcar_turno_atendido(request, turno_id):
    """Vista AJAX para marcar un turno como atendido"""
    try:
        profesional = request.user.profesional
        turno = get_object_or_404(Turno, id=turno_id, profesional=profesional)
        
        turno.estado = 'finalizado'
        turno.save()
        
        return JsonResponse({'success': True, 'message': 'Turno marcado como finalizado.'})
    except Profesional.DoesNotExist:
        return JsonResponse({'error': 'No tienes un perfil de profesional asociado.'}, status=403)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def reprogramar_turno(request, turno_id):
    """Vista AJAX para reprogramar un turno"""
    try:
        profesional = request.user.profesional
        turno = get_object_or_404(Turno, id=turno_id, profesional=profesional)
        
        data = json.loads(request.body)
        nueva_fecha_hora_str = data.get('nueva_fecha_hora')
        
        if not nueva_fecha_hora_str:
            return JsonResponse({'error': 'Nueva fecha y hora no proporcionada.'}, status=400)
        
        try:
            # Intentar varios formatos de fecha
            for formato in ['%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S']:
                try:
                    nueva_fecha_hora = datetime.strptime(nueva_fecha_hora_str, formato)
                    break
                except ValueError:
                    continue
            else:
                raise ValueError("Formato de fecha inválido")
            
            turno.fecha_hora = nueva_fecha_hora
            turno.estado = 'programado'
            turno.save()
            
            return JsonResponse({'success': True, 'message': 'Turno reprogramado exitosamente.'})
        except ValueError:
            return JsonResponse({'error': 'Formato de fecha inválido. Use YYYY-MM-DD HH:MM'}, status=400)
    except Profesional.DoesNotExist:
        return JsonResponse({'error': 'No tienes un perfil de profesional asociado.'}, status=403)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)