from django.urls import path
from . import views


app_name = 'core'

urlpatterns = [
    # Páginas principales
    path('', views.index, name='index'),
    
    # Paneles de usuario
    path('panel-paciente/', views.panel_paciente, name='panel_paciente'),
    path('panel-profesional/', views.panel_profesional, name='panel_profesional'),
    
    # Perfiles y gestión de pacientes
    path('perfil-paciente/', views.perfil_paciente, name='mi_perfil_paciente'),
    path('perfil-paciente/<int:paciente_id>/', views.perfil_paciente, name='perfil_paciente'),
    path('buscar-pacientes/', views.buscar_pacientes, name='buscar_pacientes'),
    
    # Registro de usuarios
    path('registro-paciente/', views.registro_paciente, name='registro_paciente'),
    path('registro-profesional/', views.registro_profesional, name='registro_profesional'),
    
    # Formularios para agregar información médica
    path('paciente/<int:paciente_id>/agregar-alergia/', views.agregar_alergia, name='agregar_alergia'),
    path('paciente/<int:paciente_id>/agregar-condicion/', views.agregar_condicion, name='agregar_condicion'),
    path('paciente/<int:paciente_id>/agregar-tratamiento/', views.agregar_tratamiento, name='agregar_tratamiento'),
    
    # APIs para datos dinámicos
    path('api/mis-turnos/', views.api_turnos_paciente, name='api_turnos_paciente'),
    path('api/mi-historial/', views.api_historial_paciente, name='api_historial_paciente'),
    path('api/turnos-profesional/', views.api_turnos_profesional, name='api_turnos_profesional'),
    
    # APIs AJAX para panel profesional
    path('panel-profesional/turnos/', views.obtener_turnos_fecha, name='obtener_turnos_fecha'),
    path('panel-profesional/turnos/<int:turno_id>/atender/', views.marcar_turno_atendido, name='marcar_turno_atendido'),
    path('panel-profesional/turnos/<int:turno_id>/reprogramar/', views.reprogramar_turno, name='reprogramar_turno'),
]