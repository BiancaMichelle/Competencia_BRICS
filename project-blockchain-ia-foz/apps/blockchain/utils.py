# Utilidades para la migración e implementación de blockchain en historiales clínicos
# Archivo: apps/blockchain/utils.py

from django.db import transaction
from django.db import models
from .models import (
    Paciente, CondicionMedica, PruebaLaboratorio, Tratamiento,
    FHIRPatient, FHIRCondition, FHIRObservation, FHIRMedicationStatement,
    BlockchainService, LegacyModelMapper, BlockchainHash
)


class MigrationService:
    """Servicio para migrar datos legacy a modelos FHIR"""
    
    @staticmethod
    def migrate_all_patients():
        """Migra todos los pacientes legacy a FHIR"""
        migrated_count = 0
        errors = []
        
        for paciente in Paciente.objects.all():
            try:
                with transaction.atomic():
                    fhir_patient = LegacyModelMapper.migrate_paciente_to_fhir(paciente)
                    migrated_count += 1
                    print(f"Migrado: {fhir_patient.get_full_name()}")
            except Exception as e:
                errors.append(f"Error migrando paciente {paciente.id}: {str(e)}")
        
        return migrated_count, errors
    
    @staticmethod
    def migrate_all_conditions():
        """Migra todas las condiciones médicas legacy a FHIR"""
        migrated_count = 0
        errors = []
        
        for condicion in CondicionMedica.objects.all():
            try:
                with transaction.atomic():
                    fhir_condition = LegacyModelMapper.migrate_condicion_to_fhir(condicion)
                    migrated_count += 1
                    print(f"Migrada condición: {fhir_condition.display}")
            except Exception as e:
                errors.append(f"Error migrando condición {condicion.id}: {str(e)}")
        
        return migrated_count, errors


class BlockchainAnalytics:
    """Análisis y reportes del blockchain"""
    
    @staticmethod
    def get_blockchain_statistics():
        """Obtiene estadísticas del blockchain"""
        return {
            'total_hashes': BlockchainHash.objects.count(),
            'hashes_by_type': dict(
                BlockchainHash.objects.values_list('content_type')
                .annotate(count=models.Count('id'))
            ),
            'verified_hashes': BlockchainHash.objects.filter(is_verified=True).count(),
            'unverified_hashes': BlockchainHash.objects.filter(is_verified=False).count(),
        }
    
    @staticmethod
    def verify_all_chains():
        """Verifica la integridad de todas las cadenas"""
        results = {}
        content_types = BlockchainHash.objects.values_list('content_type', flat=True).distinct()
        
        for content_type in content_types:
            is_valid, message = BlockchainService.verify_chain_integrity(content_type)
            results[content_type] = {
                'valid': is_valid,
                'message': message
            }
        
        return results


class DataExporter:
    """Exporta datos para análisis o respaldo"""
    
    @staticmethod
    def export_patient_blockchain_data(patient_id):
        """Exporta todos los datos blockchain de un paciente"""
        try:
            patient = FHIRPatient.objects.get(id=patient_id)
            
            # Recopilar todos los hashes relacionados
            patient_hash = BlockchainHash.objects.filter(
                content_type='FHIRPatient',
                object_id=patient.id
            ).first()
            
            condition_hashes = BlockchainHash.objects.filter(
                content_type='FHIRCondition',
                object_id__in=patient.conditions.values_list('id', flat=True)
            )
            
            observation_hashes = BlockchainHash.objects.filter(
                content_type='FHIRObservation',
                object_id__in=patient.observations.values_list('id', flat=True)
            )
            
            medication_hashes = BlockchainHash.objects.filter(
                content_type='FHIRMedicationStatement',
                object_id__in=patient.medication_statements.values_list('id', flat=True)
            )
            
            return {
                'patient': patient.generate_blockchain_data(),
                'patient_hash': patient_hash.hash_value if patient_hash else None,
                'conditions': [
                    {
                        'data': condition.generate_blockchain_data(),
                        'hash': hash_obj.hash_value
                    }
                    for condition, hash_obj in zip(
                        patient.conditions.all(),
                        condition_hashes
                    )
                ],
                'observations': [
                    {
                        'data': observation.generate_blockchain_data(),
                        'hash': hash_obj.hash_value
                    }
                    for observation, hash_obj in zip(
                        patient.observations.all(),
                        observation_hashes
                    )
                ],
                'medications': [
                    {
                        'data': med_statement.generate_blockchain_data(),
                        'hash': hash_obj.hash_value
                    }
                    for med_statement, hash_obj in zip(
                        patient.medication_statements.all(),
                        medication_hashes
                    )
                ]
            }
        except FHIRPatient.DoesNotExist:
            return None


# Comandos de management para Django
"""
Para crear comandos de management, puedes crear estos archivos:

1. apps/blockchain/management/__init__.py
2. apps/blockchain/management/commands/__init__.py
3. apps/blockchain/management/commands/migrate_to_fhir.py
4. apps/blockchain/management/commands/verify_blockchain.py

Ejemplo de comando migrate_to_fhir.py:

from django.core.management.base import BaseCommand
from apps.blockchain.utils import MigrationService

class Command(BaseCommand):
    help = 'Migra datos legacy a modelos FHIR'
    
    def handle(self, *args, **options):
        self.stdout.write('Iniciando migración...')
        
        # Migrar pacientes
        count, errors = MigrationService.migrate_all_patients()
        self.stdout.write(f'Pacientes migrados: {count}')
        
        # Migrar condiciones
        count, errors = MigrationService.migrate_all_conditions()
        self.stdout.write(f'Condiciones migradas: {count}')
        
        if errors:
            self.stdout.write('Errores encontrados:')
            for error in errors:
                self.stdout.write(f'  - {error}')
"""
