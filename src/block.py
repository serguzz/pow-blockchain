import hashlib
import time
import json
from .transaction import Transaction

# Block class with PoW
class Block:
    def __init__(self, index, previous_hash, transactions: list[Transaction], miner, difficulty=1, timestamp=None, nonce=0, hash=None):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = round(timestamp or time.time(), 6)
        self.transactions = transactions
        self.miner = miner
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
            "miner": self.miner,
            "difficulty": self.difficulty,
            "nonce": self.nonce
        }
        block_string = json.dumps(block_dict, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    
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
            'transactions': [tx.to_dict() for tx in self.transactions],
            'miner': self.miner,
            'difficulty': self.difficulty,
            'nonce': self.nonce,
            'hash': self.hash
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)
    

    def __str__(self):
        return f"Block: \n" \
                f"  Index: {self.index} type: {type(self.index)}\n" \
                f"  Previous Hash: {self.previous_hash} type: {type(self.previous_hash)}\n" \
                f"  Timestamp: {self.timestamp} type: {type(self.timestamp)}\n" \
                f"  Transactions: {self.transactions} type: {type(self.transactions)}\n" \
                f"  Difficulty: {self.difficulty} type: {type(self.difficulty)}\n" \
                f"  Nonce: {self.nonce} type: {type(self.nonce)}\n" \
                f"  Hash: {self.hash} type: {type(self.hash)}\n" \
                f"  Hash calculated: {self.calculate_hash()} type: {type(self.calculate_hash())}\n" \
    

    def __eq__(self, other):
        if not isinstance(other, Block):
            return False
        transactions = [tx.to_dict() for tx in self.transactions]
        other_transactions = [tx.to_dict() for tx in other.transactions]
        if len(transactions) != len(other_transactions):
            return False
        for i in range(len(transactions)):
            if transactions[i] != other_transactions[i]:
                return False
        return (
            self.index == other.index and
            self.previous_hash == other.previous_hash and
            self.timestamp == other.timestamp and
            # self.transactions == other.transactions and
            self.miner == other.miner and
            self.difficulty == other.difficulty and
            self.nonce == other.nonce and
            self.hash == other.hash
        )


    @staticmethod
    def from_dict(data):
        transactions = [Transaction.from_dict(tx) for tx in data['transactions']]
        block = Block(
            index=data['index'],
            previous_hash=data['previous_hash'],
            timestamp=data['timestamp'], # Assume timestamp is already rounded
            transactions=transactions,
            miner=data['miner'],
            difficulty=data['difficulty'],
            nonce=data['nonce'],
            hash=data['hash']
        )
        if block.hash != block.calculate_hash():
            print(f"Invalid block {block.index} from dictionary: hash {block.hash} does not match calculated hash {block.calculate_hash()}.")
            return None
        return block