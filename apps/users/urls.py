from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    
    # Vistas de paciente principales
    path("", views.user_list, name="user_list"),
    path('me/', views.perfil_paciente, name='mi_perfil'),
    path('<int:paciente_id>/', views.perfil_paciente, name='perfil_paciente'),
    # path("<int:user_id>/delete/", views.user_delete, name="user_delete"),
    
    # Vistas médicas principales
    path('panel-profesional/', views.panel_profesional, name='panel_profesional'),
    path('buscar-pacientes/', views.buscar_pacientes, name='buscar_pacientes'),
    
    # Medical forms views
    path('<int:paciente_id>/agregar-alergia/', views.agregar_alergia, name='agregar_alergia'),
    path('<int:paciente_id>/agregar-condicion/', views.agregar_condicion, name='agregar_condicion'),
    path('<int:paciente_id>/agregar-tratamiento/', views.agregar_tratamiento, name='agregar_tratamiento'),
    path('<int:paciente_id>/agregar-prueba-laboratorio/', views.agregar_prueba_laboratorio, name='agregar_prueba_laboratorio'),
    path('<int:paciente_id>/agregar-cirugia/', views.agregar_cirugia, name='agregar_cirugia'),
    
    # Medical record detail views
    path('<int:paciente_id>/alergia/<int:alergia_id>/', views.ver_alergia, name='ver_alergia'),
    path('<int:paciente_id>/condicion/<int:condicion_id>/', views.ver_condicion, name='ver_condicion'),
    path('<int:paciente_id>/tratamiento/<int:tratamiento_id>/', views.ver_tratamiento, name='ver_tratamiento'),
    path('<int:paciente_id>/prueba-laboratorio/<int:prueba_id>/', views.ver_prueba_laboratorio, name='ver_prueba_laboratorio'),
    path('<int:paciente_id>/cirugia/<int:cirugia_id>/', views.ver_cirugia, name='ver_cirugia'),
    
    # Blockchain integration
    path('blockchain-status/', views.blockchain_status, name='blockchain_status'),
    path('hash/<int:hash_id>/', views.hash_detail, name='hash_detail'),
    path('hash/value/<str:hash_value>/', views.hash_detail_by_value, name='hash_detail_by_value'),
    path('paciente/<int:paciente_id>/hashes/', views.patient_blockchain_hashes, name='patient_blockchain_hashes'),
    
    # Registration views
    path('registro/paciente/', views.registro_paciente, name='registro_paciente'),
    path('registro/profesional/', views.registro_profesional, name='registro_profesional'),
    
]
