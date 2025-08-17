from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class ChatMessage(models.Model):
    """Modelo para almacenar mensajes del chat"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True,  # Permitir NULL temporalmente
        blank=True,  # Permitir vacío en formularios
        verbose_name="Usuario"
    )
    user_message = models.TextField(verbose_name="Mensaje del usuario", help_text="Mensaje enviado por el usuario")
    ai_response = models.TextField(verbose_name="Respuesta de la IA", help_text="Respuesta generada por la IA")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y hora")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Fecha de creación")
    session_key = models.CharField(
        max_length=40, 
        null=True, 
        blank=True, 
        help_text="ID de sesión del usuario",
        verbose_name="Clave de sesión"
    )
    
    class Meta:
        verbose_name = "Mensaje de Chat"
        verbose_name_plural = "Mensajes de Chat"
        ordering = ['-timestamp', '-created_at']
    
    def __str__(self):
        username = self.user.username if self.user else "Anónimo"
        return f"{username} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"