# GreenLedger

GreenLedger is a carbon tax management platform designed to help engineers and organizations manage their carbon emissions and comply with environmental regulations. The application allows users to report carbon emissions, view their balance of carbon credits, and access transaction history, all while promoting sustainable practices.

## Features

- **User Registration and Login**: Secure user authentication with role-based access.
- **Carbon Emission Reporting**: Users can report their carbon emissions based on their profession (Civil, Mechanical, Electronics).
- **Balance Management**: Users can view their current balance of carbon credits and tokens.
- **Transaction History**: Access a history of carbon-related transactions.
- **Dashboard**: Profession-specific dashboards for engineers to manage their emissions and view relevant information.
- **Contact Us**: A contact form for users to reach out for support or inquiries.
- **Blockchain Integration**: All transactions are securely recorded on a blockchain.

## Technologies Used

- **Flask**: A lightweight WSGI web application framework for Python.
- **Bootstrap**: A front-end framework for developing responsive web applications.
- **Cryptography**: For secure handling of user data and transactions.
- **Blockchain**: For immutable transaction records.

## Installation

To set up the GreenLedger application locally, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/saberchch/GreenLedger.git
   cd GreenLedger
   ```

2. **Create a Virtual Environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   ```bash
   flask run
   ```

5. **Access the Application**: Open your web browser and go to `http://127.0.0.1:5000`.

## Usage

- **Register**: Create a new account by providing a username and profession.
- **Login**: Access your dashboard by logging in with your credentials.
- **Report Emissions**: Use the dashboard to report your carbon emissions.
- **View Blockchain**: Access the blockchain to see all recorded transactions.
- **Contact Support**: Use the contact form for any inquiries or support requests.

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the contributors and the open-source community for their support and resources.
