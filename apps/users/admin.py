from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from .models import Paciente, Profesional, Alergia, CondicionMedica, Tratamiento, Antecedente, PruebaLaboratorio, Cirugia, BlockchainHash, AccesoBlockchain
from .views import admin_index


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ['cedula', 'user', 'genero', 'fecha_nacimiento', 'tipo_sangre']
    list_filter = ['genero', 'tipo_sangre', 'fecha_nacimiento']
    search_fields = ['cedula', 'user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['user']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Profesional)
class ProfesionalAdmin(admin.ModelAdmin):
    list_display = ['user', 'especialidad', 'matricula', 'telefono']
    list_filter = ['especialidad']
    search_fields = ['user__first_name', 'user__last_name', 'matricula', 'user__email']
    readonly_fields = ['user']


@admin.register(Alergia)
class AlergiaAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'sustancia', 'severidad', 'fecha_diagnostico']
    list_filter = ['severidad', 'fecha_diagnostico']
    search_fields = ['paciente__cedula', 'paciente__user__first_name', 'paciente__user__last_name', 'sustancia']


@admin.register(CondicionMedica)
class CondicionMedicaAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'codigo', 'estado', 'fecha_diagnostico']
    list_filter = ['estado', 'fecha_diagnostico']
    search_fields = ['paciente__cedula', 'paciente__user__first_name', 'paciente__user__last_name', 'codigo']


@admin.register(Tratamiento)
class TratamientoAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'profesional', 'descripcion', 'activo', 'fecha_inicio']
    list_filter = ['activo', 'fecha_inicio', 'profesional__especialidad']
    search_fields = ['paciente__cedula', 'paciente__user__first_name', 'paciente__user__last_name', 'descripcion']


@admin.register(Antecedente)
class AntecedenteAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'tipo', 'descripcion', 'fecha_evento']
    list_filter = ['tipo', 'fecha_evento']
    search_fields = ['paciente__cedula', 'paciente__user__first_name', 'paciente__user__last_name', 'descripcion']


@admin.register(PruebaLaboratorio)
class PruebaLaboratorioAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'profesional', 'nombre_prueba', 'fecha_realizacion']
    list_filter = ['fecha_realizacion', 'profesional__especialidad']
    search_fields = ['paciente__cedula', 'paciente__user__first_name', 'paciente__user__last_name', 'nombre_prueba']


@admin.register(Cirugia)
class CirugiaAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'profesional', 'nombre_cirugia', 'fecha_cirugia', 'estado']
    list_filter = ['estado', 'fecha_cirugia', 'profesional__especialidad']
    search_fields = ['paciente__cedula', 'paciente__user__first_name', 'paciente__user__last_name', 'nombre_cirugia']


@admin.register(BlockchainHash)
class BlockchainHashAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'categoria', 'hash_value', 'timestamp', 'transaction_hash']
    list_filter = ['categoria', 'timestamp']
    search_fields = ['paciente__cedula', 'paciente__user__first_name', 'paciente__user__last_name', 'hash_value']
    readonly_fields = ['hash_value', 'transaction_hash', 'block_number', 'timestamp']


@admin.register(AccesoBlockchain)
class AccesoBlockchainAdmin(admin.ModelAdmin):
    list_display = ['hash_record', 'profesional', 'fecha_acceso', 'motivo_acceso']
    list_filter = ['fecha_acceso', 'profesional__especialidad']
    search_fields = ['hash_record__paciente__cedula', 'profesional__user__first_name', 'profesional__user__last_name']
    readonly_fields = ['fecha_acceso']


# Configurar el sitio admin personalizado
admin.site.site_header = "ARQA Medical System - Administración"
admin.site.site_title = "ARQA Admin"
admin.site.index_title = "Panel de Administración"

# Personalizar la URL del index del admin
class CustomAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', admin_index, name='index'),
        ]
        return custom_urls + urls

# Crear instancia del sitio admin personalizado
custom_admin_site = CustomAdminSite(name='custom_admin')

# Registrar modelos en el sitio personalizado
custom_admin_site.register(Paciente, PacienteAdmin)
custom_admin_site.register(Profesional, ProfesionalAdmin)
custom_admin_site.register(Alergia, AlergiaAdmin)
custom_admin_site.register(CondicionMedica, CondicionMedicaAdmin)
custom_admin_site.register(Tratamiento, TratamientoAdmin)
custom_admin_site.register(Antecedente, AntecedenteAdmin)
custom_admin_site.register(PruebaLaboratorio, PruebaLaboratorioAdmin)
custom_admin_site.register(Cirugia, CirugiaAdmin)
custom_admin_site.register(BlockchainHash, BlockchainHashAdmin)
custom_admin_site.register(AccesoBlockchain, AccesoBlockchainAdmin)
