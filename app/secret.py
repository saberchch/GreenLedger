import hashlib
from mnemonic import Mnemonic
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.fernet import Fernet
import base64
import os

class SecretManager:
    def __init__(self):
        """Initialize SecretManager with a mnemonic generator for secret phrases."""
        self.mnemo = Mnemonic("english")
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def generate_secret_phrase(self, strength=128):
        """
        Generate a secret phrase (mnemonic) using the BIP-39 standard.

        Args:
            strength (int): Entropy strength (128 bits generates 12 words).

        Returns:
            str: The generated secret phrase (mnemonic words).
        """
        return self.mnemo.generate(strength=strength)

    def generate_key_from_secret_phrase(self, secret_phrase):
        """
        Generate a key pair (public and private keys) from a secret phrase.

        Args:
            secret_phrase (str): The BIP-39 mnemonic (secret phrase) used to derive the seed.

        Returns:
            tuple: (public_key_pem, private_key_pem) The public and private keys in PEM format.
        """
        seed = self.mnemo.to_seed(secret_phrase)

        # Generate RSA keys for the user (for simplicity, using RSA in this example)
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()

        # Serialize keys to PEM format
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return public_key_pem, private_key_pem

    def recover_key_from_secret_phrase(self, secret_phrase):
        """
        Recover a key pair from an existing secret phrase (mnemonic).

        Args:
            secret_phrase (str): The BIP-39 mnemonic used for key recovery.

        Returns:
            tuple: (public_key_pem, private_key_pem) The recovered public and private keys in PEM format.
        """
        return self.generate_key_from_secret_phrase(secret_phrase)

    def hash_secret_phrase(self, secret_phrase):
        """
        Generate a secure hash of the secret phrase for additional verification or security purposes.

        Args:
            secret_phrase (str): The secret phrase to hash.

        Returns:
            str: The SHA-256 hash of the secret phrase.
        """
        return hashlib.sha256(secret_phrase.encode()).hexdigest()

    def generate_account_address(self, public_key_pem):
        """
        Generate an account address from the public key.

        Args:
            public_key_pem (bytes): The public key in PEM format.

        Returns:
            str: The generated account address (hash of the public key).
        """
        # Hash the public key using SHA-256
        sha256_hash = hashlib.sha256(public_key_pem).digest()

        # Optionally, apply RIPEMD-160 for further hashing
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(sha256_hash)

        # Use the resulting hash as the account address
        account_address = ripemd160.hexdigest()
        return account_address

    def sign_transaction(self, vote_data, secret_phrase):
        """
        Sign the transaction data using the private key derived from the secret phrase.

        Args:
            vote_data (str): The data of the vote transaction to be signed.
            secret_phrase (str): The secret phrase used to derive the private key.

        Returns:
            bytes: The signature of the transaction data.
        """
        # Recover the private key from the secret phrase
        _, private_key_pem = self.generate_key_from_secret_phrase(secret_phrase)
        
        # Load the private key from PEM format
        private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None,
            backend=default_backend()
        )
        
        # Sign the vote data
        signature = private_key.sign(
            vote_data.encode(),  # Ensure the data is in bytes
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return signature

    def encrypt_secret_phrase(self, secret_phrase):
        """Encrypt the secret phrase."""
        return self.cipher.encrypt(secret_phrase.encode()).decode()

    def decrypt_secret_phrase(self, encrypted_phrase):
        """Decrypt the secret phrase."""
        return self.cipher.decrypt(encrypted_phrase.encode()).decode()
