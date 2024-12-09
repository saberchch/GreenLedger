import hashlib
import time

class GreenToken:
    def __init__(self, identifier, user_did, expiration_time):
        """
        Initialize the GreenToken with an identifier, user DID, and expiration time.

        Args:
            identifier (str): A unique identifier for the token.
            user_did (str): The DID of the user associated with the token.
            expiration_time (float): The amount of time in seconds before the token expires.
        """
        self.identifier = identifier  # Unique identifier for the token
        self.user_did = user_did  # The DID of the user associated with the token
        self.creation_time = time.time()  # Token creation time in epoch format
        self.expiration_time = expiration_time  # Expiration time in seconds
        self.revoked = False  # Flag indicating if the token has been revoked

    def revoke(self):
        """Mark the token as revoked."""
        self.revoked = True

    def is_valid(self):
        """
        Check if the token is valid (not revoked and not expired).
        
        Returns:
            bool: True if the token is valid, False otherwise.
        """
        current_time = time.time()
        return not self.revoked and current_time < self.creation_time + self.expiration_time

    def calculate_token_hash(self):
        """
        Calculate a hash for the token for additional verification.

        Returns:
            str: The SHA-256 hash of the token's details.
        """
        token_string = f"{self.identifier}:{self.user_did}:{self.creation_time}:{self.expiration_time}:{self.revoked}".encode()
        return hashlib.sha256(token_string).hexdigest()

    def transfer(self, new_user_did):
        """
        Transfer the token to another user.

        Args:
            new_user_did (str): The DID of the new user.

        Raises:
            ValueError: If the token is revoked or expired.
        """
        if self.is_valid():
            self.user_did = new_user_did
        else:
            raise ValueError("Cannot transfer revoked or expired token.")

class TokenStake:
    def __init__(self, blockchain):
        self.blockchain = blockchain
        self.user_stakes = {}  # Initialize the user_stakes dictionary

    def stake_tokens(self, user_did, amount):
        # Validate input
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        # Check if the user has enough balance
        user_balance = self.blockchain.user_balance_manager.get_balance(user_did)
        if user_balance < amount:
            raise ValueError("Insufficient balance to stake.")

        # Update the user's stake
        self.user_stakes[user_did] = self.user_stakes.get(user_did, 0) + amount

        # Update the user's balance
        self.blockchain.user_balance_manager.update_balance(user_did, user_balance - amount)

        # Create a transaction for staking
        self.blockchain.add_transaction(
            sender=user_did,
            recipient="STAKE_POOL",
            operation="STAKE",
            data={"amount": amount}
        )
        self.blockchain.add_block()

        print(f"User {user_did} staked {amount} tokens. New stake: {self.user_stakes[user_did]}, New balance: {self.blockchain.user_balance_manager.get_balance(user_did)}")

    def unstake_tokens(self, user_did, amount):
        # Validate input
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        # Check if the user has enough staked tokens
        if self.user_stakes.get(user_did, 0) < amount:
            raise ValueError("Insufficient stake to unstake.")

        # Update the user's stake
        self.user_stakes[user_did] -= amount
        if self.user_stakes[user_did] == 0:
            del self.user_stakes[user_did]

        # Update the user's balance
        current_balance = self.blockchain.user_balance_manager.get_balance(user_did)
        self.blockchain.user_balance_manager.update_balance(user_did, current_balance + amount)

        # Create a transaction for unstaking
        self.blockchain.add_transaction(
            sender="STAKE_POOL",
            recipient=user_did,
            operation="UNSTAKE",
            data={"amount": amount}
        )
        self.blockchain.add_block()

        print(f"User {user_did} unstaked {amount} tokens. New stake: {self.user_stakes.get(user_did, 0)}")

    def get_stake(self, user_did):
        """Retrieve the current stake of a user."""
        stake = self.user_stakes.get(user_did, 0)
        print(f"Current stake for {user_did}: {stake}")  # Debugging: Print the stake
        return stake

    def drop_tokens(self, sender_did, recipient_did, amount):
        # Validate input
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        # Ensure both sender and recipient are initialized
        self.blockchain.user_balance_manager.initialize_user(sender_did)
        self.blockchain.user_balance_manager.initialize_user(recipient_did)

        # Check if the sender has enough balance
        sender_balance = self.blockchain.calculate_user_balance(sender_did)
        if sender_balance < amount:
            raise ValueError("Insufficient balance to drop.")

        # Use the UserBalance class to update balances
        self.blockchain.user_balance_manager.send_tokens(sender_did, recipient_did, amount)

        # Create a transaction for dropping
        self.blockchain.add_transaction(
            sender=sender_did,
            recipient=recipient_did,
            operation="DROP",
            data={"amount": amount}
        )
        self.blockchain.add_block()

class TokenManager:
    def __init__(self, blockchain):
        self.blockchain = blockchain

    def transfer_tokens(self, sender, recipient, amount):
        if self.blockchain.get_balance(sender) < amount:
            raise ValueError("Insufficient balance")
        transaction = self.blockchain.add_transaction(
            sender=sender,
            recipient=recipient,
            operation='TOKEN_TRANSFER',
            data={'amount': amount}
        )
        self.blockchain.add_block()
        return transaction

    def mint_tokens(self, recipient, amount):
        transaction = self.blockchain.add_transaction(
            sender='SYSTEM',
            recipient=recipient,
            operation='MINT_TOKENS',
            data={'amount': amount}
        )
        self.blockchain.add_block()
        return transaction

    def burn_tokens(self, sender, amount):
        if self.blockchain.get_balance(sender) < amount:
            raise ValueError("Insufficient balance")
        transaction = self.blockchain.add_transaction(
            sender=sender,
            recipient='SYSTEM',
            operation='BURN_TOKENS',
            data={'amount': amount}
        )
        self.blockchain.add_block()
        return transaction
