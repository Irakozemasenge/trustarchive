import hashlib
import json
import time


class Block:
    def __init__(self, index, data, previous_hash=''):
        self.index = index
        self.timestamp = time.time()
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def proof_of_work(self, difficulty=2):
        target = '0' * difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.compute_hash()
        return self.hash


class BlockchainService:
    """
    Blockchain locale pour TrustArchive.
    Chaque document enregistré crée un bloc immuable.
    """

    def get_last_block(self):
        from .models import BlockchainRecord
        last = BlockchainRecord.objects.order_by('-block_index').first()
        return last

    def register_document(self, unique_number, document_hash):
        from .models import BlockchainRecord
        last = self.get_last_block()
        previous_hash = last.block_hash if last else '0' * 64
        index = (last.block_index + 1) if last else 0

        block = Block(
            index=index,
            data={'unique_number': unique_number, 'document_hash': document_hash},
            previous_hash=previous_hash,
        )
        tx_hash = block.proof_of_work(difficulty=2)

        BlockchainRecord.objects.create(
            block_index=index,
            block_hash=tx_hash,
            previous_hash=previous_hash,
            document_unique_number=unique_number,
            document_hash=document_hash,
            nonce=block.nonce,
            timestamp=block.timestamp,
        )
        return tx_hash

    def verify_chain(self):
        from .models import BlockchainRecord
        records = BlockchainRecord.objects.order_by('block_index')
        prev_hash = '0' * 64
        for record in records:
            block = Block(
                index=record.block_index,
                data={'unique_number': record.document_unique_number, 'document_hash': record.document_hash},
                previous_hash=prev_hash,
            )
            block.nonce = record.nonce
            block.timestamp = record.timestamp
            computed = block.compute_hash()
            if computed != record.block_hash:
                return False, f"Bloc {record.block_index} corrompu"
            prev_hash = record.block_hash
        return True, "Chaîne valide"

    def verify_document(self, unique_number, document_hash):
        from .models import BlockchainRecord
        try:
            record = BlockchainRecord.objects.get(document_unique_number=unique_number)
            return record.document_hash == document_hash
        except BlockchainRecord.DoesNotExist:
            return False
