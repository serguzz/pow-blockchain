import hashlib
import time

# Block class with PoW
class Block:
    def __init__(self, index, previous_hash, transactions, difficulty=2, timestamp=None, nonce=0, hash=None):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.timestamp = timestamp or time.time()
        self.nonce = nonce
        self.difficulty = difficulty  # Number of leading zeros required in hash
        self.hash = hash or self.calculate_hash()

    def calculate_hash(self):
        """Returns SHA-256 hash of block data."""
        value = f"{self.index}{self.previous_hash}{self.transactions}{self.timestamp}{self.nonce}"
        return hashlib.sha256(value.encode()).hexdigest()

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
            'transactions': self.transactions,
            'difficulty': self.difficulty,
            'timestamp': self.timestamp,
            'nonce': self.nonce,
            'hash': self.hash
        }
    
    @staticmethod
    def from_dict(data):
        return Block(
            index=data['index'],
            previous_hash=data['previous_hash'],
            transactions=data['transactions'],
            difficulty=data.get('difficulty', 2),
            timestamp=data['timestamp'],
            nonce=data['nonce'],
            hash=data['hash']
        )
