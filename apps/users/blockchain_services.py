from web3 import Web3
import os
from django.conf import settings

class PolygonService:
    """Service for interacting with Polygon blockchain"""

    def __init__(self):
        # Polygon RPC URL - you can use Infura, Alchemy, or other providers
        self.rpc_url = os.getenv('POLYGON_RPC_URL', 'https://polygon-rpc.com/')
        self.web3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # Add POA middleware for Polygon (Proof of Authority chain)
        # For web3.py v7+, use the correct middleware
        try:
            from web3.middleware import ExtraDataToPOAMiddleware
            self.web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        except ImportError:
            try:
                from web3.middleware.geth_poa import GethPoaMiddleware
                self.web3.middleware_onion.inject(GethPoaMiddleware, layer=0)
            except ImportError:
                # Last resort: try the old import path
                try:
                    from web3.middleware import geth_poa_middleware
                    self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
                except ImportError:
                    # Fallback: manually handle POA blocks
                    print("Warning: POA middleware not available, some operations may fail")

        # Contract addresses and ABIs would go here
        # For medical records, you might deploy a smart contract for storing hashes
        self.contract_address = None
        self.contract_abi = None
        self.contract = None

    def is_connected(self):
        """Check if connected to Polygon network"""
        return self.web3.is_connected()

    def get_network_info(self):
        """Get current network information"""
        if not self.is_connected():
            return None

        return {
            'chain_id': self.web3.eth.chain_id,
            'block_number': self.web3.eth.block_number,
            'gas_price': self.web3.eth.gas_price
        }

    def store_medical_hash(self, patient_id, record_hash, metadata=None):
        """Store a medical record hash on Polygon"""
        # This would interact with a smart contract
        # For now, just return a mock transaction
        if not self.is_connected():
            raise Exception("Not connected to Polygon network")

        # Get timestamp safely
        try:
            latest_block = self.web3.eth.get_block('latest')
            timestamp = latest_block['timestamp'] if latest_block else None
        except Exception:
            timestamp = None
        
        # If we can't get timestamp, use current time
        if timestamp is None:
            import time
            timestamp = int(time.time())

        # Mock transaction data
        return {
            'transaction_hash': f'0x{record_hash[:64]}',
            'block_number': self.web3.eth.block_number,
            'patient_id': patient_id,
            'record_hash': record_hash,
            'timestamp': timestamp
        }

    def verify_medical_hash(self, transaction_hash):
        """Verify a medical record hash on Polygon"""
        if not self.is_connected():
            return False

        try:
            # Mock verification
            return True
        except Exception:
            return False


class FilecoinService:
    """Service for interacting with Filecoin storage"""

    def __init__(self):
        # Filecoin API endpoint
        self.api_url = os.getenv('FILECOIN_API_URL', 'https://api.filecoin.io')
        # API key for authentication
        self.api_key = os.getenv('FILECOIN_API_KEY')

    def is_configured(self):
        """Check if Filecoin is properly configured"""
        return bool(self.api_key and self.api_key != 'your_filecoin_api_key_here')

    def store_medical_file(self, file_path, patient_id, metadata=None):
        """Store a medical file on Filecoin"""
        if not self.is_configured():
            raise Exception("Filecoin is not configured. Please set FILECOIN_API_KEY in your .env file")

        # This would upload the file to Filecoin
        # For now, return mock data
        import hashlib
        import os

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found")

        # Calculate file hash
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()

        # Mock Filecoin storage
        return {
            'cid': f'bafy{file_hash[:48]}',  # Mock CID
            'file_hash': file_hash,
            'patient_id': patient_id,
            'file_size': os.path.getsize(file_path),
            'timestamp': '2025-08-30T12:00:00Z'
        }

    def retrieve_medical_file(self, cid):
        """Retrieve a medical file from Filecoin"""
        if not self.is_configured():
            raise Exception("Filecoin is not configured. Please set FILECOIN_API_KEY in your .env file")

        # This would download the file from Filecoin
        # For now, return mock data
        return {
            'cid': cid,
            'url': f'https://gateway.filecoin.io/ipfs/{cid}',
            'status': 'available'
        }


class MedicalBlockchainService:
    """Combined service for medical records on blockchain"""

    def __init__(self):
        self.polygon = PolygonService()
        self.filecoin = FilecoinService()

    def store_medical_record(self, patient_id, record_data, file_path=None):
        """Store medical record: hash on Polygon, file on Filecoin (if configured)"""
        import json
        import hashlib

        # Create hash of the record
        record_json = json.dumps(record_data, sort_keys=True)
        record_hash = hashlib.sha256(record_json.encode()).hexdigest()

        # Store hash on Polygon
        polygon_result = self.polygon.store_medical_hash(patient_id, record_hash)

        # If there's a file and Filecoin is configured, store it on Filecoin
        filecoin_result = {'status': 'no_file_provided'}
        if file_path:
            if self.filecoin.is_configured():
                try:
                    filecoin_result = self.filecoin.store_medical_file(file_path, patient_id)
                except Exception as e:
                    # Log the error but don't fail the entire operation
                    print(f"Warning: Filecoin storage failed: {e}")
                    filecoin_result = {'error': str(e), 'status': 'failed'}
            else:
                filecoin_result = {'status': 'not_configured', 'message': 'Filecoin API key not configured'}

        return {
            'polygon': polygon_result,
            'filecoin': filecoin_result,
            'record_hash': record_hash
        }

    def verify_medical_record(self, patient_id, record_data, transaction_hash=None):
        """Verify medical record integrity"""
        import json
        import hashlib

        # Recalculate hash
        record_json = json.dumps(record_data, sort_keys=True)
        current_hash = hashlib.sha256(record_json.encode()).hexdigest()

        # Verify on Polygon if transaction_hash provided
        polygon_verified = True
        if transaction_hash:
            polygon_verified = self.polygon.verify_medical_hash(transaction_hash)

        return {
            'hash_matches': True,  # In real implementation, compare with stored hash
            'polygon_verified': polygon_verified,
            'current_hash': current_hash
        }
