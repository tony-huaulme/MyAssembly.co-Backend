from flask import Blueprint, redirect, url_for, session
from flask_dance.contrib.google import google
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    if not google.authorized:
        return redirect(url_for('google.login'))
    
    resp = google.get('/oauth2/v1/userinfo')
    assert resp.ok, resp.text
    user_info = resp.json()
    
    # Get user from DB or create a new one
    user = User.query.filter_by(email=user_info["email"]).first()
    if not user:
        user = User(username=user_info["name"], email=user_info["email"], google_id=user_info["id"])
        db.session.add(user)
        db.session.commit()
    
    session['user'] = user_info["name"]
    return f'Logged in as {session["user"]}'

@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))
