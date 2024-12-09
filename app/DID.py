import hashlib
import json
from datetime import datetime

class DID:
    def __init__(self, identifier, public_key):
        """
        Initialize the DID with the identifier and public key.

        Args:
            identifier (str): The identifier for the user (e.g., account address or username).
            public_key (str): The public key of the user.
        """
        # Use identifier as the DID
        self.identifier = f"did:example:{identifier}"
        self.public_key = public_key
        self.metadata = {}  # Dictionary to hold verifiable claims and other metadata

    def add_metadata(self, key, value):
        """Add metadata or verifiable claims to the DID."""
        self.metadata[key] = value

    def get_metadata(self):
        """Return the metadata associated with the DID."""
        return self.metadata

    def generate_did_document(self):
        """
        Generate a DID document that can be shared or stored on the blockchain.

        Returns:
            str: The DID document as a JSON string.
        """
        did_document = {
            "@context": "https://www.w3.org/ns/did/v1",
            "id": self.identifier,
            "publicKey": [{
                "id": f"{self.identifier}#key-1",
                "type": "Ed25519VerificationKey2018",
                "controller": self.identifier,
                "publicKeyBase58": self.public_key
            }],
            "service": []  # Services could be added here, like messaging or voting services
        }
        return json.dumps(did_document)

    def calculate_did_hash(self):
        """
        Calculate a hash for the DID, which can be stored or used for additional verification.

        Returns:
            str: The SHA-256 hash of the DID document.
        """
        # Convert datetime objects in metadata to strings
        metadata_serializable = {
            key: (value.isoformat() if isinstance(value, datetime) else value)
            for key, value in self.metadata.items()
        }
        did_string = json.dumps({
            "id": self.identifier,
            "public_key": self.public_key,
            "metadata": metadata_serializable
        }, sort_keys=True).encode()
        return hashlib.sha256(did_string).hexdigest()

    def generate_did(self, identifier):
        """
        Generate a DID for a user.

        Args:
            identifier (str): The unique identifier for the user (e.g., username).

        Returns:
            str: The generated DID.
        """
        return f"did:example:{identifier}"
