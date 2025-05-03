from src.wallet import Wallet

# Create a new wallet
wallet = Wallet()
print("New Wallet Address:", wallet.address)

# Save to file
wallet.save_wallet('wallets/test_wallet.json')

# Load from file
loaded_wallet = Wallet.load_wallet('wallets/test_wallet.json')
print("Loaded Wallet Address:", loaded_wallet.address)

# Check signing
message = "Hello blockchain"
signature = loaded_wallet.sign(message)
print("Signature:", signature)
