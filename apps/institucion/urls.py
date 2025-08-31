from django.urls import path
from . import views

urlpatterns = [
    path('registrar/enfermero/', views.registrar_enfermero, name='registrar_enfermero'),
    path('registrar/operario/', views.registrar_operario, name='registrar_operario'),
    path('registrar/sala/', views.registrar_sala, name='registrar_sala'),
    path('registrar/cama/', views.registrar_cama, name='registrar_cama'),
    path('lista/sala/', views.lista_salas, name='lista_salas'),
    path('management/', views.institutional_management, name='institutional_management'),
]