from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import hashlib
import json


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
    
    # Campos para blockchain eliminados - se maneja automáticamente
    
    def __str__(self):
        return f"{self.paciente} - Alergia a {self.sustancia}"


class CondicionMedica(models.Model):
    paciente = models.ForeignKey('Paciente', on_delete=models.CASCADE, related_name='condiciones')
    codigo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    fecha_diagnostico = models.DateField()
    estado = models.CharField(max_length=20, choices=[
        ('activa', 'Activa'),
        ('controlada', 'Controlada'),
        ('remision', 'En Remisión'),
        ('curada', 'Curada')
    ], default='activa')
    
    def __str__(self):
        return f"{self.paciente} - {self.codigo}"


class Medicamento(models.Model):
    nombre = models.CharField(max_length=200)
    principio_activo = models.CharField(max_length=200)
    concentracion = models.CharField(max_length=50)
    forma_farmaceutica = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.nombre} ({self.concentracion})"


class Tratamiento(models.Model):
    paciente = models.ForeignKey('Paciente', on_delete=models.CASCADE, related_name='tratamientos')
    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE)
    medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE, null=True, blank=True)
    descripcion = models.TextField()
    dosis = models.CharField(max_length=100, blank=True)
    frecuencia = models.CharField(max_length=100, blank=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    observaciones = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    
    # Campos para blockchain eliminados - se maneja automáticamente
    
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
    
    paciente = models.ForeignKey('Paciente', on_delete=models.CASCADE, related_name='antecedentes')
    tipo = models.CharField(max_length=20, choices=TIPOS_ANTECEDENTE)
    descripcion = models.TextField()
    fecha_evento = models.DateField(null=True, blank=True)
    observaciones = models.TextField(blank=True)
    
    
    def __str__(self):
        return f"{self.paciente} - {self.get_tipo_display()}: {self.descripcion[:50]}"


class PruebaLaboratorio(models.Model):
    paciente = models.ForeignKey('Paciente', on_delete=models.CASCADE, related_name='pruebas')
    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE)
    nombre_prueba = models.CharField(max_length=200)
    fecha_realizacion = models.DateField()
    resultados = models.TextField()
    valores_referencia = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)
    archivo_resultado = models.FileField(upload_to='pruebas_laboratorio/', blank=True, null=True)
    
    
    def __str__(self):
        return f"{self.paciente} - {self.nombre_prueba} ({self.fecha_realizacion})"


class Cirugia(models.Model):
    paciente = models.ForeignKey('Paciente', on_delete=models.CASCADE, related_name='cirugias')
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
    
    # Campos para blockchain eliminados - se maneja automáticamente
    
    def __str__(self):
        return f"{self.nombre_cirugia} - {self.paciente} ({self.fecha_cirugia})"


class Turno(models.Model):
    ESTADOS_TURNO = [
        ('programado', 'Programado'),
        ('confirmado', 'Confirmado'),
        ('en_curso', 'En Curso'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
        ('no_asistio', 'No Asistió')
    ]
    
    paciente = models.ForeignKey('Paciente', on_delete=models.CASCADE, related_name='turnos')
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


# MODELOS ESPECÍFICOS DE BLOCKCHAIN

class Block(models.Model):
    """Bloque individual en la blockchain"""
    index = models.PositiveIntegerField(unique=True)
    timestamp = models.DateTimeField(default=timezone.now)
    data = models.TextField(help_text="Datos del bloque en formato JSON")
    previous_hash = models.CharField(max_length=64)
    hash = models.CharField(max_length=64, unique=True)
    nonce = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['index']
    
    def calculate_hash(self):
        """Calcula el hash del bloque"""
        data_string = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def mine_block(self, difficulty=2):
        """Mina el bloque con proof of work"""
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
    
    def save(self, *args, **kwargs):
        if not self.hash:
            self.hash = self.calculate_hash()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Block {self.index} - {self.hash[:16]}..."



# MODELO PARA GESTIÓN SEPARADA DE HASHES BLOCKCHAIN
class BlockchainHash(models.Model):
    """Modelo separado para almacenar hashes blockchain de registros médicos"""
    content_type = models.CharField(max_length=50, help_text="Tipo de modelo (Patient, Condition, etc.)")
    object_id = models.PositiveIntegerField(help_text="ID del objeto referenciado")
    hash_value = models.CharField(max_length=64, unique=True)
    previous_hash = models.CharField(max_length=64, blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)
    block_reference = models.ForeignKey(Block, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        unique_together = ('content_type', 'object_id')
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Hash {self.content_type}:{self.object_id} - {self.hash_value[:16]}..."



# SERVICIOS Y UTILIDADES PARA BLOCKCHAIN

class BlockchainService:
    """Servicio para gestionar hashes blockchain separados de los datos médicos"""
    
    @staticmethod
    def generate_hash(model_instance):
        """Genera hash para cualquier modelo FHIR"""
        if hasattr(model_instance, 'generate_blockchain_data'):
            data = model_instance.generate_blockchain_data()
            hash_input = json.dumps(data, sort_keys=True)
            return hashlib.sha256(hash_input.encode()).hexdigest()
        return None
    
    @staticmethod
    def create_blockchain_hash(model_instance):
        """Crea un registro de hash blockchain para un modelo"""
        hash_value = BlockchainService.generate_hash(model_instance)
        if hash_value:
            # Obtener el hash anterior para crear cadena
            content_type = model_instance.__class__.__name__
            previous_hash_obj = BlockchainHash.objects.filter(
                content_type=content_type
            ).order_by('-timestamp').first()
            
            previous_hash = previous_hash_obj.hash_value if previous_hash_obj else "0"
            
            blockchain_hash = BlockchainHash.objects.create(
                content_type=content_type,
                object_id=model_instance.pk,
                hash_value=hash_value,
                previous_hash=previous_hash
            )
            
            return blockchain_hash
        return None
    
    @staticmethod
    def verify_chain_integrity(content_type=None):
        """Verifica la integridad de la cadena de hashes"""
        filters = {}
        if content_type:
            filters['content_type'] = content_type
            
        hashes = BlockchainHash.objects.filter(**filters).order_by('timestamp')
        
        for i, hash_obj in enumerate(hashes):
            if i == 0:
                # Primer hash, debería tener previous_hash = "0" o None
                continue
            
            previous_hash_obj = hashes[i-1]
            if hash_obj.previous_hash != previous_hash_obj.hash_value:
                return False, f"Cadena rota en hash ID {hash_obj.id}"
        
        return True, "Cadena íntegra"


# SIGNALS PARA AUTOMATIZAR CREACIÓN DE HASHES
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Paciente)
def create_patient_hash(sender, instance, created, **kwargs):
    """Crea hash blockchain cuando se crea o actualiza un paciente"""
    if created or kwargs.get('update_fields'):
        BlockchainService.create_blockchain_hash(instance)


# MODELO PARA AUDITORÍA Y VERSIONADO
class MedicalRecordVersion(models.Model):
    """Versiones de registros médicos para auditoría"""
    content_type = models.CharField(max_length=50)
    object_id = models.PositiveIntegerField()
    version_data = models.TextField(help_text="Datos en formato JSON")
    hash_blockchain = models.ForeignKey(BlockchainHash, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Version {self.content_type}:{self.object_id} - {self.created_at}"


# COMPATIBILIDAD CON MODELOS LEGACY - YA NO NECESARIO
# El modelo Paciente ha sido eliminado, ahora Paciente es el modelo principal

class DataMigrationUtils:
    """Utilidades para migración de datos"""
    
    @staticmethod
    def create_patient_from_user(user, cedula, fecha_nacimiento, telefono='', direccion='', tipo_sangre=''):
        """Crea un paciente desde datos básicos"""
        return Paciente.objects.create(
            user=user,
            cedula=cedula,
            nombres=user.first_name,
            apellidos=user.last_name,
            genero='unknown',
            fecha_nacimiento=fecha_nacimiento,
            telefono=telefono,
            direccion=direccion,
            tipo_sangre=tipo_sangre,
            email=user.email or ''
        )