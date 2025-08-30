#!/usr/bin/env python
"""
Script para verificar el estado de los datos en la base de datos
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from apps.users.models import Paciente, BlockchainHash, Profesional

def check_database_status():
    """Verifica el estado de los datos en la base de datos"""
    print("🔍 Verificando estado de la base de datos...")

    # Contar pacientes
    pacientes_count = Paciente.objects.count()
    print(f"📊 Total de pacientes: {pacientes_count}")

    # Contar profesionales
    profesionales_count = Profesional.objects.count()
    print(f"👨‍⚕️ Total de profesionales: {profesionales_count}")

    # Contar hashes de blockchain
    hashes_count = BlockchainHash.objects.count()
    print(f"🔗 Total de hashes en blockchain: {hashes_count}")

    # Verificar hashes por categoría
    categorias = ['genesis', 'alergia', 'condicion', 'tratamiento', 'prueba_laboratorio', 'antecedente', 'cirugia']
    for categoria in categorias:
        count = BlockchainHash.objects.filter(categoria=categoria).count()
        print(f"   {categoria}: {count} hashes")

    # Verificar pacientes con hashes genesis
    pacientes_con_genesis = Paciente.objects.filter(blockchain_hashes__categoria='genesis').distinct().count()
    print(f"🎯 Pacientes con hash génesis: {pacientes_con_genesis}")

    # Mostrar algunos ejemplos de hashes
    if hashes_count > 0:
        print("\n📋 Ejemplos de hashes encontrados:")
        hashes_ejemplo = BlockchainHash.objects.all()[:3]
        for hash_obj in hashes_ejemplo:
            print(f"   ID: {hash_obj.id}")
            print(f"   Hash: {hash_obj.hash_value[:32]}...")
            print(f"   Categoría: {hash_obj.categoria}")
            print(f"   Paciente: {hash_obj.paciente.user.first_name} {hash_obj.paciente.user.last_name}")
            print()

    # Verificar estructura de la tabla
    print("🏗️ Verificando estructura de la tabla BlockchainHash...")
    try:
        # Intentar hacer una consulta compleja
        genesis_hashes = BlockchainHash.objects.filter(categoria='genesis').select_related('paciente')
        if genesis_hashes.exists():
            primer_hash = genesis_hashes.first()
            print(f"✅ Estructura correcta - Hash génesis encontrado: {primer_hash.hash_value[:32]}...")
            print(f"   Paciente asociado: {primer_hash.paciente.user.first_name} {primer_hash.paciente.user.last_name}")
        else:
            print("⚠️ No se encontraron hashes génesis")
    except Exception as e:
        print(f"❌ Error en la estructura de la tabla: {str(e)}")

if __name__ == '__main__':
    check_database_status()
