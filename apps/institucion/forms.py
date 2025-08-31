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

    def clean(self):
        cleaned_data = super().clean()
        numero = cleaned_data.get('numero')
        sala = cleaned_data.get('sala')

        if sala:
            # Capacidad
            capacidad = sala.capacidad
            camas_existentes = Cama.objects.filter(sala=sala).count()
            if self.instance.pk:
                camas_existentes -= 1
            if camas_existentes >= capacidad:
                raise forms.ValidationError(
                    f"The {sala.nombre} has reached its maximum capacity of {capacidad} beds."
                )

            # Cama única por sala
            if Cama.objects.filter(sala=sala, numero=numero).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError(
                    f"La cama {numero} ya está registrada en la sala {sala.nombre}."
                )

        return cleaned_data
