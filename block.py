import hashlib
import time

# Block class with PoW
class Block:
    def __init__(self, index, previous_hash, transactions, difficulty=4, timestamp=None):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.timestamp = timestamp or time.time()
        self.nonce = 0  # Starts at 0
        self.difficulty = difficulty  # Number of leading zeros required in hash
        self.hash = self.mine_block()

    def calculate_hash(self):
        """Returns SHA-256 hash of block data."""
        data = f"{self.index}{self.previous_hash}{self.transactions}{self.timestamp}{self.nonce}"
        return hashlib.sha256(data.encode()).hexdigest()

    def mine_block(self):
        """Proof of Work: Adjust nonce until hash meets difficulty criteria."""
        while True:
            hash_attempt = self.calculate_hash()
            if hash_attempt[:self.difficulty] == "0" * self.difficulty:  # Check if hash meets difficulty
                return hash_attempt
            self.nonce += 1  # Increment nonce and try again
