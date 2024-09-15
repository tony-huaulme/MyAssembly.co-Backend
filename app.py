from flask import Flask, request
from models.models import db, User
from config import Config
from flask import jsonify
from flask_migrate import Migrate, upgrade, migrate
from routes.file import handle_file
from routes.auth import google_auth_callback, login_with_google, login_emailpw, signup_emailpw

app = Flask(__name__)
app.config.from_object(Config)

app.add_url_rule('/files/<path:filename>', view_func=handle_file, methods=['GET', 'POST', 'DELETE'])

# Add routes for OAuth
app.add_url_rule('/auth/callback', view_func=google_auth_callback, methods=['GET'])
app.add_url_rule('/login/google', view_func=login_with_google, methods=['GET'])

# Add routes for email-password auth
app.add_url_rule('/signup/emailpw', view_func=signup_emailpw, methods=['POST'])
app.add_url_rule('/login/emailpw', view_func=login_emailpw, methods=['POST'])

# Initialize extensions
db.init_app(app)



# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

@app.route('/resetdb', methods=['POST'])
def reset_db():
    try:
        # Drop all tables
        db.drop_all()
        # Create all tables
        db.create_all()
        # Apply migrations
        with app.app_context():
            migrate.upgrade()
        return jsonify({'message': 'Database reset and upgraded successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Define a route where we see if user logged in if so show his email console
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_list = [{'id': user.id, 'username': user.username, 'email': user.email} for user in users]
    return jsonify(users_list)

@app.route('/users', methods=['POST'])
def add_user():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    if not username or not email:
        return jsonify({'error': 'Missing username or email'}), 400
    
    # Check if user already exists
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({'error': 'User already exists'}), 409
    

    new_user = User(username=username, email=email)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User added successfully', 'user': {'id': new_user.id, 'username': new_user.username, 'email': new_user.email}}), 201





with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000, ssl_context='adhoc')