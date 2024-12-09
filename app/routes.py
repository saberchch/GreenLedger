from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, current_user, logout_user
from app.forms import RegistrationForm, LoginForm
from app.blockchain import Blockchain
from app.secret import SecretManager
from app.transaction import Transaction

main = Blueprint('main', __name__)
blockchain = Blockchain()
blockchain.load_blockchain()  # Load the blockchain from the JSON file
secret_manager = SecretManager()  # Create an instance of SecretManager


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()  # Create an instance of the RegistrationForm
    if form.validate_on_submit():
        username = form.username.data
        profession = form.profession.data  # Get the profession from the form
        
        # Generate a new secret phrase
        secret_phrase = secret_manager.generate_secret_phrase()
        
        # Encrypt the secret phrase
        encrypted_secret_phrase = secret_manager.encrypt_secret_phrase(secret_phrase)
        
        # Generate public/private key pair from the secret phrase
        public_key, private_key = secret_manager.generate_key_from_secret_phrase(secret_phrase)
        
        # Check if the username is available
        if not blockchain.is_username_available(username):
            flash(f"Username '{username}' is already taken.", 'danger')
            return render_template('register.html', form=form)  # Pass the form back to the template

        # Create the user registration transaction
        user_registration_transaction = blockchain.add_transaction(
            sender=username,
            recipient='SYSTEM',
            operation='USER_REGISTRATION',
            data={
                "encrypted_secret_phrase": encrypted_secret_phrase,
                "public_key": public_key.decode('utf-8'),
                "profession": profession
            }
        )

        # Add the user registration transaction to a new block
        blockchain.add_block(user_registration_transaction)

        # Create a CREDIT transaction to initialize the user's balance with 10 tokens
        credit_transaction = blockchain.add_transaction(
            sender='SYSTEM',
            recipient=username,
            operation='CREDIT',
            data={'amount': 10}
        )

        # Add the credit transaction to a new block
        blockchain.add_block(credit_transaction)

        # Flash message with the secret phrase and security recommendation
        flash(f"Registration successful! Your initial balance is 10 tokens.", 'success')
        
        # Store the secret phrase in the session
        session['secret_phrase'] = secret_phrase  # Store the secret phrase in the session
        
        # Redirect to the secret key explanation page
        return redirect(url_for('main.secret_key_explanation'))  # Redirect to the explanation page
            
    return render_template('register.html', form=form)  # Pass the form to the template

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        secret_phrase = form.secret_phrase.data
        
        # Retrieve user data using the correct method
        user_data = blockchain.get_user_data(username)
        
        if user_data:
            # Retrieve the encrypted secret phrase and profession
            encrypted_secret_phrase = user_data.get('encrypted_secret_phrase')
            profession = user_data.get('profession')  # Retrieve the profession
            
            # Debugging output
            print(f"Retrieved Encrypted Secret Phrase: '{encrypted_secret_phrase}'")
            print(f"Retrieved Profession: '{profession}'")
            print(f"Provided Secret Phrase: '{secret_phrase}'")
            
            try:
                # Decrypt the stored encrypted secret phrase
                decrypted_secret_phrase = secret_manager.decrypt_secret_phrase(encrypted_secret_phrase)
                
                # Debugging: Print the decrypted secret phrase
                print(f"Decrypted Secret Phrase: '{decrypted_secret_phrase}'")
                
                # Verify the secret phrase
                if decrypted_secret_phrase == secret_phrase:
                    session['username'] = username
                    session['profession'] = profession  # Store the profession in the session
                    flash('Login successful! Welcome back.', 'success')
                    
                    # Redirect to the appropriate dashboard based on profession
                    return redirect_to_dashboard(profession)
                else:
                    flash('Invalid secret phrase. Please try again.', 'danger')
            except Exception as e:
                print(f"Decryption error: {e}")
                flash('An error occurred during login. Please try again.', 'danger')
        else:
            flash('Invalid username. Please try again.', 'danger')
    
    return render_template('login.html', form=form)

def get_user_data(username):
    """Retrieve user data from the blockchain."""
    user_data = blockchain.get_user_data(username)
    return user_data

def validate_secret_phrase(encrypted_secret_phrase, provided_secret_phrase):
    """Validate the provided secret phrase against the stored encrypted one."""
    return encrypted_secret_phrase and secret_manager.decrypt_secret_phrase(encrypted_secret_phrase) == provided_secret_phrase

def redirect_to_dashboard(profession):
    """Redirect to the appropriate dashboard based on the user's profession."""
    if profession == 'civil_engineer':
        return redirect(url_for('main.civil_engineer_dashboard'))
    elif profession == 'mechanical_engineer':
        return redirect(url_for('main.mechanical_engineer_dashboard'))
    elif profession == 'electronics_engineer':
        return redirect(url_for('main.electronics_engineer_dashboard'))
    else:
        return redirect(url_for('main.dashboard'))  # Default dashboard if profession is unknown

@main.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

@main.route('/user_dashboard')
def user_dashboard():
    if 'username' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('main.login'))
    
    username = session['username']
    profession = session['profession']
    
    # Redirect to the appropriate dashboard based on profession
    return redirect_to_dashboard(profession)

@main.route('/report_carbon_emission')
def report_carbon_emission():
    if request.method == 'POST':
        amount = request.form.get('amount', type=float)
        emission_source = request.form.get('emission_source')
        activity_type = request.form.get('activity_type')
        compliance_status = request.form.get('compliance_status')
        reporting_period = request.form.get('reporting_period')

        # Determine the user's profession
        profession = session.get('profession')

        # Create a carbon emission transaction based on the profession
        if profession == 'civil engineer':
            carbon_emission_transaction = blockchain.add_civil_engineering_transaction(
                sender=session['username'],
                recipient='DID:example:environmentalAgency',
                amount=amount,
                emission_source=emission_source,
                activity_type=activity_type,
                compliance_status=compliance_status,
                reporting_period=reporting_period
            )
        elif profession == 'mechanical engineer':
            carbon_emission_transaction = blockchain.add_mechanical_engineering_transaction(
                sender=session['username'],
                recipient='DID:example:environmentalAgency',
                amount=amount,
                emission_source=emission_source,
                activity_type=activity_type,
                compliance_status=compliance_status,
                reporting_period=reporting_period
            )
        elif profession == 'electronics engineer':
            carbon_emission_transaction = blockchain.add_electronics_engineering_transaction(
                sender=session['username'],
                recipient='DID:example:environmentalAgency',
                amount=amount,
                emission_source=emission_source,
                activity_type=activity_type,
                compliance_status=compliance_status,
                reporting_period=reporting_period
            )
        else:
            flash('Invalid profession. Unable to report emissions.', 'danger')
            return redirect(url_for('main.civil_engineer_dashboard'))

        # Add the transaction to the blockchain
        blockchain.add_transaction(carbon_emission_transaction)
        flash('Carbon emission reported successfully!', 'success')
        return redirect(url_for('main.civil_engineer_dashboard'))

    return render_template('civil_engineer_dashboard.html', username=session['username'])

@main.route('/engineer_dashboard')
def engineer_dashboard():
    if 'username' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('main.login'))
    
    username = session['username']
    return render_template('engineer_dashboard.html', username=username)

@main.route('/manager_dashboard')
def manager_dashboard():
    if 'username' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('main.login'))
    
    username = session['username']
    return render_template('manager_dashboard.html', username=username)

@main.route('/analyst_dashboard')
def analyst_dashboard():
    if 'username' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('main.login'))
    
    username = session['username']
    return render_template('analyst_dashboard.html', username=username)

@main.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('main.login'))
    
    profession = session['profession']
    
    if profession == 'civil engineer':
        return redirect(url_for('main.civil_engineer_dashboard'))
    elif profession == 'mechanical engineer':
        return redirect(url_for('main.mechanical_engineer_dashboard'))
    elif profession == 'electronics engineer':
        return redirect(url_for('main.electronics_engineer_dashboard'))
    else:
        flash('Invalid profession. Unable to access dashboard.', 'danger')
        return redirect(url_for('main.index'))

@main.route('/civil_engineer_dashboard')
def civil_engineer_dashboard():
    if 'username' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('main.login'))
    
    username = session['username']
    return render_template('civil_engineer_dashboard.html', username=username)

@main.route('/mechanical_engineer_dashboard')
def mechanical_engineer_dashboard():
    if 'username' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('main.login'))
    
    username = session['username']
    return render_template('mechanical_engineer_dashboard.html', username=username)

@main.route('/electronics_engineer_dashboard')
def electronics_engineer_dashboard():
    if 'username' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('main.login'))
    
    username = session['username']
    return render_template('electronics_engineer_dashboard.html', username=username)

@main.route('/secret_key_explanation')
def secret_key_explanation():
    secret_phrase = session.get('secret_phrase')  # Get the secret phrase from the session
    return render_template('secret_key_explanation.html', secret_phrase=secret_phrase)

@main.route('/view_blockchain')
def view_blockchain():
    # Placeholder for viewing the blockchain
    return render_template('view_blockchain.html')  # Create this template later

@main.route('/create_report')
def create_report():
    # Placeholder for creating reports
    return render_template('create_report.html')  # Create this template later

@main.route('/submit_carbon_emission')
def submit_carbon_emission():
    # Placeholder for submitting carbon emissions
    return render_template('report_carbon_emission.html')  # Create this template later

@main.route('/create_project')
def create_project():
    # Placeholder for creating a project
    return render_template('create_project.html')  # Create this template later

@main.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
    if request.method == 'POST':
        # Handle form submission
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # Here you can add logic to process the contact form, such as sending an email or saving to a database
        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('main.contact_us'))

    return render_template('contact_us.html')

@main.route('/view_balance_history')
def view_balance_history():
    # Placeholder for balance history logic
    # You can retrieve the balance history from the blockchain and pass it to the template
    return render_template('balance_history.html')  # Create this template later
  