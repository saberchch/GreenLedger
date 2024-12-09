from flask import Flask
from app.routes import main

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key_here'  # Replace with a secure key
    app.register_blueprint(main)
    return app 