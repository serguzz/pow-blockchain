from block import Block
import os
import pandas as pd

# Blockchain class - the sequence of blocks
class Blockchain:
    difficulty = 5  # difficulty of the genesis Block
    filepath = ""
    def __init__(self, filepath="blockchain/blockchain.csv", difficulty=5):  # Set default difficulty to 4
        self.filepath = filepath
        self.difficulty = difficulty  # Initialize difficulty
        self.chain = []
        self.load_chain()

    def load_chain(self):
        """Load blockchain from CSV, or create genesis block if file is missing."""
        if os.path.exists(self.filepath):
            df = pd.read_csv(self.filepath)
            for _, row in df.iterrows():
                block = Block(
                    index=int(row['index']),
                    previous_hash=row['previous_hash'],
                    data=row['data'],
                    difficulty=int(row['difficulty']),
                    timestamp=row['timestamp'],
                    nonce=int(row['nonce'])
                    # hash=row['hash']
                )
                self.chain.append(block)
        else:
            print("🧱 No blockchain found, creating genesis block...")
            self.chain = [self.create_genesis_block()]
            self.save_chain()

    def save_chain(self):
        """Save current blockchain to CSV."""
        data = [{
            "index": block.index,
            "previous_hash": block.previous_hash,
            "timestamp": block.timestamp,
            "data": block.data,
            "difficulty": block.difficulty,
            "nonce": block.nonce,
            "hash": block.hash
        } for block in self.chain]

        df = pd.DataFrame(data)
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        df.to_csv(self.filepath, index=False)


    def create_genesis_block(self):
        """Creates the first block with a fixed previous hash."""
        return Block(0, "0", "Genesis Block", self.difficulty)

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data):
        """Adds a new block with PoW to the blockchain."""
        latest_block = self.get_latest_block()
        new_block = Block(len(self.chain), latest_block.hash, data, self.difficulty)
        self.chain.append(new_block)
        self.save_chain()  # <-- Save on every new block
        print(f"Block {new_block.index} mined with hash: {new_block.hash}")
        return new_block

    def print_blockchain(self):
        # Print the blockchain
        for block in self.chain:
            print(f"Block {block.index}:")
            print(f"  Previous Hash: {block.previous_hash}")
            print(f"  Data: {block.data}")
            print(f"  Timestamp: {block.timestamp}")
            print(f"  Nonce: {block.nonce}")
            print(f"  Hash: {block.hash}\n")