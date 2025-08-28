from django.urls import path
from . import views

app_name = 'blockchain'

urlpatterns = [
    # Dashboard principal
    path('', views.blockchain_dashboard, name='dashboard'),
    path('dashboard/', views.blockchain_dashboard, name='blockchain_dashboard'),
        
    # APIs médicas
    path('api/historial-paciente/', views.api_historial_paciente, name='api_historial_paciente'),
    path('api/agregar-alergia/<int:paciente_id>/', views.agregar_alergia, name='agregar_alergia'),
    path('api/agregar-condicion/<int:paciente_id>/', views.agregar_condicion, name='agregar_condicion'),
    path('api/agregar-tratamiento/<int:paciente_id>/', views.agregar_tratamiento, name='agregar_tratamiento'),
    
    # URLs específicas para blockchain
    path('verify/', views.verify_blockchain, name='verify_blockchain'),
    path('patient-history/<int:paciente_id>/', views.get_patient_blockchain_history, name='patient_blockchain_history'),
]