from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json
import hashlib

class Paciente(models.Model):
    TIPOS_SANGRE = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cedula = models.CharField(max_length=20, unique=True)
    fecha_nacimiento = models.DateField()
    telefono = models.CharField(max_length=20)
    direccion = models.TextField()
    tipo_sangre = models.CharField(max_length=3, choices=TIPOS_SANGRE, blank=True)
    
    # Campos para blockchain
    blockchain_hash = models.CharField(max_length=64, blank=True, null=True)
    ultimo_bloque_actualizado = models.CharField(max_length=64, blank=True, null=True)
    fecha_ultimo_hash = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    def get_edad(self):
        from datetime import date
        today = date.today()
        return today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
    
    def generar_hash_blockchain(self):
        """Genera un hash para el blockchain basado en los datos del paciente"""
        data = {
            'cedula': self.cedula,
            'nombre': f"{self.user.first_name} {self.user.last_name}",
            'fecha_nacimiento': str(self.fecha_nacimiento),
            'tipo_sangre': self.tipo_sangre,
            'timestamp': str(timezone.now())
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


class Profesional(models.Model):
    ESPECIALIDADES = [
        ('cardiologia', 'Cardiología'),
        ('dermatologia', 'Dermatología'),
        ('endocrinologia', 'Endocrinología'),
        ('gastroenterologia', 'Gastroenterología'),
        ('ginecologia', 'Ginecología'),
        ('neurologia', 'Neurología'),
        ('nutricion', 'Nutrición'),
        ('oftalmologia', 'Oftalmología'),
        ('pediatria', 'Pediatría'),
        ('psiquiatria', 'Psiquiatría'),
        ('traumatologia', 'Traumatología'),
        ('urologia', 'Urología'),
        ('medicina_general', 'Medicina General'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    especialidad = models.CharField(max_length=50, choices=ESPECIALIDADES)
    matricula = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20)
    consultorio = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Dr/a. {self.user.first_name} {self.user.last_name} - {self.get_especialidad_display()}"


class Alergia(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='alergias')
    sustancia = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    severidad = models.CharField(max_length=20, choices=[
        ('leve', 'Leve'),
        ('moderada', 'Moderada'),
        ('grave', 'Grave'),
        ('muy_grave', 'Muy Grave')
    ], default='leve')
    fecha_diagnostico = models.DateField()
    
    # Campos para blockchain
    blockchain_hash = models.CharField(max_length=64, blank=True, null=True)
    
    def __str__(self):
        return f"{self.paciente} - Alergia a {self.sustancia}"


class CondicionMedica(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='condiciones')
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    fecha_diagnostico = models.DateField()
    estado = models.CharField(max_length=20, choices=[
        ('activa', 'Activa'),
        ('controlada', 'Controlada'),
        ('remision', 'En Remisión'),
        ('curada', 'Curada')
    ], default='activa')
    
    # Campos para blockchain
    blockchain_hash = models.CharField(max_length=64, blank=True, null=True)
    
    def __str__(self):
        return f"{self.paciente} - {self.nombre}"


class Medicamento(models.Model):
    nombre = models.CharField(max_length=200)
    principio_activo = models.CharField(max_length=200)
    concentracion = models.CharField(max_length=50)
    forma_farmaceutica = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.nombre} ({self.concentracion})"


class Tratamiento(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='tratamientos')
    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE)
    medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE, null=True, blank=True)
    descripcion = models.TextField()
    dosis = models.CharField(max_length=100, blank=True)
    frecuencia = models.CharField(max_length=100, blank=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    observaciones = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    
    # Campos para blockchain
    blockchain_hash = models.CharField(max_length=64, blank=True, null=True)
    
    def __str__(self):
        return f"{self.paciente} - {self.descripcion[:50]}"


class Antecedente(models.Model):
    TIPOS_ANTECEDENTE = [
        ('familiar', 'Familiar'),
        ('personal', 'Personal'),
        ('quirurgico', 'Quirúrgico'),
        ('alergico', 'Alérgico'),
        ('farmacologico', 'Farmacológico'),
    ]
    
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='antecedentes')
    tipo = models.CharField(max_length=20, choices=TIPOS_ANTECEDENTE)
    descripcion = models.TextField()
    fecha_evento = models.DateField(null=True, blank=True)
    observaciones = models.TextField(blank=True)
    
    # Campos para blockchain
    blockchain_hash = models.CharField(max_length=64, blank=True, null=True)
    
    def __str__(self):
        return f"{self.paciente} - {self.get_tipo_display()}: {self.descripcion[:50]}"


class PruebaLaboratorio(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='pruebas')
    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE)
    nombre_prueba = models.CharField(max_length=200)
    fecha_realizacion = models.DateField()
    resultados = models.TextField()
    valores_referencia = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)
    archivo_resultado = models.FileField(upload_to='pruebas_laboratorio/', blank=True, null=True)
    
    # Campos para blockchain
    blockchain_hash = models.CharField(max_length=64, blank=True, null=True)
    
    def __str__(self):
        return f"{self.paciente} - {self.nombre_prueba} ({self.fecha_realizacion})"


class Cirugia(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='cirugias')
    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE)
    nombre_cirugia = models.CharField(max_length=200)
    fecha_cirugia = models.DateField()
    descripcion = models.TextField()
    complicaciones = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=[
        ('programada', 'Programada'),
        ('realizada', 'Realizada'),
        ('cancelada', 'Cancelada'),
        ('postergada', 'Postergada')
    ], default='programada')
    
    # Campos para blockchain
    blockchain_hash = models.CharField(max_length=64, blank=True, null=True)
    
    def __str__(self):
        return f"{self.paciente} - {self.nombre_cirugia} ({self.fecha_cirugia})"


class Turno(models.Model):
    ESTADOS_TURNO = [
        ('programado', 'Programado'),
        ('confirmado', 'Confirmado'),
        ('en_curso', 'En Curso'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
        ('no_asistio', 'No Asistió')
    ]
    
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='turnos')
    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE, related_name='turnos')
    fecha_hora = models.DateTimeField()
    motivo = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADOS_TURNO, default='programado')
    observaciones = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.paciente} - {self.profesional} ({self.fecha_hora})"
    
    class Meta:
        ordering = ['fecha_hora']
        

# modelo para el chat
class ChatMessage(models.Model):
    """
    Modelo para almacenar mensajes del chat (opcional)
    Este modelo se puede usar si quieres guardar el historial de conversaciones
    """
    user_message = models.TextField(help_text="Mensaje del usuario")
    ai_response = models.TextField(help_text="Respuesta de la IA")
    created_at = models.DateTimeField(default=timezone.now)
    session_key = models.CharField(max_length=40, null=True, blank=True, help_text="ID de sesión del usuario")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Mensaje de Chat"
        verbose_name_plural = "Mensajes de Chat"
    
    def __str__(self):
        return f"Chat - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
