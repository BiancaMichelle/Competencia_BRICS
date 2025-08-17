# Estructura Modular del Proyecto

Este proyecto Django ha sido reestructurado en módulos independientes para mejorar la organización y mantenibilidad del código.

## Nueva Estructura

```
project-blockchain-ia-foz/
├── apps/                          # Directorio de aplicaciones modulares
│   ├── chat/                      # Módulo de Chat con IA
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── migrations/
│   │
│   ├── blockchain/                # Módulo de Blockchain
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── blockchain_service.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── migrations/
│   │
│   └── __init__.py
│
├── app/                          # Aplicación principal (Django core)
│   ├── core/                     # Módulo core (funcionalidades básicas)
│   │   ├── models.py             # Modelos de Paciente, Profesional, etc.
│   │   ├── views.py              # Vistas principales (sin chat/blockchain)
│   │   ├── forms.py              # Formularios (sin ChatForm)
│   │   └── ...
│   │
│   ├── config/                   # Configuración de Django
│   │   ├── settings.py           # Configuración actualizada
│   │   ├── urls.py               # URLs principales
│   │   └── ...
│   │
│   └── templates/
│       ├── chat/                 # Templates del módulo chat
│       │   └── chat.html
│       │
│       ├── blockchain/           # Templates del módulo blockchain
│       │   └── dashboard.html
│       │
│       └── ...
```

## Módulos Implementados

### 1. Módulo Chat (`apps/chat/`)

**Funcionalidades:**
- Chat con IA especializada en temas médicos
- Historial de mensajes por usuario
- Respuestas en tiempo real (streaming)
- Interfaz moderna y responsive

**Modelos:**
- `ChatMessage`: Almacena conversaciones entre usuarios e IA

**URLs:**
- `/chat/` - Interfaz principal del chat
- `/chat/api/` - API para mensajes normales
- `/chat/api/stream/` - API para respuestas en tiempo real

### 2. Módulo Blockchain (`apps/blockchain/`)

**Funcionalidades:**
- Gestión de blockchain para registros médicos
- Verificación de integridad de datos
- Transacciones médicas seguras
- Dashboard con estadísticas

**Modelos:**
- `Block`: Bloques de la blockchain
- `MedicalRecord`: Registros médicos en blockchain
- `BlockchainTransaction`: Transacciones de la blockchain

**URLs:**
- `/blockchain/` - Dashboard principal
- `/blockchain/add-record/` - Agregar registro médico
- `/blockchain/verify/<hash>/` - Verificar integridad
- `/blockchain/stats/` - Estadísticas

### 3. Módulo Core (`app/core/`)

**Funcionalidades (mantenidas):**
- Gestión de pacientes y profesionales
- Sistema de turnos
- Historial médico tradicional
- Autenticación y autorización

## Configuración Actualizada

### settings.py
```python
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    # ... otras apps de Django
    
    # Apps del proyecto
    'app.core',           # Funcionalidades principales
    'apps.chat',          # Chat con IA
    'apps.blockchain',    # Blockchain médica
]
```

### urls.py principal
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.core.urls')),           # URLs principales
    path('chat/', include('apps.chat.urls')),     # URLs del chat
    path('blockchain/', include('apps.blockchain.urls')),  # URLs blockchain
    path('login/', auth_views.LoginView.as_view()),
    path('logout/', auth_views.LogoutView.as_view()),
]
```

## Migraciones Aplicadas

```bash
# Crear migraciones para los nuevos módulos
python manage.py makemigrations chat
python manage.py makemigrations blockchain

# Aplicar migraciones
python manage.py migrate
```

## Navegación Actualizada

El navbar ahora incluye enlaces a los nuevos módulos:
- **Chat IA** (`/chat/`) - Chat con inteligencia artificial
- **Blockchain** (`/blockchain/`) - Dashboard de blockchain médica

## Ventajas de la Nueva Estructura

### 1. **Separación de Responsabilidades**
- Cada módulo tiene su propia responsabilidad específica
- Código más organizado y fácil de mantener

### 2. **Escalabilidad**
- Fácil agregar nuevos módulos
- Desarrollo independiente de funcionalidades

### 3. **Reutilización**
- Módulos pueden ser reutilizados en otros proyectos
- Código más modular y testeable

### 4. **Mantenimiento**
- Errores aislados por módulo
- Actualizaciones independientes

## Próximos Pasos

1. **Testing**: Implementar tests unitarios para cada módulo
2. **Documentación**: Completar documentación de APIs
3. **Optimización**: Mejorar rendimiento de blockchain
4. **Seguridad**: Implementar autenticación JWT para APIs

## Comandos Útiles

```bash
# Ejecutar servidor de desarrollo
python manage.py runserver

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recopilar archivos estáticos
python manage.py collectstatic
```

## Contacto y Soporte

Para preguntas sobre la nueva estructura o problemas técnicos, consultar la documentación de cada módulo o contactar al equipo de desarrollo.
