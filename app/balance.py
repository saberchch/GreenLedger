class BalanceManager:
    def __init__(self):
        self.balances = {}  # Dictionary to store user balances

    def initialize_user(self, user_did):
        """Initialize a user's balance if not already present."""
        if user_did not in self.balances:
            self.balances[user_did] = 0  # Set initial balance to 0

    def get_balance(self, user_did):
        """Retrieve the balance of a user."""
        return self.balances.get(user_did, 0)

    def update_balance(self, user_did, amount):
        """Update the balance of a user."""
        if user_did not in self.balances:
            self.initialize_user(user_did)
        self.balances[user_did] += amount

    def send_tokens(self, sender_did, recipient_did, amount):
        """Transfer tokens from one user to another."""
        # Allow SYSTEM to send tokens without checking balance
        if sender_did == 'SYSTEM':
            self.update_balance(recipient_did, amount)  # Just update the recipient's balance
            return  # Exit the function after updating

        if self.get_balance(sender_did) < amount:
            raise ValueError("Insufficient balance")
        
        self.update_balance(sender_did, -amount)
        self.update_balance(recipient_did, amount)

    def print_balance(self, username):
        print(f"Balance before credit: {self.get_balance(username)}")  # Before adding credit
