import hashlib
import time
import json

# Block class with PoW
class Block:
    def __init__(self, index, previous_hash, transactions, difficulty=1, timestamp=None, nonce=0, hash=None):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = round(timestamp or time.time(), 6)
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
        # print(f"Calculating hash for block: {block_dict}")
        block_string = json.dumps(block_dict, sort_keys=True).encode()
        result = hashlib.sha256(block_string).hexdigest()
        # print(f"Hash calculated: {result}")
        return result
        # return hashlib.sha256(block_string).hexdigest()
    
    def mine_block(self, stop_event=None):
        """Proof of Work: Adjust nonce until hash meets difficulty criteria."""
        prefix = '0' * self.difficulty
        while not self.hash.startswith(prefix):
            if stop_event and stop_event.is_set():
                print("⛔ Mining interrupted on Block level!")
                return None
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
        block = Block(
            index=data['index'],
            previous_hash=data['previous_hash'],
            # timestamp=round(data['timestamp'], 6),
            timestamp=data['timestamp'], # Assume timestamp is already rounded
            transactions=data['transactions'],
            difficulty=data['difficulty'],
            nonce=data['nonce'],
            hash=data['hash']
        )
        if block.hash != block.calculate_hash():
            print(f"Invalid block {block.index} from dictionary: hash does not match calculated hash.")
            return None
        return block