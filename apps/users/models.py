from django.db import models
from django.contrib.auth.models import User
from pytz import timezone



class UserProfile(models.Model):
    """Perfil básico para usuarios del sistema core"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.CharField(max_length=255, blank=True, help_text="URL del avatar")
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile of {self.user.username}"


class HospitalAdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    cargo = models.CharField(max_length=100)
    #telefono_hospital = models.CharField(max_length=20, blank=True)
    #departamento = models.CharField(max_length=100, blank=True)
    #hash_registro = models.CharField(max_length=255, blank=True)


class Paciente(models.Model):
    """Modelo principal de Paciente del sistema médico"""
    GENDER_CHOICES = [
        ('male', 'Masculino'),
        ('female', 'Femenino'),
        ('other', 'Otro'),
        ('unknown', 'Desconocido'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
        ('suspended', 'Suspendido'),
    ]
    
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
    
    # Relación con usuario de Django
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Identificadores únicos
    cedula = models.CharField(max_length=20, unique=True)
    
    # Datos personales
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    genero = models.CharField(max_length=10, choices=GENDER_CHOICES)
    fecha_nacimiento = models.DateField()
    tipo_sangre = models.CharField(max_length=3, choices=TIPOS_SANGRE, blank=True)
    
    # Contacto
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    # Dirección
    direccion = models.TextField(blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    codigo_postal = models.CharField(max_length=20, blank=True)
    
    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.nombres} {self.apellidos}"
    
    def get_full_name(self):
        return f"{self.nombres} {self.apellidos}"
    
    def get_edad(self):
        """Calcula la edad del paciente"""
        from datetime import date
        today = date.today()
        return today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
    
    def generate_blockchain_data(self):
        """Genera datos estructurados para blockchain"""
    def generate_blockchain_data(self):
        """Genera datos estructurados para blockchain"""
        return {
            'resource_type': 'Patient',
            'cedula': self.cedula,
            'name': self.get_full_name(),
            'gender': self.genero,
            'birth_date': str(self.fecha_nacimiento),
            'tipo_sangre': self.tipo_sangre,
            'phone': self.telefono,
            'timestamp': str(timezone.now())
        }


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
