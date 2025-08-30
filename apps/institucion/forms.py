from django import forms
from .models import Enfermero, Operario, Sala, Cama

class EnfermeroForm(forms.ModelForm):
    class Meta:
        model = Enfermero
        fields = ['nombre', 'apellido', 'especialidad', 'turno']

class OperarioForm(forms.ModelForm):
    class Meta:
        model = Operario
        fields = ['nombre', 'apellido', 'area', 'turno']

class SalaForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = ['nombre', 'capacidad']

class CamaForm(forms.ModelForm):
    class Meta:
        model = Cama
        fields = ['numero', 'sala', 'estado', 'enfermero_asignado']
