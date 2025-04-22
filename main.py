from blockchain import Blockchain

# Test the Blockchain with PoW
# Initialize Blockchain with difficulty level 4
my_blockchain = Blockchain(difficulty=6)

# Add new blocks
my_blockchain.add_block("Alice pays Bob 10 BTC")
my_blockchain.add_block("Bob pays Charlie 5 BTC")

# Print the blockchain
for block in my_blockchain.chain:
    print(f"Block {block.index}:")
    print(f"  Previous Hash: {block.previous_hash}")
    print(f"  Transactions: {block.transactions}")
    print(f"  Timestamp: {block.timestamp}")
    print(f"  Nonce: {block.nonce}")
    print(f"  Hash: {block.hash}\n")