#!/usr/bin/env python
"""
Script de prueba para verificar la funcionalidad de acceso por hash value
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from apps.users.models import Paciente, BlockchainHash, Profesional

def test_hash_access():
    """Prueba el acceso a detalles de hash usando hash_value"""
    print("🔍 Probando acceso por hash value...")

    # Obtener un paciente con hash genesis
    try:
        paciente = Paciente.objects.filter(blockchain_hashes__categoria='genesis').first()
        if not paciente:
            print("❌ No se encontraron pacientes con hash génesis")
            return

        # Obtener el hash genesis
        genesis_hash = BlockchainHash.objects.filter(
            paciente=paciente,
            categoria='genesis'
        ).first()

        if not genesis_hash:
            print("❌ El paciente no tiene hash génesis")
            return

        print(f"✅ Paciente encontrado: {paciente.user.first_name} {paciente.user.last_name}")
        print(f"✅ Hash génesis: {genesis_hash.hash_value}")
        print(f"✅ ID del hash: {genesis_hash.id}")

        # Verificar que se puede acceder por hash_value
        hash_by_value = BlockchainHash.objects.filter(hash_value=genesis_hash.hash_value).first()

        if hash_by_value and hash_by_value == genesis_hash:
            print("✅ Acceso por hash_value funciona correctamente")
            print(f"   URL de acceso: /users/hash/value/{genesis_hash.hash_value}/")
        else:
            print("❌ Error en acceso por hash_value")

    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")

if __name__ == '__main__':
    test_hash_access()
