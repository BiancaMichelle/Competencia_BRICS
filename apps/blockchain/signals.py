# apps/blockchain/signals.py
from django.db.models.signals import post_save, post_delete
from django.db import transaction
from django.dispatch import receiver
from .models import BlockchainService
from .models import (
    Alergia, CondicionMedica, Tratamiento,
    Antecedente, PruebaLaboratorio, Cirugia
)
from apps.users.models import Paciente

def schedule_patient_version(paciente, created_by=None):
    # Ejecutar después del commit para evitar snapshots inconsistentes
    def _create():
        BlockchainService.create_patient_version(paciente, created_by=created_by)
    transaction.on_commit(_create)

@receiver(post_save, sender=Paciente)
def on_paciente_saved(sender, instance, created, **kwargs):
    if created:
        # Crear el primer hash cuando se registra el paciente
        schedule_patient_version(instance, created_by=None)

@receiver(post_delete, sender=Alergia)
@receiver(post_delete, sender=CondicionMedica)
@receiver(post_delete, sender=Tratamiento)
@receiver(post_delete, sender=Antecedente)
@receiver(post_delete, sender=PruebaLaboratorio)
@receiver(post_delete, sender=Cirugia)
def on_medical_record_deleted(sender, instance, **kwargs):
    paciente = getattr(instance, 'paciente', None)
    if not paciente:
        return
    schedule_patient_version(paciente, created_by=None)