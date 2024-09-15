from flask import Blueprint, redirect, url_for, session, request
from oauthlib.oauth2 import WebApplicationClient
from requests_oauthlib import OAuth2Session
from models.models import db, User
import os

auth_bp = Blueprint('auth', __name__)

# Google OAuth2 configuration
CLIENT_ID = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET')
AUTHORIZATION_BASE_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
TOKEN_URL = 'https://oauth2.googleapis.com/token'
USER_INFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'

# Create a client instance
client = WebApplicationClient(CLIENT_ID)

@auth_bp.route('/login')
def login():
    authorization_url, state = client.authorization_url(
        AUTHORIZATION_BASE_URL,
        access_type='offline',
        prompt='consent',
        redirect_uri=url_for('auth.google_authorized', _external=True)
    )
    session['oauth_state'] = state
    return redirect(authorization_url)

@auth_bp.route('/login/google/authorized')
def google_authorized():
    # Get authorization response
    code = request.args.get('code')
    token_url, headers, body = client.prepare_token_request(
        TOKEN_URL,
        authorization_response=request.url,
        redirect_url=url_for('auth.google_authorized', _external=True),
        code=code
    )

    # Fetch token
    oauth_session = OAuth2Session(CLIENT_ID, client_secret=CLIENT_SECRET)
    token_response = oauth_session.post(token_url, headers=headers, data=body)
    token_json = token_response.json()
    client.parse_request_body_response(token_response.text)

    # Get user info
    oauth_session = OAuth2Session(CLIENT_ID, token=token_json)
    user_info_response = oauth_session.get(USER_INFO_URL)
    user_info = user_info_response.json()
    print(user_info)
    user = User.query.filter_by(email=user_info.get("email")).first()
    if not user:
        print("Creating new user")
        user = User(username=user_info.get("name"), email=user_info.get("email"), google_id=user_info.get("sub"))
        db.session.add(user)
        db.session.commit()