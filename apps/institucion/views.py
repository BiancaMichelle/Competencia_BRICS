
# Create your views here.
from django.shortcuts import render, redirect
from .forms import EnfermeroForm, OperarioForm, SalaForm, CamaForm
from .models import Enfermero, Operario, Sala, Cama

def registrar_enfermero(request):
    if request.method == 'POST':
        form = EnfermeroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('registrar_enfermero')
    else:
        form = EnfermeroForm()
        enfermeros = Enfermero.objects.all()
    return render(request, 'management/registrar_enfermero.html', {'form': form, 'enfermeros': enfermeros})

def registrar_operario(request):
    if request.method == 'POST':
        form = OperarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('registrar_operario')
    else:
        form = OperarioForm()
        operarios = Operario.objects.all()
    return render(request, 'management/registrar_operario.html', {'form': form, 'operarios': operarios})

def registrar_sala(request):
    if request.method == 'POST':
        form = SalaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('registrar_sala')
    else:
        form = SalaForm()
    salas = Sala.objects.all()
    return render(request, 'management/registrar_sala.html', {'form': form, 'salas': salas})

def registrar_cama(request):
    if request.method == 'POST':
        form = CamaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('registrar_cama')
    else:
        form = CamaForm()
    camas = Cama.objects.select_related('sala', 'enfermero_asignado').all()
    return render(request, 'management/registrar_cama.html', {'form': form, 'camas': camas})

def lista_camas(request):
    camas = Cama.objects.select_related('sala', 'enfermero_asignado').all()
    return render(request, 'management/lista_camas.html', {'camas': camas})

def lista_salas(request):
    salas = Sala.objects.all()
    return render(request, 'management/lista_salas.html', {'salas': salas})