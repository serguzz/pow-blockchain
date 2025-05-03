import json
from ecdsa import SigningKey, SECP256k1
import hashlib

class Wallet:
    """
    Wallet consists of a private and public keys
    The private key is used to sign transactions, while the public key is used to verify  them
    The address is derived from the public key - The address is a hash of the public key
    """
    
    def __init__(self, private_key=None):
        if private_key:
            self.private_key = SigningKey.from_string(bytes.fromhex(private_key), curve=SECP256k1)
        else:
            self.private_key = SigningKey.generate(curve=SECP256k1)
        self.public_key = self.private_key.get_verifying_key()

    @property
    def address(self):
        pub_key_bytes = self.public_key.to_string()
        return hashlib.sha256(pub_key_bytes).hexdigest()

    def save_wallet(self, path):
        data = {
            'private_key': self.private_key.to_string().hex(),
            'public_key': self.public_key.to_string().hex(),
            'address': self.address
        }
        with open(path, 'w') as f:
            json.dump(data, f)

    @staticmethod
    def load_wallet(path):
        with open(path, 'r') as f:
            data = json.load(f)
            return Wallet(private_key=data['private_key'])

    def sign(self, message):
        return self.private_key.sign(message.encode()).hex()
    
    def __str__(self):
        return f"\nWallet Address: {self.address},\
            \nPrivate Key: {self.private_key.to_string().hex()}\
            \nPublic Key: {self.public_key.to_string().hex()}\n"
