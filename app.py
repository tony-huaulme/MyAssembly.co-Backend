from flask import Flask, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_dance.contrib.google import make_google_blueprint, google
from models import db, User
from config import Config
from auth import auth_bp  # Import the auth_bp blueprint from auth.py

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)

# Register the auth blueprint
app.register_blueprint(auth_bp)  # Registering the auth_bp blueprint

# Google OAuth blueprint
google_bp = make_google_blueprint(
    client_id=app.config['GOOGLE_OAUTH_CLIENT_ID'],
    client_secret=app.config['GOOGLE_OAUTH_CLIENT_SECRET'],
    redirect_to='auth.login'  # Redirect to the login route in the auth blueprint
)
app.register_blueprint(google_bp, url_prefix='/login')

@app.route('/')
def index():
    return "Welcome to the Flask App with Google OAuth! <a href='/login'>Login</a>"

# Create the tables (if they don’t exist already)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
