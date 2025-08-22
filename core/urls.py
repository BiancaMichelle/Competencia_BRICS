from django.urls import path, include
from . import views


app_name = 'core'

urlpatterns = [
    # Páginas principales
    path('', views.index, name='index'),
    path('admin-access-denied/', views.admin_access_denied, name='admin_access_denied'),

]



