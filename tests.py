from blockchain import Blockchain

def test_blockchain():
    # Test the Blockchain with PoW
    # Initialize Blockchain with difficulty level 6
    my_blockchain = Blockchain(difficulty=5)

    # Add new blocks
    my_blockchain.add_block("Alice pays Bob 10 BTC")
    my_blockchain.add_block("Bob pays Charlie 5 BTC")

    my_blockchain.print_blockchain()

# --------------------------- #
test_blockchain()