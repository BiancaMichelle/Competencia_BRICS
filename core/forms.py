from django import forms

# Todos los formularios relacionados con modelos médicos
# (PacienteForm, ProfesionalForm, AlergiaForm, etc.)
# han sido movidos al módulo blockchain: apps/blockchain/forms.py

# Este archivo se mantiene para futuros formularios
# específicos del módulo core si son necesarios.

# Ejemplo de formulario básico que podría quedarse en el core:
class ContactoForm(forms.Form):
    """Formulario de contacto general del sistema"""
    nombre = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre completo'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'tu@email.com'})
    )
    mensaje = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 4, 
            'placeholder': 'Escribe tu mensaje aquí...'
        })
    )
