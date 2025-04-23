from block import Block
import os
import pandas as pd

# Blockchain class - the sequence of blocks
class Blockchain:
    difficulty = 5  # difficulty of the genesis Block
    def __init__(self, client_id="default", difficulty=5):  # Set default difficulty to 4
        self.client_id = client_id
        self.difficulty = difficulty  # Initialize difficulty
        self.chain = []
        self.load_chain()

    def get_csv_path(self):
        return f"blockchain/blockchain_{self.client_id}.csv"

    def load_chain(self):
        """Load blockchain from CSV, or create genesis block if file is missing."""
        path = self.get_csv_path()
        if os.path.exists(path):
            df = pd.read_csv(path)
            for _, row in df.iterrows():
                block = Block(
                    index=int(row['index']),
                    previous_hash=row['previous_hash'],
                    transactions=row['transactions'],
                    difficulty=int(row['difficulty']),
                    timestamp=row['timestamp'],
                    nonce=int(row['nonce'])
                    # hash=row['hash']
                )
                block.hash = row['hash']
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
            "transactions": block.transactions,
            "difficulty": block.difficulty,
            "nonce": block.nonce,
            "hash": block.hash
        } for block in self.chain]

        df = pd.DataFrame(data)
        # os.makedirs(os.path.dirname(self.get_csv_path()), exist_ok=True)
        df.to_csv(self.get_csv_path(), index=False)


    def create_genesis_block(self):
        """Creates the first block with a fixed previous hash."""
        block = Block(0, "0", "Genesis Block", self.difficulty)
        block.mine_block()  # Mine the genesis block
        return block

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, transactions):
        """Adds a new block with PoW to the blockchain."""
        latest_block = self.get_latest_block()
        new_block = Block(len(self.chain), latest_block.hash, transactions, self.difficulty)
        new_block.mine_block()
        self.chain.append(new_block)
        self.save_chain()  # <-- Save on every new block
        print(f"Block {new_block.index} mined with hash: {new_block.hash}")
        return new_block

    def print_blockchain(self):
        # Print the blockchain
        for block in self.chain:
            print(f"Block {block.index}:")
            print(f"  Previous Hash: {block.previous_hash}")
            print(f"  Transactions: {block.transactions}")
            print(f"  Timestamp: {block.timestamp}")
            print(f"  Nonce: {block.nonce}")
            print(f"  Hash: {block.hash}\n")