# Sistema Médico Blockchain - ARQA

Sistema de g### ### 3. Configuración rápida (Recomendado)

**En Windows:**
```bash
setup.bat
```

**En Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

Esto automáticamente:
- Crea el entorno virtual
- Instala todas las dependencias
- Configura las variables de entorno
- Ejecuta las migraciones
- Compila el CSS

### 4. Configuración manual

Si prefieres configurar manualmente:

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
npm install
```

### 5. Configurar variables de entornoariables de entorno

Crea un archivo `.env` en la raíz del proyecto copiando el archivo de ejemplo:

```bash
cp .env.example .env
```

Edita el archivo `.env` con tus configuraciones específicas:

```env
# Django Configuration
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Polygon Configuration
POLYGON_RPC_URL=https://polygon-mainnet.infura.io/v3/TU_INFURA_PROJECT_ID

# Filecoin Configuration (opcional)
FILECOIN_API_URL=https://api.filecoin.io
FILECOIN_API_KEY=tu_filecoin_api_key
```

### 6. Instalar dependencias de Node.js (para Tailwind CSS)stión médica con integración blockchain usando Polygon y Filecoin para garantizar la integridad y trazabilidad de los datos médicos.

## 🚀 Características

- **Dashboard médico profesional** con métricas y estadísticas en tiempo real
- **Sistema de pacientes y profesionales** con roles diferenciados
- **Integración con Polygon** para transacciones rápidas y baratas
- **Almacenamiento en Filecoin** para archivos médicos distribuidos
- **Interfaz moderna** con Tailwind CSS y Alpine.js
- **Sistema de verificación** automática de integridad de datos

## 📋 Requisitos Previos

- Python 3.8+
- Node.js (para Tailwind CSS)
- Git
- Cuenta en Infura/Alchemy para Polygon RPC
- API key de Filecoin (opcional)

## 🛠️ Instalación

### 1. Clonar el repositorio

```bash
git clone <tu-repositorio-url>
cd project-blockchain-ia-foz
```

### 2. Crear y activar entorno virtual

**En Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**En Linux/MacOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias de Python

```bash
pip install -r requirements.txt
```

### 4. Instalar dependencias de Node.js (para Tailwind CSS)

```bash
npm install
```

### 5. Configurar la base de datos

```bash
python manage.py makemigrations
python manage.py migrate
```
#### Si les salta algun error posiblemente tengan python 3.12 o 3.13, y una version de Django < 4.2

```bash
pip install --upgrade django
```

### 6. Crear superusuario

```bash
python manage.py createsuperuser
```

### 7. Compilar CSS (Tailwind)

```bash
npm run build-css
```

### 8. Ejecutar el servidor

```bash
python manage.py runserver
```

## 🎯 Uso

### Acceso al Sistema

1. **Dashboard Principal**: `http://127.0.0.1:8000/blockchain/`
2. **Admin Django**: `http://127.0.0.1:8000/admin/`
3. **Registro de Pacientes**: `http://127.0.0.1:8000/blockchain/registro-paciente/`

### Funcionalidades por Rol

#### Superadministrador
- Acceso completo al dashboard
- Registro de nuevos profesionales médicos
- Gestión de todos los usuarios
- Verificación de integridad blockchain

#### Pacientes
- Registro público disponible
- Panel de paciente con historial médico
- Visualización de sus datos blockchain

#### Profesionales Médicos
- Registro solo por superadmin
- Panel profesional con gestión de pacientes
- Creación de registros médicos verificables

## 🔧 Estructura del Proyecto

```
project-blockchain-ia-foz/
├── apps/
│   ├── blockchain/          # App principal con lógica médica
│   ├── chat/               # Sistema de chat (opcional)
│   └── core/               # App base del sistema
├── config/                 # Configuración Django
├── templates/              # Templates HTML
│   ├── blockchain/         # Templates del sistema médico
│   ├── layouts/           # Layouts base
│   └── registration/      # Templates de autenticación
├── static/                # Archivos estáticos
├── requirements.txt       # Dependencias Python
├── package.json          # Dependencias Node.js
└── manage.py            # Comando principal Django
```

## 🛡️ Seguridad

- **Registro de profesionales restringido**: Solo superadministradores pueden crear cuentas de médicos
- **Integración con Polygon**: Transacciones seguras y verificables en blockchain
- **Almacenamiento en Filecoin**: Archivos médicos distribuidos y resistentes a la censura
- **Autenticación requerida**: Sistema de login obligatorio para acceder a funcionalidades

## 🚨 Solución de Problemas Comunes

### Error de migraciones
```bash
python manage.py makemigrations --empty apps.blockchain
python manage.py migrate
```

### Error de CSS
```bash
npm run build-css
python manage.py collectstatic --noinput
```

### Error de permisos
Asegúrate de que el superusuario esté creado:
```bash
python manage.py createsuperuser
```

## 📝 Notas de Desarrollo

- El sistema usa SQLite por defecto (incluido en el .gitignore)
- Los archivos `__pycache__` están excluidos del repositorio
- Tailwind CSS se compila automáticamente con `npm run build-css`
- Ver [ENVIRONMENT.md](ENVIRONMENT.md) para configuración detallada de variables de entorno

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es parte del programa ARQA y está destinado para uso académico y de desarrollo.