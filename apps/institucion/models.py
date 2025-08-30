from django.db import models

# Create your models here.
class Enfermero(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100)
    turno = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Operario(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    turno = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
class Sala(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    capacidad = models.PositiveIntegerField()

    def __str__(self):
        return f"Sala {self.nombre} (Capacidad: {self.capacidad})"


class Cama(models.Model):
    ESTADO_CAMA = [
        ('disponible', 'Disponible'),
        ('ocupada', 'Ocupada'),
    ]
    numero = models.PositiveIntegerField()
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name='camas')
    estado = models.CharField(max_length=20, choices=ESTADO_CAMA, default='disponible')
    enfermero_asignado = models.ForeignKey(
        Enfermero,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='camas'
    )

    def __str__(self):
        enfermero = f" - Enfermero: {self.enfermero_asignado}" if self.enfermero_asignado else " - Sin enfermero asignado"
        return f"Cama {self.numero} en {self.sala.nombre} ({self.estado}){enfermero}"