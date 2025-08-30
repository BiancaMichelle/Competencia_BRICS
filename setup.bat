@echo off
REM Script de configuración inicial para Windows
REM Sistema Médico Blockchain

echo 🏥 Configurando Sistema Médico Blockchain...

REM Verificar si estamos en el directorio correcto
if not exist "manage.py" (
    echo ❌ Error: Ejecuta este script desde la raíz del proyecto (donde está manage.py)
    pause
    exit /b 1
)

REM Crear entorno virtual si no existe
if not exist "venv" (
    echo 📦 Creando entorno virtual...
    python -m venv venv
)

REM Activar entorno virtual
echo 🔧 Activando entorno virtual...
call venv\Scripts\activate

REM Instalar dependencias de Python
echo 📚 Instalando dependencias de Python...
pip install -r requirements.txt

REM Instalar dependencias de Node.js
echo 📦 Instalando dependencias de Node.js...
npm install

REM Crear archivo .env si no existe
if not exist ".env" (
    echo 📝 Creando archivo .env...
    copy .env.example .env
    echo ⚠️  IMPORTANTE: Edita el archivo .env con tus configuraciones reales
)

REM Ejecutar migraciones
echo 🗄️  Ejecutando migraciones...
python manage.py makemigrations
python manage.py migrate

REM Preguntar si quiere crear superusuario
echo 👤 ¿Quieres crear un superusuario? (y/n)
set /p create_superuser=
if /i "%create_superuser%"=="y" (
    python manage.py createsuperuser
)

REM Compilar CSS
echo 🎨 Compilando CSS...
npm run build-css

echo.
echo ✅ Configuración completada!
echo.
echo 🚀 Para ejecutar el servidor:
echo    call venv\Scripts\activate
echo    python manage.py runserver
echo.
echo 📖 Documentación adicional en README.md
echo.
pause
