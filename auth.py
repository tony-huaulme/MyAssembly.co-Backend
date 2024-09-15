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
    print("\n\nUser Info\n\n")
    print(user_info)
    print("\n\n....\n\n")
    
    # Get user from DB or create a new one
    user = User.query.filter_by(email=user_info.get("email")).first()
    if not user:
        user = User(username=user_info.get("name"), email=user_info.get("email"), google_id=user_info.get("id"))
        db.session.add(user)
        db.session.commit()
    
    session['user'] = user_info.get("name")
    return f'Logged in as {session["user"]}'

@auth_bp.route('/login/google/authorized')
def google_authorized():
    if not google.authorized:
        return redirect(url_for('google.login'))
    
    resp = google.get('/oauth2/v1/userinfo')
    assert resp.ok, resp.text
    user_info = resp.json()
    
    # Process user information and update session
    user = User.query.filter_by(email=user_info.get("email")).first()
    if not user:
        user = User(username=user_info.get("name"), email=user_info.get("email"), google_id=user_info.get("id"))
        db.session.add(user)
        db.session.commit()
    
    session['user'] = user_info.get("name")
    return f'Logged in as {session["user"]}'

@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))
