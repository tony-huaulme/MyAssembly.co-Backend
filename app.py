from flask import Flask, request, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_dance.contrib.google import make_google_blueprint, google
from models import db, User
from config import Config
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from io import BytesIO
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
    redirect_to='auth.google_authorized',
    scope=['https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email'] 
)
app.register_blueprint(google_bp, url_prefix='/login')

# Initialize S3 client
s3 = boto3.client('s3',
                  aws_access_key_id=app.config['AWS_ACCESS'],
                  aws_secret_access_key=app.config['AWS_SECRET'],
                  region_name=app.config['AWS_REGION'])

@app.route('/')
def index():
    return "Welcome to the Flask App with Google OAuth! <a href='/login'>Login</a>"


#Handle files
@app.route('/files/<path:filename>', methods=['GET', 'POST', 'DELETE'])
def handle_file(filename):
    if request.method == 'GET':
        # Download file
        try:
            response = s3.get_object(Bucket=app.config['AWS_BUCKET_NAME'], Key=filename)
            file_stream = BytesIO(response['Body'].read())
            return send_file(file_stream, as_attachment=True, download_name=filename.split('/')[-1])
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return jsonify({'error': 'File not found'}), 404
            else:
                return jsonify({'error': str(e)}), 500
        except NoCredentialsError:
            return jsonify({'error': 'Credentials not available'}), 403

    elif request.method == 'POST':
        # Upload file
        file = request.files.get('file')
        if file:
            try:
                s3.upload_fileobj(file, app.config['AWS_BUCKET_NAME'], filename)
                return jsonify({'message': 'File uploaded successfully'}), 201
            except NoCredentialsError:
                return jsonify({'error': 'Credentials not available'}), 403
            except ClientError as e:
                return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'No file provided'}), 400

    elif request.method == 'DELETE':
        # Delete file
        try:
            s3.delete_object(Bucket=app.config['AWS_BUCKET_NAME'], Key=filename)
            return jsonify({'message': 'File deleted successfully'}), 200
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return jsonify({'error': 'File not found'}), 404
            else:
                return jsonify({'error': str(e)}), 500
        except NoCredentialsError:
            return jsonify({'error': 'Credentials not available'}), 403

# Get all users
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_list = [{'id': user.id, 'username': user.username, 'email': user.email} for user in users]
    return jsonify(users_list)

# Add a new user
@app.route('/users', methods=['POST'])
def add_user():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    if not username or not email:
        return jsonify({'error': 'Missing username or email'}), 400
    new_user = User(username=username, email=email)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User added successfully', 'user': {'id': new_user.id, 'username': new_user.username, 'email': new_user.email}}), 201


# Create the tables (if they don’t exist already)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
