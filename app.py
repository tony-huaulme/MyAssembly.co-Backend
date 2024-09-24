from flask import Flask, request, session, jsonify
from models.models import db, AppUser, Project
from config import Config
from flask_migrate import Migrate
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize the Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Setup CORS with dynamic origins
if app.config["ENV"] == "production":
    CORS(app, origins=["https://www.myassembly.co", "https://myassembly.co"])
else:
    CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

# Initialize Flask-Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["5 per minute"]
)

@app.before_request
def require_login():
    # Check if the route is not public
    if not session.get('user_id') and request.endpoint not in ['/auth/callback', '/google_auth', '/signup/emailpw', '/login/emailpw']:
        return jsonify({"error": "Not authorized"}), 401

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)

# Import and add routes
from routes.auth import add_auth_routes
from routes.admin import rendertables
from routes.project import add_project_routes
from routes.user import add_user_routes


# Add authentication routes
add_auth_routes(app, limiter)

# Add project routes
add_project_routes(app)

# Add user routes
add_user_routes(app)

# Add test routes
app.add_url_rule('/dbui', view_func=rendertables, methods=['GET'])

# Run the application
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000, ssl_context=('adhoc'))
