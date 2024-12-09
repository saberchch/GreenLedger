import hashlib
import time
import json
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.exceptions import InvalidSignature
from app.transaction import Transaction

class Block:
    def __init__(self, index, transactions, previous_hash, nonce=0, authority_signature=None, timestamp=None, hash=None):
        """
        Initialize a new block in the blockchain.

        Args:
            index (int): The position of the block in the blockchain.
            transactions (list): A list of transactions included in the block.
            previous_hash (str): The hash of the previous block in the blockchain.
            nonce (int): The nonce used for mining the block.
            authority_signature (bytes): The signature of the authority node.
            timestamp (float): The time the block was created.
            hash (str): The hash of the block.
        """
        self.index = index
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.authority_signature = authority_signature
        self.hash = hash if hash is not None else self.calculate_hash()

    def calculate_hash(self):
        """
        Calculate the hash of the block.

        Returns:
            str: The SHA-256 hash of the block's contents.
        """
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.__dict__ for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True).encode()

        return hashlib.sha256(block_string).hexdigest()

    def mine_block(self, difficulty):
        """
        Mine the block by finding a hash that meets the difficulty criteria.

        Args:
            difficulty (int): The number of leading zeros required in the block's hash.
        """
        target = '0' * difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()

    def sign_block(self, private_key):
        """
        Sign the block with the authority's private key.

        Args:
            private_key (rsa.RSAPrivateKey): The private key of the authority node.
        """
        self.authority_signature = private_key.sign(
            self.hash.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

    def verify_signature(self, public_key):
        """
        Verify the block's signature with the authority's public key.

        Args:
            public_key (rsa.RSAPublicKey): The public key of the authority node.

        Returns:
            bool: True if the signature is valid, False otherwise.
        """
        try:
            public_key.verify(
                self.authority_signature,
                self.hash.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False

    def to_dict(self):
        """
        Convert the block to a dictionary format.

        Returns:
            dict: The block's data as a dictionary.
        """
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash
        }

    @classmethod
    def from_dict(cls, block_data):
        """Create a Block object from a dictionary."""
        transactions = [Transaction.from_dict(tx) for tx in block_data['transactions']]
        return cls(
            index=block_data['index'],
            transactions=transactions,
            previous_hash=block_data['previous_hash'],
            nonce=block_data['nonce'],
            timestamp=block_data['timestamp'],
            hash=block_data['hash']
        )
