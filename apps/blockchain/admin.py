from django.contrib import admin
from .models import (
    Block, Paciente, Profesional, Alergia, CondicionMedica, 
    Medicamento, Tratamiento, Antecedente, PruebaLaboratorio, 
    Cirugia, Turno, BlockchainHash, MedicalRecordVersion
)

# NOTA: BlockchainTransaction ELIMINADO - No se usaba en el sistema


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


# MedicalRecordAdmin y BlockchainTransactionAdmin ELIMINADOS

# ===========================================
# ADMINISTRACIÓN DE MODELOS MÉDICOS
# ===========================================

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    """Admin para el modelo principal de Paciente"""
    list_display = ['cedula', 'nombres', 'apellidos', 'genero', 'tipo_sangre']
    search_fields = ['cedula', 'nombres', 'apellidos', 'telefono']
    list_filter = ['genero', 'tipo_sangre']
    
    def get_blockchain_status(self, obj):
        """Muestra el estado del blockchain para el paciente"""
        try:
            blockchain_hash = BlockchainHash.objects.get(
                content_type='Paciente',
                object_id=obj.pk
            )
            return f"Hash: {blockchain_hash.hash_value[:16]}... ✓"
        except BlockchainHash.DoesNotExist:
            return "Sin hash blockchain ✗"
    
    get_blockchain_status.short_description = "Estado Blockchain"


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
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('paciente__user')
    
    def paciente_nombre(self, obj):
        try:
            return obj.paciente.get_full_name()
        except Exception:
            return str(obj.paciente) if obj.paciente else ''
    paciente_nombre.admin_order_field = 'paciente__nombres'
    paciente_nombre.short_description = 'Paciente'

    def paciente_email(self, obj):
        try:
            return obj.paciente.user.email
        except Exception:
            return obj.paciente.email if obj.paciente else ''
    paciente_email.short_description = 'Email paciente'


@admin.register(CondicionMedica)
class CondicionMedicaAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'codigo', 'estado', 'fecha_diagnostico']
    search_fields = ['paciente__user__first_name', 'paciente__user__last_name', 'codigo']
    list_filter = ['estado', 'fecha_diagnostico']
    
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
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('paciente__user', 'profesional__user', 'medicamento')


@admin.register(Antecedente)
class AntecedenteAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'tipo', 'descripcion', 'fecha_evento']
    search_fields = ['paciente__user__first_name', 'paciente__user__last_name']
    list_filter = ['tipo', 'fecha_evento']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('paciente__user')

    
    def user_email(self, obj):
        try:
            return obj.user.email
        except Exception:
            return obj.email
    user_email.short_description = 'Email'

@admin.register(PruebaLaboratorio)
class PruebaLaboratorioAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'nombre_prueba', 'fecha_realizacion', 'profesional']
    search_fields = ['paciente__user__first_name', 'paciente__user__last_name', 'nombre_prueba']
    list_filter = ['fecha_realizacion', 'profesional__especialidad']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('paciente__user', 'profesional__user')


@admin.register(Cirugia)
class CirugiaAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'nombre_cirugia', 'fecha_cirugia', 'profesional', 'estado']
    search_fields = ['paciente__user__first_name', 'paciente__user__last_name', 'nombre_cirugia']
    list_filter = ['estado', 'fecha_cirugia', 'profesional__especialidad']
    
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


# ===========================================
# ADMINISTRACIÓN DE MODELOS FHIR
# ===========================================

@admin.register(BlockchainHash)
class BlockchainHashAdmin(admin.ModelAdmin):
    list_display = ['content_type', 'object_id', 'hash_short', 'timestamp', 'is_verified']
    list_filter = ['content_type', 'is_verified', 'timestamp']
    search_fields = ['hash_value', 'content_type']
    readonly_fields = ['hash_value', 'timestamp']
    
    def hash_short(self, obj):
        return obj.hash_value[:16] + '...' if len(obj.hash_value) > 16 else obj.hash_value
    hash_short.short_description = 'Hash'


