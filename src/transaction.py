import hashlib
from ecdsa import VerifyingKey, SECP256k1
import json

class Transaction:
    def __init__(self, from_address, from_public_key, to_address, amount, signature=None, tx_id=None):
        
        self.from_address = from_address
        self.from_public_key = from_public_key
        self.to_address = to_address
        self.amount = amount
        self.signature = signature
        self.tx_id = tx_id or self.calculate_hash()

    def calculate_hash(self):
        message = f"{self.from_public_key}{self.to_address}{self.amount}"
        return hashlib.sha256(message.encode()).hexdigest()

    def sign_transaction(self, private_key):
        message = f"{self.from_public_key}{self.to_address}{self.amount}"
        self.signature = private_key.sign(message.encode()).hex()

    def is_valid(self):
        if not self.signature:
            return False
        message = f"{self.from_public_key}{self.to_address}{self.amount}"
        try:
            return self.from_public_key.verify(bytes.fromhex(self.signature), message.encode())
        except:
            return False


    def __eq__(self, other):
        if not isinstance(other, Transaction):
            return False
        return (self.from_address == other.from_address and
                self.from_public_key == other.from_public_key and
                self.to_address == other.to_address and
                self.amount == other.amount and
                self.signature == other.signature and
                self.tx_id == other.tx_id)
    
        
    def __str__(self):
        return f"from_address: {self.from_address},\n \
            from_public_key: {self.from_public_key.to_string().hex()},\n \
            to_address: {self.to_address},\n \
            amount: {self.amount},\n \
            signature: {self.signature},\n \
            tx_id: {self.tx_id}"
    

    def to_dict(self):
        """Return dictionary representation for saving, JSON, etc."""
        return {
            'from_address': self.from_address,
            'from_public_key': self.from_public_key.to_string().hex(),
            'to_address': self.to_address,
            'amount': self.amount,
            'signature': self.signature,
            'tx_id': self.tx_id
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a Transaction instance from a dictionary."""
        return cls(
            from_address=data['from_address'],
            from_public_key=VerifyingKey.from_string(bytes.fromhex(data['from_public_key']), curve=SECP256k1),
            to_address=data['to_address'],
            amount=data['amount'],
            signature=data['signature'],
            tx_id=data['tx_id']
        )
    
    
    def to_json(self):
        """Return JSON representation of the transaction."""
        return json.dumps(self.to_dict(), indent=4)
    
    
    def to_file(self, path):
        """Save transaction to a file."""
        with open(path, 'w') as f:
            # f.write(str(self.to_dict()))
            f.write(json.dumps(self.to_dict(), indent=4)) # Uncomment this line to use JSON saving instead of str()

    @classmethod
    def from_file(cls, path):
        """Load transaction from a file."""
        with open(path, 'r') as f:
            data = json.load(f)
            return cls.from_dict(data)
        # return cls.from_dict(json.load(f))  # Uncomment this line to use JSON loading instead of eval

    @classmethod
    def from_file_object(cls, file_obj):
        """Load transaction from a file object."""
        data = json.load(file_obj)
        return cls.from_dict(data)