from django.urls import path
from . import views

app_name = 'blockchain'

urlpatterns = [
    # Vistas médicas principales
    path('panel-paciente/', views.panel_paciente, name='panel_paciente'),
    path('panel-profesional/', views.panel_profesional, name='panel_profesional'),
    path('perfil-paciente/', views.perfil_paciente, name='perfil_paciente'),
    path('perfil-paciente/<int:paciente_id>/', views.perfil_paciente, name='perfil_paciente_detalle'),
    path('buscar-pacientes/', views.buscar_pacientes, name='buscar_pacientes'),
    
    # APIs médicas
    path('api/historial-paciente/', views.api_historial_paciente, name='api_historial_paciente'),
    path('api/agregar-alergia/<int:paciente_id>/', views.agregar_alergia, name='agregar_alergia'),
    path('api/agregar-condicion/<int:paciente_id>/', views.agregar_condicion, name='agregar_condicion'),
    path('api/agregar-tratamiento/<int:paciente_id>/', views.agregar_tratamiento, name='agregar_tratamiento'),
    
    # Registro
    path('registro-paciente/', views.registro_paciente, name='registro_paciente'),
    path('registro-profesional/', views.registro_profesional, name='registro_profesional'),
    
    # URLs específicas para blockchain
    path('dashboard/', views.blockchain_dashboard, name='blockchain_dashboard'),
    path('verify/', views.verify_blockchain, name='verify_blockchain'),
    path('patient-history/<int:paciente_id>/', views.get_patient_blockchain_history, name='patient_blockchain_history'),
]