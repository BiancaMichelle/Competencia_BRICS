from django.urls import path
from . import views


app_name = 'users'

urlpatterns = [
    
    # Vistas de paciente principales
    path("", views.user_list, name="user_list"),
    path('me/', views.perfil_paciente, name='mi_perfil'),
    path('<int:paciente_id>/', views.perfil_paciente, name='perfil_paciente'),
    path("<int:user_id>/delete/", views.user_delete, name="user_delete"),
    
    # Vistas médicas principales
    path('panel-profesional/', views.panel_profesional, name='panel_profesional'),
    path('buscar-pacientes/', views.buscar_pacientes, name='buscar_pacientes'),
    
    # Registro
    path('registro-paciente/', views.registro_paciente, name='registro_paciente'),
    path('registro-profesional/', views.registro_profesional, name='registro_profesional'),
    path('admin/registro-profesional/', views.registro_profesional, name='admin_registro_profesional'),
    
]
