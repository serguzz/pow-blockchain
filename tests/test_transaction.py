from src.wallet import Wallet
from src.transaction import Transaction

def test_transaction():
    # Create two wallets
    sender_wallet = Wallet()
    receiver_wallet = Wallet()

    # Create transaction
    tx = Transaction(
        sender_public_key=sender_wallet.public_key.to_string().hex(),
        receiver_address=receiver_wallet.address,
        amount=50
    )

    # Sign the transaction
    tx.sign_transaction(sender_wallet.private_key)
    print("Signed Transaction:", tx.signature)

    # Validate the transaction
    valid = tx.is_valid()
    print("Is transaction valid?", valid)

    assert valid is True
