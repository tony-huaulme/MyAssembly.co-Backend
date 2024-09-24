from flask import jsonify
from models.models import  AppUser

def add_user_routes(app):
    @app.route('/users', methods=['GET'])
    def get_users():
        users = AppUser.query.all()
        users_list = [{'id': user.id, 'username': user.username, 'email': user.email} for user in users]
        return jsonify(users_list)