import hashlib
from ecdsa import VerifyingKey, SECP256k1

class Transaction:
    def __init__(self, sender_public_key, receiver_address, amount, signature=None, tx_id=None):
        self.sender_public_key = sender_public_key
        self.receiver_address = receiver_address
        self.amount = amount
        self.signature = signature
        self.tx_id = tx_id or self.calculate_hash()

    def calculate_hash(self):
        message = f"{self.sender_public_key}{self.receiver_address}{self.amount}"
        return hashlib.sha256(message.encode()).hexdigest()

    def sign_transaction(self, private_key):
        message = f"{self.sender_public_key}{self.receiver_address}{self.amount}"
        self.signature = private_key.sign(message.encode()).hex()

    def is_valid(self):
        if not self.signature:
            return False
        public_key = VerifyingKey.from_string(bytes.fromhex(self.sender_public_key), curve=SECP256k1)
        message = f"{self.sender_public_key}{self.receiver_address}{self.amount}"
        try:
            return public_key.verify(bytes.fromhex(self.signature), message.encode())
        except:
            return False
        
    def __str__(self):
        return f"Transaction:\
            \nsender_public_key: {self.sender_public_key},\
            \nreceiver_address: {self.receiver_address}, \
            \namount: {self.amount}, \
            \nsignature: {self.signature}, \
            \ntx_id: {self.tx_id}\n"
