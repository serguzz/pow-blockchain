import pytest
from src.wallet import Wallet

# Create a new wallet
def test_create_wallet():
    wallet = Wallet()
    print("New Wallet Address:", wallet.address)
    assert wallet.address is not None


def test_load_wallet():
    # Save to file
    wallet = Wallet()
    wallet.save_wallet('wallets/test_wallet.json')

    # Load from file
    loaded_wallet = Wallet.load_wallet('wallets/test_wallet.json')
    print("Loaded Wallet Address:", loaded_wallet.address)
    assert loaded_wallet.address == wallet.address


def test_wallet_signature():
    # Check signing
    loaded_wallet = Wallet.load_wallet('wallets/test_wallet.json')
    message = "Hello blockchain"
    signature = loaded_wallet.sign(message)
    print("Signature:", signature)
    assert signature is not None
