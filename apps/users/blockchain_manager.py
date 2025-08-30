from django.utils import timezone
import json
import hashlib
from .models import BlockchainHash, AccesoBlockchain, Paciente
from .blockchain_services import MedicalBlockchainService


class BlockchainManager:
    """Gestor para manejar hashes y blockchain operations"""

    @staticmethod
    def generate_hash(data):
        """Genera un hash SHA256 de los datos proporcionados"""
        if isinstance(data, dict):
            data_str = json.dumps(data, sort_keys=True, default=str)
        else:
            data_str = str(data)

        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()

    @staticmethod
    def store_medical_record(paciente, categoria, record_id, record_data, profesional=None):
        """
        Almacena un registro médico en blockchain y guarda el hash localmente

        Args:
            paciente: Instancia del paciente
            categoria: Tipo de registro ('alergia', 'condicion', etc.)
            record_id: ID del registro médico
            record_data: Datos del registro
            profesional: Profesional que crea el registro (opcional)
        """
        # Generar hash de los datos
        hash_value = BlockchainManager.generate_hash(record_data)

        # Almacenar en blockchain
        service = MedicalBlockchainService()
        blockchain_result = service.store_medical_record(paciente.id, record_data)

        # Crear registro local del hash
        hash_record = BlockchainHash.objects.create(
            paciente=paciente,
            categoria=categoria,
            record_id=record_id,
            hash_value=hash_value,
            transaction_hash=blockchain_result['polygon']['transaction_hash'],
            block_number=blockchain_result['polygon']['block_number'],
            datos_originales=record_data
        )

        return hash_record, blockchain_result

    @staticmethod
    def generate_genesis_hash(paciente):
        """Genera el hash génesis cuando se crea un paciente"""
        genesis_data = {
            'tipo': 'genesis',
            'paciente_id': paciente.id,
            'cedula': paciente.cedula,
            'nombre_completo': paciente.get_full_name(),
            'fecha_nacimiento': str(paciente.fecha_nacimiento),
            'genero': paciente.genero,
            'tipo_sangre': paciente.tipo_sangre,
            'fecha_creacion': str(timezone.now()),
            'email': paciente.email
        }

        hash_record, blockchain_result = BlockchainManager.store_medical_record(
            paciente=paciente,
            categoria='genesis',
            record_id=paciente.id,
            record_data=genesis_data
        )

        return hash_record

    @staticmethod
    def get_patient_hashes_by_category(paciente):
        """Obtiene todos los hashes de un paciente organizados por categoría"""
        hashes = BlockchainHash.objects.filter(paciente=paciente)

        categorias = {}
        for hash_record in hashes:
            categoria = hash_record.categoria
            if categoria not in categorias:
                categorias[categoria] = []
            categorias[categoria].append({
                'id': hash_record.id,
                'hash': hash_record.hash_value,
                'transaction_hash': hash_record.transaction_hash,
                'timestamp': hash_record.timestamp,
                'record_id': hash_record.record_id
            })

        return categorias

    @staticmethod
    def get_hash_details(hash_id, profesional, motivo_acceso="Consulta médica"):
        """Obtiene los detalles de un hash específico y registra el acceso"""
        try:
            hash_record = BlockchainHash.objects.get(id=hash_id)

            # Registrar el acceso
            AccesoBlockchain.objects.create(
                hash_record=hash_record,
                profesional=profesional,
                motivo_acceso=motivo_acceso
            )

            return {
                'hash_record': hash_record,
                'datos_originales': hash_record.datos_originales,
                'categoria': hash_record.get_categoria_display(),
                'fecha_creacion': hash_record.timestamp,
                'transaction_hash': hash_record.transaction_hash,
                'block_number': hash_record.block_number
            }
        except BlockchainHash.DoesNotExist:
            return None

    @staticmethod
    def get_access_history(hash_record):
        """Obtiene el historial de accesos a un hash específico"""
        accesos = AccesoBlockchain.objects.filter(hash_record=hash_record).select_related('profesional', 'paciente')
        history = []
        for acceso in accesos:
            if acceso.profesional:
                history.append({
                    'usuario': acceso.profesional.get_full_name(),
                    'tipo_usuario': 'Profesional',
                    'especialidad': acceso.profesional.get_especialidad_display(),
                    'fecha_acceso': acceso.fecha_acceso,
                    'motivo': acceso.motivo_acceso
                })
            elif acceso.paciente:
                history.append({
                    'usuario': acceso.paciente.get_full_name(),
                    'tipo_usuario': 'Paciente',
                    'especialidad': 'Propietario del registro',
                    'fecha_acceso': acceso.fecha_acceso,
                    'motivo': acceso.motivo_acceso
                })
        return history

    @staticmethod
    def verify_hash_integrity(hash_record):
        """Verifica que el hash almacenado coincida con los datos originales"""
        current_hash = BlockchainManager.generate_hash(hash_record.datos_originales)
        return current_hash == hash_record.hash_value

    @staticmethod
    def registrar_acceso_medico(profesional=None, paciente=None, tipo_registro=None, registro_id=None, motivo="Consulta médica"):
        """
        Registra el acceso de un profesional o paciente a un registro médico específico

        Args:
            profesional: Instancia del profesional que accede (opcional)
            paciente: Instancia del paciente que accede (opcional)
            tipo_registro: Tipo de registro ('alergia', 'condicion', etc.) (opcional)
            registro_id: ID del registro específico (opcional)
            motivo: Motivo del acceso
        """
        try:
            # Si se proporciona tipo_registro y registro_id, buscar el hash específico
            if tipo_registro and registro_id and paciente:
                hash_record = BlockchainHash.objects.get(
                    paciente=paciente,
                    categoria=tipo_registro,
                    record_id=registro_id
                )
            else:
                # Si no se especifica, buscar cualquier hash del paciente (para acceso general)
                hash_record = BlockchainHash.objects.filter(paciente=paciente).first()
                if not hash_record:
                    return False

            # Registrar el acceso
            AccesoBlockchain.objects.create(
                hash_record=hash_record,
                profesional=profesional,
                paciente=paciente,
                motivo_acceso=motivo
            )

            return True
        except BlockchainHash.DoesNotExist:
            # Si no se encuentra el hash, crear un registro de acceso genérico
            return False
        except Exception as e:
            # Log del error pero no fallar la operación
            print(f"Error al registrar acceso médico: {str(e)}")
            return False
