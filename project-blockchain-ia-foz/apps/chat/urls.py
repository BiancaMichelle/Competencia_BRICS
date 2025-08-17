from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # URLs del módulo chat
    path('', views.chat_view, name='chat_view'),
    path('api/message/', views.send_message, name='send_message'),
    path('api/history/', views.get_chat_history, name='get_chat_history'),
]
