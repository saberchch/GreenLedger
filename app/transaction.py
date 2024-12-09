import time
import hashlib
import json

class Transaction:
    def __init__(self, operation, sender, recipient, amount=None, data=None):
        """
        Initialize a new transaction.

        Args:
            operation (str): The operation type (e.g., 'TRANSFER', 'STAKE', 'CARBON_EMISSION', 'TAX_PAYMENT', 'TAX_CREDIT', 'TAX_AUDIT').
            sender (str): The DID of the sender.
            recipient (str): The DID of the recipient.
            amount (float, optional): The amount of tokens or emissions involved in the transaction.
            data (dict, optional): Additional data related to the transaction.
        """
        self.operation = operation
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.data = data or {}
        self.timestamp = time.time()
        self.state = 'Pending'  # Default state is 'Pending'
        self.hash = self.calculate_hash()  # Calculate and store the hash

    def calculate_hash(self):
        """
        Calculate the hash of the transaction.

        Returns:
            str: The SHA-256 hash of the transaction's contents.
        """
        transaction_string = json.dumps({
            "operation": self.operation,
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "data": self.data,
            "timestamp": self.timestamp
        }, sort_keys=True).encode()

        return hashlib.sha256(transaction_string).hexdigest()

    def to_dict(self):
        """
        Convert the transaction to a dictionary format.

        Returns:
            dict: The transaction's data as a dictionary.
        """
        return {
            "operation": self.operation,
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "data": self.data,
            "timestamp": self.timestamp,
            "state": self.state,
            "hash": self.hash  # Include the hash in the dictionary
        }

    @classmethod
    def from_dict(cls, tx_data):
        """Create a Transaction object from a dictionary."""
        return cls(
            operation=tx_data['operation'],
            sender=tx_data['sender'],
            recipient=tx_data['recipient'],
            amount=tx_data.get('amount'),
            data=tx_data['data']
        )
