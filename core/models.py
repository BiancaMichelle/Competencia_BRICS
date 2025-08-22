from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ContactMessage(models.Model):
    """Modelo básico para mensajes de contacto del core"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.subject}"
    
    class Meta:
        ordering = ['-timestamp']

