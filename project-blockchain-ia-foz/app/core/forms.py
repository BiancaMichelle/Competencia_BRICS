from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import (
    Paciente, Profesional, Alergia, CondicionMedica, 
    Medicamento, Tratamiento, Antecedente, PruebaLaboratorio, 
    Cirugia, Turno
)

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['cedula', 'fecha_nacimiento', 'telefono', 'direccion', 'tipo_sangre']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1234567-8'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: +595 21 123456'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tipo_sangre': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'cedula': 'Cédula de Identidad',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
            'tipo_sangre': 'Tipo de Sangre',
        }


class PacienteRegistroForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label='Nombre')
    last_name = forms.CharField(max_length=30, required=True, label='Apellido')
    email = forms.EmailField(required=True, label='Correo Electrónico')
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        labels = {
            'username': 'Nombre de Usuario',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class ProfesionalForm(forms.ModelForm):
    class Meta:
        model = Profesional
        fields = ['especialidad', 'matricula', 'telefono', 'consultorio']
        widgets = {
            'especialidad': forms.Select(attrs={'class': 'form-control'}),
            'matricula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: MP-12345'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: +595 21 123456'}),
            'consultorio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Consultorio 201'}),
        }
        labels = {
            'especialidad': 'Especialidad',
            'matricula': 'Número de Matrícula',
            'telefono': 'Teléfono',
            'consultorio': 'Consultorio',
        }


class ProfesionalRegistroForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label='Nombre')
    last_name = forms.CharField(max_length=30, required=True, label='Apellido')
    email = forms.EmailField(required=True, label='Correo Electrónico')
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        labels = {
            'username': 'Nombre de Usuario',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class AlergiaForm(forms.ModelForm):
    class Meta:
        model = Alergia
        fields = ['sustancia', 'descripcion', 'severidad', 'fecha_diagnostico']
        widgets = {
            'sustancia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Penicilina'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'severidad': forms.Select(attrs={'class': 'form-control'}),
            'fecha_diagnostico': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        labels = {
            'sustancia': 'Sustancia/Medicamento',
            'descripcion': 'Descripción de la Reacción',
            'severidad': 'Severidad',
            'fecha_diagnostico': 'Fecha de Diagnóstico',
        }


class CondicionMedicaForm(forms.ModelForm):
    class Meta:
        model = CondicionMedica
        fields = ['nombre', 'descripcion', 'fecha_diagnostico', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Diabetes tipo 2'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fecha_diagnostico': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'nombre': 'Condición Médica',
            'descripcion': 'Descripción',
            'fecha_diagnostico': 'Fecha de Diagnóstico',
            'estado': 'Estado Actual',
        }


class MedicamentoForm(forms.ModelForm):
    class Meta:
        model = Medicamento
        fields = ['nombre', 'principio_activo', 'concentracion', 'forma_farmaceutica']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Aspirina'}),
            'principio_activo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Ácido acetilsalicílico'}),
            'concentracion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 500mg'}),
            'forma_farmaceutica': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Comprimido'}),
        }
        labels = {
            'nombre': 'Nombre del Medicamento',
            'principio_activo': 'Principio Activo',
            'concentracion': 'Concentración',
            'forma_farmaceutica': 'Forma Farmacéutica',
        }


class TratamientoForm(forms.ModelForm):
    class Meta:
        model = Tratamiento
        fields = ['medicamento', 'descripcion', 'dosis', 'frecuencia', 'fecha_inicio', 'fecha_fin', 'observaciones', 'activo']
        widgets = {
            'medicamento': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'dosis': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1 comprimido'}),
            'frecuencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Cada 8 horas'}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'medicamento': 'Medicamento',
            'descripcion': 'Descripción del Tratamiento',
            'dosis': 'Dosis',
            'frecuencia': 'Frecuencia',
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_fin': 'Fecha de Fin (opcional)',
            'observaciones': 'Observaciones',
            'activo': 'Tratamiento Activo',
        }


class AntecedenteForm(forms.ModelForm):
    class Meta:
        model = Antecedente
        fields = ['tipo', 'descripcion', 'fecha_evento', 'observaciones']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fecha_evento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'tipo': 'Tipo de Antecedente',
            'descripcion': 'Descripción',
            'fecha_evento': 'Fecha del Evento (opcional)',
            'observaciones': 'Observaciones',
        }


class PruebaLaboratorioForm(forms.ModelForm):
    class Meta:
        model = PruebaLaboratorio
        fields = ['nombre_prueba', 'fecha_realizacion', 'resultados', 'valores_referencia', 'observaciones', 'archivo_resultado']
        widgets = {
            'nombre_prueba': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Análisis de sangre completo'}),
            'fecha_realizacion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'resultados': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'valores_referencia': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'archivo_resultado': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nombre_prueba': 'Nombre de la Prueba',
            'fecha_realizacion': 'Fecha de Realización',
            'resultados': 'Resultados',
            'valores_referencia': 'Valores de Referencia',
            'observaciones': 'Observaciones',
            'archivo_resultado': 'Archivo de Resultado (PDF, imagen, etc.)',
        }


class CirugiaForm(forms.ModelForm):
    class Meta:
        model = Cirugia
        fields = ['nombre_cirugia', 'fecha_cirugia', 'descripcion', 'complicaciones', 'estado']
        widgets = {
            'nombre_cirugia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Apendicectomía'}),
            'fecha_cirugia': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'complicaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'nombre_cirugia': 'Nombre de la Cirugía',
            'fecha_cirugia': 'Fecha de la Cirugía',
            'descripcion': 'Descripción',
            'complicaciones': 'Complicaciones (si las hubo)',
            'estado': 'Estado',
        }


class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ['paciente', 'fecha_hora', 'motivo', 'observaciones']
        widgets = {
            'paciente': forms.Select(attrs={'class': 'form-control'}),
            'fecha_hora': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'paciente': 'Paciente',
            'fecha_hora': 'Fecha y Hora',
            'motivo': 'Motivo de la Consulta',
            'observaciones': 'Observaciones',
        }

    def __init__(self, *args, **kwargs):
        profesional = kwargs.pop('profesional', None)
        super().__init__(*args, **kwargs)
        if profesional:
            # Filtrar solo los pacientes del profesional o todos si es administrador
            self.fields['paciente'].queryset = Paciente.objects.all()


class TurnoPacienteForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ['profesional', 'fecha_hora', 'motivo']
        widgets = {
            'profesional': forms.Select(attrs={'class': 'form-control'}),
            'fecha_hora': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'profesional': 'Profesional',
            'fecha_hora': 'Fecha y Hora Preferida',
            'motivo': 'Motivo de la Consulta',
        }


# Formulario para búsqueda de pacientes
class BuscarPacienteForm(forms.Form):
    cedula = forms.CharField(
        max_length=20, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar por cédula'})
    )
    nombre = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar por nombre'})
    )