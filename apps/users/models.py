from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class HospitalAdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    cargo = models.CharField(max_length=100)
    # telefono_hospital = models.CharField(max_length=20, blank=True)
    # departamento = models.CharField(max_length=100, blank=True)

class Person(models.Model):
    """Abstract base with common person fields shared by Paciente and Profesional."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    codigo_postal = models.CharField(max_length=20, blank=True)

    class Meta:
        abstract = True

    # Expose name/email fields via properties that delegate to the related User
    @property
    def nombres(self):
        return self.user.first_name

    @nombres.setter
    def nombres(self, value):
        self.user.first_name = value
        self.user.save(update_fields=['first_name'])

    @property
    def apellidos(self):
        return self.user.last_name

    @apellidos.setter
    def apellidos(self, value):
        self.user.last_name = value
        self.user.save(update_fields=['last_name'])

    @property
    def email(self):
        return self.user.email

    @email.setter
    def email(self, value):
        self.user.email = value
        self.user.save(update_fields=['email'])

    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Paciente(Person):
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

    # Identificadores únicos
    cedula = models.CharField(max_length=20, unique=True)

    # Datos personales específicos
    genero = models.CharField(max_length=10, choices=GENDER_CHOICES)
    fecha_nacimiento = models.DateField()
    tipo_sangre = models.CharField(max_length=3, choices=TIPOS_SANGRE, blank=True)

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"

    def save(self, *args, **kwargs):
        # Sincronizar email entre User y Paciente: si paciente.email está definido,
        # lo copiamos a user.email; si no, y user.email existe, lo copiamos a paciente.email.
        if hasattr(self, 'user') and self.user:
            try:
                if self.email:
                    if self.user.email != self.email:
                        self.user.email = self.email
                        self.user.save(update_fields=['email'])
                else:
                    # copiar desde user si paciente.email está vacío
                    if self.user.email:
                        self.email = self.user.email
            except Exception:
                # en caso de problemas con la relación user, continuar y guardar paciente
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

    def get_edad(self):
        """Calcula la edad del paciente"""
        from datetime import date
        today = date.today()
        return today.year - self.fecha_nacimiento.year - ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))

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


class Profesional(Person):
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

    especialidad = models.CharField(max_length=50, choices=ESPECIALIDADES)
    matricula = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20)
    consultorio = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Dr/a. {self.user.first_name} {self.user.last_name} - {self.get_especialidad_display()}"
