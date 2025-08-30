#!/usr/bin/env python
"""
Script para probar el acceso directo por hash value
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from apps.users.models import Paciente, BlockchainHash, Profesional

def test_direct_hash_access():
    """Prueba el acceso directo a la URL de hash por valor"""
    print("🔍 Probando acceso directo por hash value...")

    # Crear cliente de prueba
    client = Client()

    # Obtener el hash genesis
    genesis_hash = BlockchainHash.objects.filter(categoria='genesis').first()
    if not genesis_hash:
        print("❌ No se encontró hash génesis")
        return

    hash_value = genesis_hash.hash_value
    print(f"✅ Hash génesis encontrado: {hash_value}")

    # Crear un usuario profesional para la prueba
    try:
        profesional_user = User.objects.filter(is_staff=True).first()
        if not profesional_user:
            print("❌ No se encontró usuario profesional")
            return

        # Hacer login
        client.login(username=profesional_user.username, password='testpass123')

        # Probar acceso a la URL
        url = f'/users/hash/value/{hash_value}/'
        print(f"🔗 Probando URL: {url}")

        response = client.get(url, follow=True)

        print(f"📊 Código de respuesta: {response.status_code}")

        if response.status_code == 200:
            print("✅ Acceso exitoso a la URL del hash")
            if "Hash Génesis" in response.content.decode():
                print("✅ Contenido correcto - se muestra información del hash")
            else:
                print("⚠️ Contenido recibido pero no contiene información del hash")
        else:
            print(f"❌ Error de acceso: {response.status_code}")
            print(f"   Contenido del error: {response.content.decode()[:200]}...")

    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")

def test_url_patterns():
    """Verifica que las URLs estén correctamente configuradas"""
    print("\n🔍 Verificando configuración de URLs...")

    from django.urls import reverse
    from django.conf import settings

    try:
        # Verificar que la URL se puede resolver
        hash_value = "837271445d879deb35c3113e4fad9e0ca7327ca8be58c6306f5f2bfe63d3dc65"
        url = reverse('users:hash_detail_by_value', kwargs={'hash_value': hash_value})
        print(f"✅ URL resuelta correctamente: {url}")
    except Exception as e:
        print(f"❌ Error resolviendo URL: {str(e)}")

if __name__ == '__main__':
    test_direct_hash_access()
    test_url_patterns()
