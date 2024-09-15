import json
import requests
from flask import Flask, redirect, request
from oauthlib import oauth2
from models.models import db, User
from config import Config
from io import BytesIO
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from flask import send_file, jsonify

app = Flask(__name__)
app.config.from_object(Config)

# Google OAuth2 configuration
CLIENT_ID = app.config['GOOGLE_OAUTH_CLIENT_ID']
CLIENT_SECRET = app.config['GOOGLE_OAUTH_CLIENT_SECRET']


DATA = {
    'response_type': "code",
    'redirect_uri': "https://www.backend.myassembly.co/home",
    'scope': 'https://www.googleapis.com/auth/userinfo.email',
    'client_id': CLIENT_ID,
    'prompt': 'consent'
}
URL_DICT = {
    'google_oauth': 'https://accounts.google.com/o/oauth2/v2/auth',
    'token_gen': 'https://oauth2.googleapis.com/token',
    'get_user_info': 'https://www.googleapis.com/oauth2/v3/userinfo'
}
CLIENT = oauth2.WebApplicationClient(CLIENT_ID)
REQ_URI = CLIENT.prepare_request_uri(
    uri=URL_DICT['google_oauth'],
    redirect_uri=DATA['redirect_uri'],
    scope=DATA['scope'],
    prompt=DATA['prompt']
)


# Initialize extensions
db.init_app(app)

# Initialize S3 client
s3 = boto3.client('s3',
                  aws_access_key_id=app.config['AWS_ACCESS'],
                  aws_secret_access_key=app.config['AWS_SECRET'],
                  region_name=app.config['AWS_REGION'])

@app.route('/')
def login():
    return redirect(REQ_URI)

@app.route('/home')
def home():
    code = request.args.get('code')
    token_url, headers, body = CLIENT.prepare_token_request(
        URL_DICT['token_gen'],
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(CLIENT_ID, CLIENT_SECRET)
    )
    CLIENT.parse_request_body_response(json.dumps(token_response.json()))
    uri, headers, body = CLIENT.add_token(URL_DICT['get_user_info'])
    response_user_info = requests.get(uri, headers=headers, data=body)
    info = response_user_info.json()
    return redirect('/user/%s' % info['email'])

@app.route('/user/<email>')
def login_success(email):
    return "Hello %s" % email

@app.route('/files/<path:filename>', methods=['GET', 'POST', 'DELETE'])
def handle_file(filename):
    if request.method == 'GET':
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
    new_user = User(username=username, email=email)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User added successfully', 'user': {'id': new_user.id, 'username': new_user.username, 'email': new_user.email}}), 201

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000, ssl_context='adhoc')