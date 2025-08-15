from django.contrib import admin
from .models import (
    Paciente, Profesional, Alergia, CondicionMedica, 
    Medicamento, Tratamiento, Antecedente, PruebaLaboratorio, 
    Cirugia, Turno, ChatMessage
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
    
@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """
    Administración de mensajes de chat
    """
    list_display = ('created_at', 'user_message_preview', 'ai_response_preview', 'session_key')
    list_filter = ('created_at',)
    search_fields = ('user_message', 'ai_response')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def user_message_preview(self, obj):
        """Mostrar preview del mensaje del usuario"""
        return obj.user_message[:50] + '...' if len(obj.user_message) > 50 else obj.user_message
    user_message_preview.short_description = 'Mensaje Usuario'
    
    def ai_response_preview(self, obj):
        """Mostrar preview de la respuesta de la IA"""
        return obj.ai_response[:50] + '...' if len(obj.ai_response) > 50 else obj.ai_response
    ai_response_preview.short_description = 'Respuesta IA'
