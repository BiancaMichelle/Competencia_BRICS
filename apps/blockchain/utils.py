from django.db import models
from .models import (
    BlockchainService, BlockchainHash
)

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

