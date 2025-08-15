# Sistema Médico con Blockchain

## Descripción del Proyecto

Este proyecto es un sistema de gestión médica que utiliza Django como framework backend y está preparado para integrar tecnología blockchain para garantizar la integridad y seguridad de los datos médicos de los pacientes.

## Arquitectura y Modelos

### Modelos Principales

1. **Paciente**: Información personal y médica de los pacientes
2. **Profesional**: Datos de los profesionales de la salud
3. **Alergia**: Alergias registradas por paciente
4. **CondicionMedica**: Condiciones médicas actuales o pasadas
5. **Tratamiento**: Tratamientos prescritos por profesionales
6. **Antecedente**: Antecedentes médicos del paciente
7. **PruebaLaboratorio**: Resultados de pruebas médicas
8. **Cirugia**: Cirugías realizadas o programadas
9. **Turno**: Sistema de citas médicas
10. **Medicamento**: Catálogo de medicamentos

### Preparación para Blockchain

Cada modelo que contiene información médica sensible incluye campos específicos para la integración con blockchain:

- `blockchain_hash`: Hash único generado para el registro
- `ultimo_bloque_actualizado`: Hash del último bloque en la cadena
- `fecha_ultimo_hash`: Timestamp de la última actualización

#### Método de Generación de Hash

```python
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
```

## Funcionalidades Implementadas

### Para Pacientes

- **Panel de Control**: Vista general de información médica
- **Historial Médico**: Acceso a antecedentes, pruebas, tratamientos
- **Gestión de Turnos**: Visualización de citas programadas
- **Perfil Completo**: Información personal y médica detallada

### Para Profesionales

- **Panel Profesional**: Vista de turnos y pacientes
- **Búsqueda de Pacientes**: Búsqueda por cédula o nombre
- **Gestión de Información Médica**: Agregar alergias, condiciones, tratamientos
- **Historial de Pacientes**: Acceso completo a información médica

### APIs Implementadas

- `api/mis-turnos/`: Obtiene turnos del paciente logueado
- `api/mi-historial/`: Obtiene historial médico del paciente
- `api/turnos-profesional/`: Obtiene turnos del profesional por fecha

## Integración Futura con Blockchain

### Estructura Preparada

El sistema está diseñado para integrar fácilmente con una blockchain privada o pública. Los puntos de integración incluyen:

1. **Creación de Registros**: Cada vez que se crea un nuevo registro médico, se genera un hash
2. **Verificación de Integridad**: Los hashes pueden verificarse contra la blockchain
3. **Auditoría**: Seguimiento de cambios en los datos médicos
4. **Sincronización**: Campo para último bloque actualizado

### Implementación Sugerida

```python
# Ejemplo de integración con blockchain
class BlockchainService:
    def __init__(self):
        self.blockchain_url = settings.BLOCKCHAIN_URL
        
    def registrar_datos_paciente(self, paciente):
        """Registra los datos del paciente en la blockchain"""
        hash_datos = paciente.generar_hash_blockchain()
        # Enviar a blockchain
        # Actualizar paciente.blockchain_hash
        # Actualizar paciente.ultimo_bloque_actualizado
        
    def verificar_integridad(self, paciente):
        """Verifica la integridad de los datos contra la blockchain"""
        hash_actual = paciente.generar_hash_blockchain()
        # Consultar blockchain
        # Comparar hashes
        return hash_actual == paciente.blockchain_hash
```

## Configuración del Proyecto

### Instalación

1. Clonar el repositorio
2. Crear entorno virtual: `python -m venv venv`
3. Activar entorno: `venv\Scripts\activate` (Windows)
4. Instalar dependencias: `pip install -r requirements.txt`
5. Ejecutar migraciones: `python manage.py migrate`
6. Crear superusuario: `python manage.py createsuperuser`
7. Ejecutar servidor: `python manage.py runserver`

### URLs Principales

- `/` - Página de inicio
- `/panel-paciente/` - Panel del paciente
- `/panel-profesional/` - Panel del profesional
- `/buscar-pacientes/` - Búsqueda de pacientes (profesionales)
- `/registro-paciente/` - Registro de nuevo paciente
- `/registro-profesional/` - Registro de nuevo profesional

## Seguridad y Privacidad

### Medidas Implementadas

1. **Autenticación**: Sistema de login requerido para acceder a datos
2. **Autorización**: Pacientes solo ven sus datos, profesionales pueden ver pacientes asignados
3. **Hashing**: Preparación para verificación de integridad con blockchain
4. **CSRF Protection**: Protección contra ataques CSRF en formularios

### Preparación para GDPR/Normativas

- Modelo preparado para consentimiento de datos
- Hash de blockchain para auditoría de accesos
- Posibilidad de anonimización de datos

## Próximos Pasos para Blockchain

1. **Integrar Web3.py** para comunicación con blockchain Ethereum
2. **Implementar Smart Contracts** para gestión de datos médicos
3. **Crear Sistema de Permisos** basado en blockchain
4. **Implementar Auditoría** de accesos y modificaciones
5. **Sincronización Automática** con la red blockchain

## Estructura de Archivos

```
app/
├── core/
│   ├── models.py          # Modelos de datos con preparación blockchain
│   ├── forms.py           # Formularios para gestión de datos
│   ├── views.py           # Vistas y APIs
│   ├── admin.py           # Configuración del panel de administración
│   └── urls.py            # Configuración de URLs
├── templates/
│   ├── panel_paciente.html     # Panel principal del paciente
│   ├── panel_profesional.html  # Panel principal del profesional
│   ├── perfil_paciente.html    # Perfil completo del paciente
│   ├── buscar_pacientes.html   # Búsqueda de pacientes
│   ├── forms/                  # Templates para formularios
│   └── registration/           # Templates de registro
└── static/
    ├── css/
    └── img/
```

Este sistema está completamente preparado para la integración con blockchain y proporciona una base sólida para un sistema de gestión médica seguro y transparente.
