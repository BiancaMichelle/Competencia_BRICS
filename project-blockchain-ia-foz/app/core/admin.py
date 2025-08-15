from django.contrib import admin
from .models import (
    Paciente, Profesional, Alergia, CondicionMedica, 
    Medicamento, Tratamiento, Antecedente, PruebaLaboratorio, 
    Cirugia, Turno
)

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ['user', 'cedula', 'fecha_nacimiento', 'tipo_sangre', 'telefono']
    search_fields = ['user__first_name', 'user__last_name', 'cedula']
    list_filter = ['tipo_sangre', 'fecha_nacimiento']
    readonly_fields = ['blockchain_hash', 'ultimo_bloque_actualizado', 'fecha_ultimo_hash']

@admin.register(Profesional)
class ProfesionalAdmin(admin.ModelAdmin):
    list_display = ['user', 'especialidad', 'matricula', 'telefono']
    search_fields = ['user__first_name', 'user__last_name', 'matricula']
    list_filter = ['especialidad']

@admin.register(Alergia)
class AlergiaAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'sustancia', 'severidad', 'fecha_diagnostico']
    search_fields = ['paciente__user__first_name', 'paciente__user__last_name', 'sustancia']
    list_filter = ['severidad', 'fecha_diagnostico']
    readonly_fields = ['blockchain_hash']

@admin.register(CondicionMedica)
class CondicionMedicaAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'nombre', 'estado', 'fecha_diagnostico']
    search_fields = ['paciente__user__first_name', 'paciente__user__last_name', 'nombre']
    list_filter = ['estado', 'fecha_diagnostico']
    readonly_fields = ['blockchain_hash']

@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'principio_activo', 'concentracion', 'forma_farmaceutica']
    search_fields = ['nombre', 'principio_activo']

@admin.register(Tratamiento)
class TratamientoAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'profesional', 'medicamento', 'fecha_inicio', 'fecha_fin', 'activo']
    search_fields = ['paciente__user__first_name', 'paciente__user__last_name']
    list_filter = ['activo', 'fecha_inicio', 'profesional__especialidad']
    readonly_fields = ['blockchain_hash']

@admin.register(Antecedente)
class AntecedenteAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'tipo', 'descripcion', 'fecha_evento']
    search_fields = ['paciente__user__first_name', 'paciente__user__last_name']
    list_filter = ['tipo', 'fecha_evento']
    readonly_fields = ['blockchain_hash']

@admin.register(PruebaLaboratorio)
class PruebaLaboratorioAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'nombre_prueba', 'fecha_realizacion', 'profesional']
    search_fields = ['paciente__user__first_name', 'paciente__user__last_name', 'nombre_prueba']
    list_filter = ['fecha_realizacion', 'profesional__especialidad']
    readonly_fields = ['blockchain_hash']

@admin.register(Cirugia)
class CirugiaAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'nombre_cirugia', 'fecha_cirugia', 'profesional', 'estado']
    search_fields = ['paciente__user__first_name', 'paciente__user__last_name', 'nombre_cirugia']
    list_filter = ['estado', 'fecha_cirugia', 'profesional__especialidad']
    readonly_fields = ['blockchain_hash']

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'profesional', 'fecha_hora', 'estado']
    search_fields = ['paciente__user__first_name', 'paciente__user__last_name']
    list_filter = ['estado', 'fecha_hora', 'profesional__especialidad']
    date_hierarchy = 'fecha_hora'