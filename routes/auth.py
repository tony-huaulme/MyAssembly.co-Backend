import json
import requests
from flask import jsonify, redirect, request, make_response
from oauthlib import oauth2
from models.models import db, AppUser
from config import Config
from flask import session

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



from flask import jsonify

def add_auth_routes(app,):
    @app.route('/auth/callback', methods=['GET'])
    # @limiter.limit("5 per minute")
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

        #extract what can give me the profile pic of the google account
        print(info)
        # Check if user already exists
        user = AppUser.query.filter_by(email=info['email']).first()
        new_user = False
        if not user:
            new_user = AppUser(username=info['name'], email=info['email'])
            db.session.add(new_user)
            db.session.commit()

        #set user id in session
        session['user_id'] = new_user.id if not user else user.id
        session.permanent = True
        # response = make_response(redirect(f"{'http://localhost:3000' if Config.ENV == 'development' else 'https://www.myassembly.co'}/authenticated"))
        # response.set_cookie('user_email', info['email'], domain=".myassembly.co", secure=True, httponly=False)
        # response.set_cookie('user_name', info['name'], domain=".myassembly.co", secure=True, httponly=False)

        response = make_response(redirect(f"{'http://localhost:3000' if Config.ENV == 'development' else 'https://www.myassembly.co'}/dashboard/projects"))
        #?user_email={info['email']}&user_name={info['name']}&new_user={True if new_user else False}&picture={info['picture']}
        return response


    @app.route('/google_auth', methods=['GET'])
    # @limiter.limit("5 per minute")
    def google_auth():
        return jsonify({'redirect_url': REQ_URI}), 200

    @app.route('/signup/emailpw', methods=['POST'])
    # @limiter.limit("5 per minute")
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

        session['user_id'] = new_user.id if not user else user.id
        session.permanent = True

        response = make_response(redirect(f"{'http://localhost:3000' if Config.ENV == 'development' else 'https://www.myassembly.co'}/dashboard/projects"))

        return response

    @app.route('/login/emailpw', methods=['POST'])
    # @limiter.limit("5 per minute")
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
        

        session['user_id'] = user.id
        session.permanent = True
        return jsonify({'message': 'Login successful', 'user': {'id': user.id, 'email': user.email}}), 200

    @app.route('/logout')
    def logout():
        # Clear the session data to log out the user
        session.clear()
        # just return 200
        return jsonify({'message': 'Logged out successfully'}), 200
    
    # route to check if user is authenticated
    @app.route('/auth/check', methods=['GET'])
    def check_auth():
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'authenticated': False}), 200

        user = AppUser.query.get(user_id)
        if not user:
            return jsonify({'authenticated': False}), 200

        return jsonify({'authenticated': True, 'user': {'id': user.id, 'email': user.email}}), 200