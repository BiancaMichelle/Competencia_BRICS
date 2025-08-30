#!/bin/bash

# Script de configuración inicial para el proyecto Sistema Médico Blockchain
# Este script configura el entorno de desarrollo

echo "🏥 Configurando Sistema Médico Blockchain..."

# Verificar si estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo "❌ Error: Ejecuta este script desde la raíz del proyecto (donde está manage.py)"
    exit 1
fi

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python -m venv venv
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/Scripts/activate  # Para Windows
# source venv/bin/activate    # Para Linux/Mac

# Instalar dependencias de Python
echo "📚 Instalando dependencias de Python..."
pip install -r requirements.txt

# Instalar dependencias de Node.js
echo "📦 Instalando dependencias de Node.js..."
npm install

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    echo "📝 Creando archivo .env..."
    cp .env.example .env
    echo "⚠️  IMPORTANTE: Edita el archivo .env con tus configuraciones reales"
fi

# Ejecutar migraciones
echo "🗄️  Ejecutando migraciones..."
python manage.py makemigrations
python manage.py migrate

# Crear superusuario (opcional)
echo "👤 ¿Quieres crear un superusuario? (y/n)"
read -r create_superuser
if [ "$create_superuser" = "y" ] || [ "$create_superuser" = "Y" ]; then
    python manage.py createsuperuser
fi

# Compilar CSS
echo "🎨 Compilando CSS..."
npm run build-css

echo ""
echo "✅ Configuración completada!"
echo ""
echo "🚀 Para ejecutar el servidor:"
echo "   source venv/Scripts/activate  # Windows"
echo "   # source venv/bin/activate   # Linux/Mac"
echo "   python manage.py runserver"
echo ""
echo "📖 Documentación adicional en README.md"
