from block import Block

# Blockchain class - the sequence of blocks
class Blockchain:
    difficulty = 5  # difficulty of the genesis Block
    def __init__(self, difficulty=5):  # Set default difficulty to 4
        self.chain = [self.create_genesis_block()]
        self.difficulty = difficulty  # Initialize difficulty

    def create_genesis_block(self):
        """Creates the first block with a fixed previous hash."""
        return Block(0, "0", "Genesis Block", self.difficulty)

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, transactions):
        """Adds a new block with PoW to the blockchain."""
        latest_block = self.get_latest_block()
        new_block = Block(len(self.chain), latest_block.hash, transactions, self.difficulty)
        self.chain.append(new_block)
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