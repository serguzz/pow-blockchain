import hashlib
import time
import json

# Block class with PoW
class Block:
    def __init__(self, index, previous_hash, transactions, difficulty=5, timestamp=None, nonce=0, hash=None):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp or time.time()
        self.transactions = transactions
        self.difficulty = difficulty  # Number of leading zeros required in hash
        self.nonce = nonce
        self.hash = hash or self.calculate_hash()

    def calculate_hash(self):
        """Returns SHA-256 hash of block data."""
        block_dict = {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "difficulty": self.difficulty,  # <-- this is important
            "nonce": self.nonce
        }
        block_string = json.dumps(block_dict, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def mine_block(self):
        """Proof of Work: Adjust nonce until hash meets difficulty criteria."""
        prefix = '0' * self.difficulty
        while not self.hash.startswith(prefix):
            self.nonce += 1
            self.hash = self.calculate_hash()
        return self.hash
    
    def to_dict(self):
        return {
            'index': self.index,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'difficulty': self.difficulty,
            'nonce': self.nonce,
            'hash': self.hash
        }
    
    @staticmethod
    def from_dict(data):
        return Block(
            index=data['index'],
            previous_hash=data['previous_hash'],
            timestamp=data['timestamp'],
            transactions=data['transactions'],
            difficulty=data['difficulty'],
            nonce=data['nonce'],
            hash=data['hash']
        )
