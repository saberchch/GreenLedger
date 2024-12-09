import json
import os
from datetime import datetime
from app.block import Block
from app.transaction import Transaction
from app.DID import DID
from cryptography.hazmat.primitives.asymmetric import rsa
import threading
import time
from app.balance import BalanceManager
from flask import flash 

class Blockchain:
    def __init__(self, filename='blockchain.json'):
        self.chain = []
        self.current_transactions = []  # List to hold current transactions
        self.authority_nodes = {}  # Map of node identifiers to public keys
        self.filename = filename
        self.balance_manager = BalanceManager()  # Initialize balance manager
        self.load_blockchain()

    
    def create_genesis_block(self):
        """Create the genesis block and add it to the blockchain."""
        genesis_block = Block(0, [], "0", nonce=0)
        self.chain.append(genesis_block)
        self.store_blockchain()
        print("Genesis block created.")

    def store_blockchain(self):
        """Save the blockchain to a file."""
        with open(self.filename, 'w') as f:
            json.dump([block.to_dict() for block in self.chain], f, indent=4)

    def load_blockchain(self):
        """Load the blockchain from a file, or create a genesis block if the file is empty or missing."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    chain_data = json.load(f)
                    if chain_data:
                        self.chain = [Block.from_dict(block_data) for block_data in chain_data]
                        print(f"Blockchain loaded from {self.filename}.")
                    else:
                        print("Blockchain file is empty. Initializing with a genesis block.")
                        self.create_genesis_block()
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading blockchain: {e}. Initializing with a genesis block.")
                self.create_genesis_block()
        else:
            print("Blockchain file not found. Initializing with a genesis block.")
            self.create_genesis_block()

    @property
    def last_block(self):
        return self.chain[-1] if self.chain else None

        
    def add_transaction(self, sender, recipient, operation, data):
        """
        Add a new transaction to the list of current transactions.

        Args:
            sender (str): The sender's username or DID.
            recipient (str): The recipient's username or DID.
            operation (str): The operation type (e.g., 'CARBON_EMISSION_CIVIL').
            data (dict): Additional data related to the transaction.

        Returns:
            Transaction: The created transaction.
        """
        transaction = Transaction(
            operation=operation,
            sender=sender,
            recipient=recipient,
            data=data
        )
        self.current_transactions.append(transaction)
        return transaction

    def add_block(self, transaction):
        """
        Add a new block to the blockchain with a single transaction.

        Args:
            transaction (Transaction): The transaction to include in the block.
        """
        # Calculate the hash of the last block
        previous_hash = self.last_block.hash if self.last_block else "0"
        
        # Create a new block with the transaction
        new_block = Block(len(self.chain), [transaction], previous_hash, datetime.now().isoformat())
        
        # Add the block to the chain
        self.chain.append(new_block)
        
        # Update the state of the transaction to 'Processed'
        transaction.state = 'Processed'
        
        # Save the blockchain state
        self.store_blockchain()

        print(f"Adding block with transaction: {transaction}")  # Debugging output
        print(f"Current blockchain state: {self.chain}")  # Debugging output
        
        return new_block

    def add_civil_engineering_transaction(self, sender, recipient, materials_used, machinery_emissions, energy_consumption):
        """
        Add a civil engineering transaction with specific metadata.

        Args:
            sender (str): The sender's DID.
            recipient (str): The recipient's DID.
            materials_used (dict): Materials used in the project.
            machinery_emissions (dict): Emissions from machinery.
            energy_consumption (dict): Energy consumption data.

        Returns:
            Transaction: The created transaction.
        """
        data = {
            'materials_used': materials_used,
            'machinery_emissions': machinery_emissions,
            'energy_consumption': energy_consumption
        }
        return self.add_transaction(sender, recipient, 'CARBON_EMISSION', data)

    def add_mechanical_engineering_transaction(self, sender, recipient, energy_usage, operation_hours, fuel_consumption):
        """
        Add a mechanical engineering transaction with specific metadata.

        Args:
            sender (str): The sender's DID.
            recipient (str): The recipient's DID.
            energy_usage (dict): Energy usage data.
            operation_hours (dict): Hours of operation for processes.
            fuel_consumption (dict): Fuel consumption data.

        Returns:
            Transaction: The created transaction.
        """
        data = {
            'energy_usage': energy_usage,
            'operation_hours': operation_hours,
            'fuel_consumption': fuel_consumption
        }
        return self.add_transaction(sender, recipient, 'CARBON_EMISSION', data)

    def add_electronics_engineering_transaction(self, sender, recipient, power_usage, recycling_efforts):
        """
        Add an electronics engineering transaction with specific metadata.

        Args:
            sender (str): The sender's DID.
            recipient (str): The recipient's DID.
            power_usage (dict): Power usage data.
            recycling_efforts (dict): Recycling efforts data.

        Returns:
            Transaction: The created transaction.
        """
        data = {
            'power_usage': power_usage,
            'recycling_efforts': recycling_efforts
        }
        return self.add_transaction(sender, recipient, 'CARBON_EMISSION', data)

    def calculate_user_balance(self, user_did):
        """
        Calculate the balance of a user based on their transactions.

        Args:
            user_did (str): The DID of the user.

        Returns:
            float: The calculated balance of the user.
        """
        balance = 0.0
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.recipient == user_did:
                    balance += transaction.data.get('amount', 0)
                elif transaction.sender == user_did:
                    balance -= transaction.data.get('amount', 0)
        return balance

    def burn_tokens(self, user_id, amount):
        """
        Burn a specified amount of tokens from a user's balance.

        Args:
            user_id (str): The ID of the user.
            amount (float): The amount of tokens to burn.

        Returns:
            bool: True if the burn was successful, False otherwise.
        """
        user_balance = self.balance_manager.get_balance(user_id)
        if user_balance >= amount:
            self.balance_manager.update_balance(user_id, -amount)
            
            # Record the burn transaction
            self.add_transaction(
                sender=user_id,
                recipient="BURN",
                operation="BURN",
                data={"amount": amount}
            )
            self.add_block()
            
            print(f"Burned {amount} tokens from user {user_id}.")
            return True
        else:
            print(f"Failed to burn tokens: insufficient balance for user {user_id}.")
            return False

    def get_user_data(self, username):
        """
        Retrieve user-specific data from the blockchain.

        Args:
            username (str): The username or DID of the user.

        Returns:
            dict: A dictionary containing user-specific data, or None if the user is not found.
        """
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.sender == username:
                    # Deserialize the JSON string to a dictionary if needed
                    if isinstance(transaction.data, str):
                        transaction_data = json.loads(transaction.data)
                    else:
                        transaction_data = transaction.data
                    
                    return {
                        'encrypted_secret_phrase': transaction_data.get('encrypted_secret_phrase'),
                        'public_key': transaction_data.get('public_key'),
                        'profession': transaction_data.get('profession')  # Include profession
                    }
        return None  # User not found

    def is_username_available(self, username):
        """
        Check if a username is available for registration.

        Args:
            username (str): The username to check.

        Returns:
            bool: True if the username is available, False otherwise.
        """
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.sender == username and transaction.operation in ['USER_REGISTRATION', 'STORE_DID']:
                    return False
        return True

    def add_user_to_blockchain(self, username, encrypted_secret, public_key):
        """
        Add a new user to the blockchain and generate a DID.

        Args:
            username (str): The username of the new user.
            encrypted_secret (str): The encrypted secret phrase of the new user.
            public_key (str): The public key of the new user.
        """
        # Check if the username is available
        if not self.is_username_available(username):
            return False, f"Username '{username}' is already taken."

        transaction_data = {
            "encrypted_secret_phrase": encrypted_secret,
            "public_key": public_key
        }

        # Create the user registration transaction
        transaction = self.add_transaction(
            sender=username,
            recipient='SYSTEM',
            operation='USER_REGISTRATION',
            data=transaction_data
        )

        # Immediately mark the transaction as processed
        transaction.state = "Processed"

        # Initialize the user's balance
        self.balance_manager.initialize_user(username)

        # Add the block with the user registration transaction
        self.add_block()  # This will include the transaction in the same block

        return True, "Registration successful!"

    def select_mining_node(self):
        """Select the next authority node to mine a block."""
        # Simple round-robin selection or other criteria
        # For example, using a round-robin approach:
        node_ids = list(self.authority_nodes.keys())
        if not node_ids:
            raise ValueError("No authority nodes available.")
        # Select the next node based on the current chain length
        return node_ids[len(self.chain) % len(node_ids)]

    def start_mining(self, interval=600):
        """Start the mining process with a fixed interval."""
        def mine():
            while True:
                time.sleep(interval)
                try:
                    self.mine_block()
                except Exception as e:
                    print(f"Error during mining: {e}")

        mining_thread = threading.Thread(target=mine)
        mining_thread.daemon = True
        mining_thread.start()

    def mine_block(self):
        """Mine a new block using the selected authority node."""
        node_id = self.select_mining_node()
        private_key = self.authority_nodes[node_id]  # Assuming you have a way to access the private key
        self.add_block()
        print(f"Block mined by authority node: {node_id}")

    def create_user_did(self, user_identifier, user_public_key):
        """
        Generate a DID for a new user.
        
        Args:
            user_identifier (str): Unique identifier for the user (e.g., username).
            user_public_key (str): Public key of the user.
        
        Returns:
            tuple: The DID document and its hash.
        """
        # Create a DID instance for the user
        user_did = DID(identifier=user_identifier, public_key=user_public_key)
        
        # Add any metadata needed (optional)
        user_did.add_metadata("role", "voter")
        user_did.add_metadata("registration_date", datetime.now())
        
        # Generate the DID document
        did_document = user_did.generate_did_document()
        
        # Optionally calculate a hash of the DID
        did_hash = user_did.calculate_did_hash()
        
        return did_document, did_hash

    

    def store_did_in_blockchain(self, username, public_key):
        """
        Store the DID document in the blockchain.

        Args:
            username (str): The username of the user.
            public_key (str): The public key of the user.

        Returns:
            Transaction: The transaction created for storing the DID.
        """
        # Check if the username is available
        if not self.is_username_available(username):
            flash(f"User '{username}' is already registered.", 'danger')
            return None  # Or handle as needed

        # Create a DID document
        did_document = {
            "@context": "https://www.w3.org/ns/did/v1",
            "id": f"did:example:{username}",
            "publicKey": [{
                "id": f"did:example:{username}#key-1",
                "type": "Ed25519VerificationKey2018",
                "controller": f"did:example:{username}",
                "publicKeyBase58": public_key
            }],
            "service": []
        }

        # Create the DID transaction
        did_transaction = Transaction(
            operation="STORE_DID",
            sender=username,
            recipient="DID_REGISTRY",
            data=json.dumps(did_document)  # Ensure the document is stored as a JSON string
        )

        # Add the transaction to the current transactions list
        self.current_transactions.append(did_transaction)

        # Add this line to create a new block with the DID transaction
        self.add_block()

        return did_transaction  # Return the transaction
    
    
    def find_did_in_blockchain(self, user_identifier):
        print(f"Searching for DID with user identifier: {user_identifier}")
        for index, block in enumerate(self.chain):
            print(f"Searching in block {index}")
            for transaction in block.transactions:
                print(f"Transaction: {transaction.to_dict()}")
                if transaction.sender == user_identifier and transaction.operation == "STORE_DID":
                    print(f"Found matching transaction: {transaction.to_dict()}")
                    # Parse the JSON string stored in transaction.data
                    return json.loads(transaction.data)  # Return the parsed JSON object
        print("DID not found in blockchain")
        return None
    

    def validate_chain(self, verbose=False):
        """
        Validate the entire blockchain using stored data.
        :param verbose: If True, print detailed information during validation.
        :return: True if valid, False if not
        """
        for i in range(len(self.chain)):
            current_block = self.chain[i]
            
            if verbose:
                print(f"\nValidating block {i}:")
                print(f"  Current block hash: {current_block.hash}")

            # Check block hash
            calculated_hash = current_block.calculate_hash()
            if current_block.hash != calculated_hash:
                print(f"Invalid hash in block {i}")
                print(f"  Stored hash: {current_block.hash}")
                print(f"  Calculated hash: {calculated_hash}")
                return False

            # Additional validation checks can be added here

        print("Blockchain is valid")
        return True

    def is_valid_transaction(self, transaction):
        """
        Validate a transaction by comparing it with the original transaction data stored in the blockchain.
        """
        original_tx = next((tx for block in self.chain for tx in block.transactions 
                            if tx.get_transaction_id() == transaction.get_transaction_id()), None)
        
        if original_tx and original_tx.data != transaction.data:
            print(f"Transaction data mismatch: Original {original_tx.data}, Current {transaction.data}")
            return False
        return True

    def is_chain_valid(self):
        """
        Check if the blockchain is valid.
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            # Check if the current block's hash is valid
            if not current_block.is_valid():
                print(f"Invalid hash in block {i}")
                return False

            # Check if the previous_hash field points to the previous block's hash
            if current_block.previous_hash != previous_block.hash:
                print(f"Invalid previous hash in block {i}")
                return False

            # Check if all transactions in the block are valid
            for tx in current_block.transactions:
                if not tx.is_valid():
                    print(f"Invalid transaction in block {i}")
                    return False

        return True

    def pay_tax(self, payer, tax_authority, amount, tax_period):
        """
        Record a tax payment transaction.

        Args:
            payer (str): The DID of the payer.
            tax_authority (str): The DID of the tax authority.
            amount (float): The amount of tax paid.
            tax_period (str): The tax period or reference.

        Returns:
            Transaction: The created tax payment transaction.
        """
        if self.balance_manager.get_balance(payer) < amount:
            raise ValueError("Insufficient balance to pay tax")

        transaction = self.add_transaction(
            sender=payer,
            recipient=tax_authority,
            operation='TAX_PAYMENT',
            data={'amount': amount, 'tax_period': tax_period}
        )
        self.add_block()
        return transaction

    def grant_tax_credit(self, recipient, amount, reason):
        """
        Record a tax credit transaction.

        Args:
            recipient (str): The DID of the recipient.
            amount (float): The amount of the tax credit.
            reason (str): The reason for the tax credit.

        Returns:
            Transaction: The created tax credit transaction.
        """
        transaction = self.add_transaction(
            sender='TAX_AUTHORITY',
            recipient=recipient,
            operation='TAX_CREDIT',
            data={'amount': amount, 'reason': reason}
        )
        self.add_block()
        return transaction

    def record_tax_audit(self, audited_user, findings, adjustments):
        """
        Record a tax audit transaction.

        Args:
            audited_user (str): The DID of the audited user.
            findings (str): The findings of the audit.
            adjustments (dict): Any adjustments made as a result of the audit.

        Returns:
            Transaction: The created tax audit transaction.
        """
        transaction = self.add_transaction(
            sender='TAX_AUDITOR',
            recipient=audited_user,
            operation='TAX_AUDIT',
            data={'findings': findings, 'adjustments': adjustments}
        )
        self.add_block()
        return transaction

    def calculate_carbon_tax(self, user_did):
        """
        Calculate the total carbon tax for a user based on their reported emissions.

        Args:
            user_did (str): The DID of the user.

        Returns:
            float: The total carbon tax owed by the user.
        """
        total_tax = 0.0
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.sender == user_did and transaction.operation == 'CARBON_EMISSION':
                    # Assuming a tax rate of $X per ton of CO2 emitted
                    tax_rate = 10.0  # Example tax rate
                    total_tax += transaction.data['amount'] * tax_rate
        return total_tax
