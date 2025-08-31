from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Paciente, Profesional, Alergia, CondicionMedica, Tratamiento, PruebaLaboratorio, Cirugia, Medicamento


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
            'cedula': 'Identity card',
            'fecha_nacimiento': 'Date of Birth',
            'telefono': 'Phone',
            'direccion': 'Address',
            'tipo_sangre': 'Blood Type',
        }


class PacienteRegistroForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label='First Name')
    last_name = forms.CharField(max_length=30, required=True, label='Last Name')
    email = forms.EmailField(required=True, label='Email Address')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        labels = {
            'username': 'Username',
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
            'especialidad': 'Specialty',
            'matricula': 'Registration Number',
            'telefono': 'Phone',
            'consultorio': 'Office',
        }


class ProfesionalRegistroForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label='First Name')
    last_name = forms.CharField(max_length=30, required=True, label='Last Name')
    email = forms.EmailField(required=True, label='Email Address')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        labels = {
            'username': 'Username',
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
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by IC'})
    )
    nombre = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by name'})
    )


# Formularios médicos
class AlergiaForm(forms.ModelForm):
    class Meta:
        model = Alergia
        fields = ['sustancia', 'descripcion', 'severidad', 'fecha_diagnostico']
        widgets = {
            'sustancia': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'EX: Penicillin, pollen, peanuts'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'rows': 3,
                'placeholder': 'Describe the symptoms and reactions'
            }),
            'severidad': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            }),
            'fecha_diagnostico': forms.DateInput(attrs={
                'type': 'date',
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            }),
        }
        labels = {
            'sustancia': 'Allergen Substance',
            'descripcion': 'Description',
            'severidad': 'Severity',
            'fecha_diagnostico': 'Diagnosis Date',
        }


class CondicionMedicaForm(forms.ModelForm):
    class Meta:
        model = CondicionMedica
        fields = ['codigo', 'descripcion', 'fecha_diagnostico', 'estado']
        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Ej: J00-J99 (Enfermedades respiratorias)'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'rows': 3,
                'placeholder': 'Describa la condición médica'
            }),
            'fecha_diagnostico': forms.DateInput(attrs={
                'type': 'date',
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            }),
            'estado': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            }),
        }
        labels = {
            'codigo': 'CIE-10 Code',
            'descripcion': 'Description',
            'fecha_diagnostico': 'Diagnosis Date',
            'estado': 'Status',
        }


class TratamientoForm(forms.ModelForm):
    class Meta:
        model = Tratamiento
        fields = ['medicamento', 'descripcion', 'dosis', 'frecuencia', 'fecha_inicio', 'fecha_fin', 'observaciones']
        widgets = {
            'medicamento': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'rows': 3,
                'placeholder': 'Describe the treatment'
            }),
            'dosis': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'EX: 500mg, 10ml'
            }),
            'frecuencia': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'EX: Twice a day, every 8 hours'
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'type': 'date',
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            }),
            'fecha_fin': forms.DateInput(attrs={
                'type': 'date',
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'rows': 2,
                'placeholder': 'Additional observations'
            }),
        }
        labels = {
            'medicamento': 'Medication',
            'descripcion': 'Treatment Description',
            'dosis': 'Dosage',
            'frecuencia': 'Frequency',
            'fecha_inicio': 'Start Date',
            'fecha_fin': 'End Date',
            'observaciones': 'Observations',
        }


class PruebaLaboratorioForm(forms.ModelForm):
    class Meta:
        model = PruebaLaboratorio
        fields = ['nombre_prueba', 'fecha_realizacion', 'resultados', 'valores_referencia', 'observaciones', 'archivo_resultado']
        widgets = {
            'nombre_prueba': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'EX: complete blood count, blood glucose'
            }),
            'fecha_realizacion': forms.DateInput(attrs={
                'type': 'date',
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            }),
            'resultados': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'rows': 4,
                'placeholder': 'Enter the test results'
            }),
            'valores_referencia': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'rows': 3,
                'placeholder': 'Normal reference values'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'rows': 2,
                'placeholder': 'Professional observations'
            }),
            'archivo_resultado': forms.FileInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            }),
        }
        labels = {
            'nombre_prueba': 'Test Name',
            'fecha_realizacion': 'Date of Performance',
            'resultados': 'Results',
            'valores_referencia': 'Reference Values',
            'observaciones': 'Observations',
            'archivo_resultado': 'Result File',
        }


class CirugiaForm(forms.ModelForm):
    class Meta:
        model = Cirugia
        fields = ['nombre_cirugia', 'fecha_cirugia', 'descripcion', 'complicaciones', 'estado']
        widgets = {
            'nombre_cirugia': forms.TextInput(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'EX: Appendectomy, Cesarean section'
            }),
            'fecha_cirugia': forms.DateInput(attrs={
                'type': 'date',
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'rows': 4,
                'placeholder': 'Describe the surgical procedure'
            }),
            'complicaciones': forms.Textarea(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500',
                'rows': 3,
                'placeholder': 'Postoperative complications (if any)'
            }),
            'estado': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500'
            }),
        }
        labels = {
            'nombre_cirugia': 'Surgery Name',
            'fecha_cirugia': 'Surgery Date',
            'descripcion': 'Description',
            'complicaciones': 'Complications',
            'estado': 'Status',
        }