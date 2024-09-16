from flask import Flask, request
from models.models import db, AppUser, Project, SharedProject, File3D
from config import Config
from flask import jsonify
from flask_migrate import Migrate

from routes.file import handle_file
from routes.auth import google_auth_callback, login_with_google, login_emailpw, signup_emailpw
from routes.test import test
from routes.admin import rendertables
app = Flask(__name__)
app.config.from_object(Config)




# Add routes for file handling
app.add_url_rule('/files/<path:filename>', view_func=handle_file, methods=['GET', 'POST', 'DELETE'])

###########################################
########## AUTHENTICATION ROUTES ##########
###########################################
# Add routes for OAuth
app.add_url_rule('/auth/callback', view_func=google_auth_callback, methods=['GET'])
app.add_url_rule('/login/google', view_func=login_with_google, methods=['GET'])
# Add routes for email-password auth
app.add_url_rule('/signup/emailpw', view_func=signup_emailpw, methods=['POST'])
app.add_url_rule('/login/emailpw', view_func=login_emailpw, methods=['POST'])

###########################################
################ TEST-ADMIN ###############
###########################################
#addding test route
app.add_url_rule('/test', view_func=test, methods=['GET'])
app.add_url_rule('/dbui', view_func=rendertables, methods=['GET'])

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)





@app.route('/projects', methods=['POST'])
def create_project():
    data = request.get_json()
    print("\n\n",data, "\n\n")  # Debugging line
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    user_id = data.get('user_id')
    project_name = data.get('project_name')
    description = data.get('description')
    s3_folder = data.get('s3_folder')

    # Check if required fields are provided
    if not user_id or not project_name or not s3_folder:
        return jsonify({"message": "User ID, project name, and S3 folder are required"}), 400

    # Check if the user exists in the database
    user = AppUser.query.get(user_id)
    if not user:
        return jsonify({"message": f"User with ID {user_id} does not exist."}), 400

    try:
        new_project = Project(
            user_id=user_id,
            project_name=project_name,
            description=description,
            s3_folder=s3_folder
        )
        db.session.add(new_project)
        db.session.commit()
    except Exception as e:
        print("Error: ", e)
        return jsonify({"message": str(e)}), 400

    return jsonify({
        "id": new_project.id,
        "user_id": new_project.user_id,
        "project_name": new_project.project_name,
        "description": new_project.description,
        "s3_folder": new_project.s3_folder,
        "created_at": new_project.created_at.isoformat(),
        "updated_at": new_project.updated_at.isoformat()
    }), 201







# Define a route where we see if user logged in if so show his email console
@app.route('/users', methods=['GET'])
def get_users():
    users = AppUser.query.all()
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
    user = AppUser.query.filter_by(email=email).first()
    if user:
        return jsonify({'error': 'User already exists'}), 409
    

    new_user = AppUser(username=username, email=email)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User added successfully', 'user': {'id': new_user.id, 'username': new_user.username, 'email': new_user.email}}), 201




with app.app_context():
    db.create_all()

if __name__ == "__main__":
    #params to run https
    app.run(debug=True, host='0.0.0.0', port=5000, ssl_context=('adhoc'))
