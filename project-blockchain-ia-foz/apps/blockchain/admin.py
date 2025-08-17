from django.contrib import admin
from .models import (
    Block, MedicalRecord, BlockchainTransaction,
    Paciente, Profesional, Alergia, CondicionMedica, 
    Medicamento, Tratamiento, Antecedente, PruebaLaboratorio, 
    Cirugia, Turno
)


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('index', 'timestamp', 'hash_short', 'previous_hash_short')
    list_filter = ('timestamp',)
    search_fields = ('hash', 'previous_hash')
    readonly_fields = ('timestamp', 'hash', 'calculate_hash')
    
    def hash_short(self, obj):
        return obj.hash[:16] + '...' if len(obj.hash) > 16 else obj.hash
    hash_short.short_description = 'Hash'
    
    def previous_hash_short(self, obj):
        return obj.previous_hash[:16] + '...' if len(obj.previous_hash) > 16 else obj.previous_hash
    previous_hash_short.short_description = 'Hash Anterior'


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'tipo_registro', 'hash_short', 'block', 'timestamp')
    list_filter = ('tipo_registro', 'timestamp', 'verificado')
    search_fields = ('paciente__user__first_name', 'paciente__user__last_name', 'tipo_registro')
    readonly_fields = ('hash_registro', 'timestamp')
    
    def hash_short(self, obj):
        return obj.hash_registro[:16] + '...' if len(obj.hash_registro) > 16 else obj.hash_registro
    hash_short.short_description = 'Hash'


@admin.register(BlockchainTransaction)
class BlockchainTransactionAdmin(admin.ModelAdmin):
    list_display = ('from_address', 'to_address', 'amount', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('from_address', 'to_address')
    readonly_fields = ('timestamp',)


# ===========================================
# ADMINISTRACIÓN DE MODELOS MÉDICOS
# ===========================================

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ['user', 'cedula', 'fecha_nacimiento', 'tipo_sangre', 'telefono']
    search_fields = ['user__first_name', 'user__last_name', 'cedula']
    list_filter = ['tipo_sangre', 'fecha_nacimiento']
    readonly_fields = ['blockchain_hash', 'ultimo_bloque_actualizado', 'fecha_ultimo_hash']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('user', 'cedula', 'fecha_nacimiento', 'telefono', 'direccion')
        }),
        ('Información Médica', {
            'fields': ('tipo_sangre',)
        }),
        ('Blockchain', {
            'fields': ('blockchain_hash', 'ultimo_bloque_actualizado', 'fecha_ultimo_hash'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Profesional)
class ProfesionalAdmin(admin.ModelAdmin):
    list_display = ['user', 'especialidad', 'matricula', 'telefono']
    search_fields = ['user__first_name', 'user__last_name', 'matricula']
    list_filter = ['especialidad']
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('user', 'matricula', 'telefono', 'direccion')
        }),
        ('Información Profesional', {
            'fields': ('especialidad', 'experiencia', 'descripcion')
        }),
    )


@admin.register(Alergia)
class AlergiaAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'sustancia', 'severidad', 'fecha_diagnostico']
    search_fields = ['paciente__user__first_name', 'paciente__user__last_name', 'sustancia']
    list_filter = ['severidad', 'fecha_diagnostico']
    readonly_fields = ['blockchain_hash']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('paciente__user')


@admin.register(CondicionMedica)
class CondicionMedicaAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'nombre', 'estado', 'fecha_diagnostico']
    search_fields = ['paciente__user__first_name', 'paciente__user__last_name', 'nombre']
    list_filter = ['estado', 'fecha_diagnostico']
    readonly_fields = ['blockchain_hash']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('paciente__user')


@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'principio_activo', 'concentracion', 'forma_farmaceutica']
    search_fields = ['nombre', 'principio_activo']
    list_filter = ['forma_farmaceutica']


@admin.register(Tratamiento)
class TratamientoAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'profesional', 'medicamento', 'fecha_inicio', 'fecha_fin', 'activo']
    search_fields = ['paciente__user__first_name', 'paciente__user__last_name']
    list_filter = ['activo', 'fecha_inicio', 'profesional__especialidad']
    readonly_fields = ['blockchain_hash']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('paciente__user', 'profesional__user', 'medicamento')


@admin.register(Antecedente)
class AntecedenteAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'tipo', 'descripcion', 'fecha_evento']
    search_fields = ['paciente__user__first_name', 'paciente__user__last_name']
    list_filter = ['tipo', 'fecha_evento']
    readonly_fields = ['blockchain_hash']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('paciente__user')


@admin.register(PruebaLaboratorio)
class PruebaLaboratorioAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'nombre_prueba', 'fecha_realizacion', 'profesional']
    search_fields = ['paciente__user__first_name', 'paciente__user__last_name', 'nombre_prueba']
    list_filter = ['fecha_realizacion', 'profesional__especialidad']
    readonly_fields = ['blockchain_hash']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('paciente__user', 'profesional__user')


@admin.register(Cirugia)
class CirugiaAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'nombre_cirugia', 'fecha_cirugia', 'profesional', 'estado']
    search_fields = ['paciente__user__first_name', 'paciente__user__last_name', 'nombre_cirugia']
    list_filter = ['estado', 'fecha_cirugia', 'profesional__especialidad']
    readonly_fields = ['blockchain_hash']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('paciente__user', 'profesional__user')


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'profesional', 'fecha_hora', 'estado', 'motivo_corto']
    search_fields = ['paciente__user__first_name', 'paciente__user__last_name', 'profesional__user__first_name', 'profesional__user__last_name']
    list_filter = ['estado', 'fecha_hora', 'profesional__especialidad']
    date_hierarchy = 'fecha_hora'
    
    def motivo_corto(self, obj):
        return obj.motivo[:50] + '...' if len(obj.motivo) > 50 else obj.motivo
    motivo_corto.short_description = 'Motivo'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('paciente__user', 'profesional__user')
    
    fieldsets = (
        ('Información del Turno', {
            'fields': ('paciente', 'profesional', 'fecha_hora', 'estado')
        }),
        ('Detalles', {
            'fields': ('motivo', 'observaciones')
        }),
    )
