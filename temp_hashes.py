from apps.blockchain.models import BlockchainHash

hashes = BlockchainHash.objects.filter(object_id=5, previous_hash='0').order_by('timestamp')
if hashes.count() > 1:
    for h in hashes[1:]:
        h.delete()
    print('Duplicados eliminados')
else:
    print('No hay duplicados')
