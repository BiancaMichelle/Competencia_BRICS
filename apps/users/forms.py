from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Paciente, Profesional


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "is_active", "is_staff"]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'email': forms.EmailInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'first_name': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'last_name': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'h-4 w-4'}),
        }


class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['cedula', 'fecha_nacimiento', 'telefono', 'direccion', 'tipo_sangre']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'}),
            'cedula': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500', 'placeholder': 'Ej: 1234567-8'}),
            'telefono': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500', 'placeholder': 'Ej: +595 21 123456'}),
            'direccion': forms.Textarea(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500', 'rows': 3}),
            'tipo_sangre': forms.Select(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'}),
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
        tailwind_classes = 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
        for field in self.fields.values():
            field.widget.attrs['class'] = tailwind_classes


class ProfesionalForm(forms.ModelForm):
    class Meta:
        model = Profesional
        fields = ['especialidad', 'matricula', 'telefono', 'consultorio']
        widgets = {
            'especialidad': forms.Select(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'}),
            'matricula': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500', 'placeholder': 'Ej: MP-12345'}),
            'telefono': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500', 'placeholder': 'Ej: +595 21 123456'}),
            'consultorio': forms.TextInput(attrs={'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500', 'placeholder': 'Ej: Consultorio 201'}),
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
        tailwind_classes = 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
        for field in self.fields.values():
            field.widget.attrs['class'] = tailwind_classes

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
