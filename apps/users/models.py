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
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Generar hash génesis si es un nuevo paciente
        if is_new:
            from .blockchain_manager import BlockchainManager
            BlockchainManager.generate_genesis_hash(self)

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

    def store_on_blockchain(self):
        """Store patient data on Polygon/Filecoin"""
        from .blockchain_services import MedicalBlockchainService

        service = MedicalBlockchainService()
        record_data = self.generate_blockchain_data()

        # Get related medical records
        alergias = [a.__dict__ for a in self.alergias.all()]
        condiciones = [c.__dict__ for c in self.condiciones.all()]
        tratamientos = [t.__dict__ for t in self.tratamientos.all()]

        full_record = {
            'patient': record_data,
            'alergias': alergias,
            'condiciones': condiciones,
            'tratamientos': tratamientos
        }

        return service.store_medical_record(self.id, full_record)


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
    
    def __str__(self):
        return f"{self.paciente} - Alergia a {self.sustancia}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Generar hash en blockchain si es un nuevo registro
        if is_new:
            from .blockchain_manager import BlockchainManager
            record_data = {
                'tipo': 'alergia',
                'paciente_id': self.paciente.id,
                'sustancia': self.sustancia,
                'descripcion': self.descripcion,
                'severidad': self.severidad,
                'fecha_diagnostico': str(self.fecha_diagnostico),
                'fecha_registro': str(timezone.now())
            }
            BlockchainManager.store_medical_record(
                paciente=self.paciente,
                categoria='alergia',
                record_id=self.id,
                record_data=record_data
            )


class CondicionMedica(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='condiciones')
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

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Generar hash en blockchain si es un nuevo registro
        if is_new:
            from .blockchain_manager import BlockchainManager
            record_data = {
                'tipo': 'condicion_medica',
                'paciente_id': self.paciente.id,
                'codigo': self.codigo,
                'descripcion': self.descripcion,
                'fecha_diagnostico': str(self.fecha_diagnostico),
                'estado': self.estado,
                'fecha_registro': str(timezone.now())
            }
            BlockchainManager.store_medical_record(
                paciente=self.paciente,
                categoria='condicion',
                record_id=self.id,
                record_data=record_data
            )


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
    
    def __str__(self):
        return f"{self.paciente} - {self.descripcion[:50]}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Generar hash en blockchain si es un nuevo registro
        if is_new:
            from .blockchain_manager import BlockchainManager
            record_data = {
                'tipo': 'tratamiento',
                'paciente_id': self.paciente.id,
                'profesional_id': self.profesional.id,
                'profesional_nombre': self.profesional.get_full_name(),
                'medicamento': self.medicamento.nombre if self.medicamento else None,
                'descripcion': self.descripcion,
                'dosis': self.dosis,
                'frecuencia': self.frecuencia,
                'fecha_inicio': str(self.fecha_inicio),
                'fecha_fin': str(self.fecha_fin) if self.fecha_fin else None,
                'observaciones': self.observaciones,
                'activo': self.activo,
                'fecha_registro': str(timezone.now())
            }
            BlockchainManager.store_medical_record(
                paciente=self.paciente,
                categoria='tratamiento',
                record_id=self.id,
                record_data=record_data,
                profesional=self.profesional
            )


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
    
    def __str__(self):
        return f"{self.paciente} - {self.get_tipo_display()}: {self.descripcion[:50]}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Generar hash en blockchain si es un nuevo registro
        if is_new:
            from .blockchain_manager import BlockchainManager
            record_data = {
                'tipo': 'antecedente',
                'paciente_id': self.paciente.id,
                'tipo_antecedente': self.tipo,
                'descripcion': self.descripcion,
                'fecha_evento': str(self.fecha_evento) if self.fecha_evento else None,
                'observaciones': self.observaciones,
                'fecha_registro': str(timezone.now())
            }
            BlockchainManager.store_medical_record(
                paciente=self.paciente,
                categoria='antecedente',
                record_id=self.id,
                record_data=record_data
            )


class PruebaLaboratorio(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='pruebas')
    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE)
    nombre_prueba = models.CharField(max_length=200)
    fecha_realizacion = models.DateField()
    resultados = models.TextField()
    valores_referencia = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)
    archivo_resultado = models.FileField(upload_to='pruebas_laboratorio/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.paciente} - {self.nombre_prueba} ({self.fecha_realizacion})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Generar hash en blockchain si es un nuevo registro
        if is_new:
            from .blockchain_manager import BlockchainManager
            record_data = {
                'tipo': 'prueba_laboratorio',
                'paciente_id': self.paciente.id,
                'profesional_id': self.profesional.id,
                'profesional_nombre': self.profesional.get_full_name(),
                'nombre_prueba': self.nombre_prueba,
                'fecha_realizacion': str(self.fecha_realizacion),
                'resultados': self.resultados,
                'valores_referencia': self.valores_referencia,
                'observaciones': self.observaciones,
                'archivo_resultado': self.archivo_resultado.name if self.archivo_resultado else None,
                'fecha_registro': str(timezone.now())
            }
            BlockchainManager.store_medical_record(
                paciente=self.paciente,
                categoria='prueba_laboratorio',
                record_id=self.id,
                record_data=record_data,
                profesional=self.profesional
            )


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
    
    def __str__(self):
        return f"{self.nombre_cirugia} - {self.paciente} ({self.fecha_cirugia})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Generar hash en blockchain si es un nuevo registro
        if is_new:
            from .blockchain_manager import BlockchainManager
            record_data = {
                'tipo': 'cirugia',
                'paciente_id': self.paciente.id,
                'profesional_id': self.profesional.id,
                'profesional_nombre': self.profesional.get_full_name(),
                'nombre_cirugia': self.nombre_cirugia,
                'fecha_cirugia': str(self.fecha_cirugia),
                'descripcion': self.descripcion,
                'complicaciones': self.complicaciones,
                'estado': self.estado,
                'fecha_registro': str(timezone.now())
            }
            BlockchainManager.store_medical_record(
                paciente=self.paciente,
                categoria='cirugia',
                record_id=self.id,
                record_data=record_data,
                profesional=self.profesional
            )


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


# ========== MODELOS PARA BLOCKCHAIN ==========

class BlockchainHash(models.Model):
    """Modelo para almacenar hashes de registros médicos en blockchain"""
    
    CATEGORIAS = [
        ('genesis', 'Hash Génesis'),
        ('alergia', 'Alergia'),
        ('condicion', 'Condición Médica'),
        ('tratamiento', 'Tratamiento'),
        ('antecedente', 'Antecedente'),
        ('prueba_laboratorio', 'Prueba de Laboratorio'),
        ('cirugia', 'Cirugía'),
    ]
    
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='blockchain_hashes')
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    record_id = models.PositiveIntegerField()  # ID del registro médico correspondiente
    hash_value = models.CharField(max_length=64, unique=True)  # SHA256 hash
    transaction_hash = models.CharField(max_length=66, blank=True)  # Hash de transacción Polygon
    block_number = models.PositiveIntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    datos_originales = models.JSONField()  # Datos originales que generaron el hash
    
    class Meta:
        verbose_name = "Blockchain Hash"
        verbose_name_plural = "Blockchain Hashes"
        unique_together = ['paciente', 'categoria', 'record_id']
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.paciente} - {self.get_categoria_display()} ({self.hash_value[:8]}...)"


class AccesoBlockchain(models.Model):
    """Modelo para auditar accesos a información médica en blockchain"""
    
    hash_record = models.ForeignKey(BlockchainHash, on_delete=models.CASCADE, related_name='accesos')
    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE, null=True, blank=True)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, null=True, blank=True)
    fecha_acceso = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    motivo_acceso = models.TextField(blank=True)  # Razón del acceso
    
    class Meta:
        verbose_name = "Acceso Blockchain"
        verbose_name_plural = "Accesos Blockchain"
        ordering = ['-fecha_acceso']
    
    def __str__(self):
        usuario = self.profesional.get_full_name() if self.profesional else self.paciente.get_full_name()
        tipo_usuario = "Profesional" if self.profesional else "Paciente"
        return f"{tipo_usuario} {usuario} accedió a {self.hash_record} el {self.fecha_acceso}"
