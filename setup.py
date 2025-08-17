#!/usr/bin/env python
"""
Script de configuración para el Sistema Médico Blockchain
Ejecuta este script después de clonar el repositorio para configurar todo automáticamente.
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Ejecuta un comando y maneja errores"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        print(f"Output: {e.output}")
        return False

def main():
    print("🏥 Sistema Médico Blockchain - Script de Configuración")
    print("=" * 60)
    
    # Verificar Python
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8+ es requerido")
        return False
    
    print(f"✅ Python {python_version.major}.{python_version.minor} detectado")
    
    # Instalar dependencias Python
    if not run_command("pip install -r requirements.txt", "Instalando dependencias de Python"):
        return False
    
    # Verificar si Node.js está instalado
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
        print("✅ Node.js detectado")
        
        # Instalar dependencias Node
        if not run_command("npm install", "Instalando dependencias de Node.js"):
            return False
            
        # Compilar CSS
        if not run_command("npm run build-css", "Compilando Tailwind CSS"):
            return False
    except subprocess.CalledProcessError:
        print("⚠️  Node.js no detectado. CSS no será compilado automáticamente.")
        print("   Instala Node.js y ejecuta 'npm install && npm run build-css' manualmente.")
    
    # Crear migraciones
    if not run_command("python manage.py makemigrations", "Creando migraciones"):
        return False
    
    # Aplicar migraciones
    if not run_command("python manage.py migrate", "Aplicando migraciones"):
        return False
    
    print("\n🎉 ¡Configuración completada exitosamente!")
    print("\n📋 Pasos siguientes:")
    print("1. Crear superusuario: python manage.py createsuperuser")
    print("2. Ejecutar servidor: python manage.py runserver")
    print("3. Abrir en navegador: http://127.0.0.1:8000/blockchain/")
    print("\n💡 Para desarrollo con CSS en tiempo real:")
    print("   npm run watch-css (en terminal separada)")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
