import json
import requests
from flask import jsonify, redirect, request
from oauthlib import oauth2
from models.models import db, AppUser
from config import Config

# Google OAuth2 configuration
CLIENT_ID = Config.GOOGLE_OAUTH_CLIENT_ID
CLIENT_SECRET = Config.GOOGLE_OAUTH_CLIENT_SECRET


DATA = {
    'response_type': "code",
    'redirect_uri': Config.GOOGLE_OAUTH_REDIRECT_URI,#"https://www.backend.myassembly.co/home"
    'scope': ['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'],
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

#GOOGLE-AUTH
def login_with_google():
    return redirect(REQ_URI)

def google_auth_callback():
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

    # Check if user already exists
    user = AppUser.query.filter_by(email=info['email']).first()
    if not user:
        new_user = AppUser(username=info['name'], email=info['email'])
        db.session.add(new_user)
        db.session.commit()

    return jsonify({"email": info['email'], "username": info['name']})


#EMAIL-PASSWORD-AUTH
def signup_emailpw():
    data = request.json
    email = data.get('email').lower()
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Missing username, email, or password'}), 400

    # Check if user already exists
    user = AppUser.query.filter_by(email=email).first()
    if user:
        return jsonify({'error': 'User already exists'}), 409

    # Create new user and hash the password
    new_user = AppUser(email=email)
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully', 'id': new_user.id, 'email': new_user.email}), 201


def login_emailpw():
    data = request.json
    email = data.get('email').lower()
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400

    # Find user by email
    user = AppUser.query.filter_by(email=email).first()
    if user is None or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401

    return jsonify({'message': 'Login successful', 'user': {'id': user.id, 'username': user.username, 'email': user.email}}), 200