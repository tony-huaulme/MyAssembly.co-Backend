from flask import jsonify, session
from models.models import  db, AppUser, Project



def add_user_routes(app):
    @app.route('/users', methods=['GET'])
    def get_users():

        sender_user_id = session.get('user_id')

        if sender_user_id != 66:
            return jsonify({"message": "Not authorized"}), 401

        users = AppUser.query.all()
        users_list = [{'id': user.id, 'username': user.username, 'email': user.email} for user in users]
        return jsonify(users_list)
    
    # delete user
    @app.route('/users/<int:user_id>', methods=['GET'])
    def delete_user(user_id):

        # if user id from session  not 66 return 404

        sender_user_id = session.get('user_id')

        if sender_user_id != 66:
            return jsonify({"message": "Not authorized"}), 401

        user = AppUser.query.get(user_id)
        if not user:
            return jsonify({"message": f"User with ID {user_id} does not exist."}), 404
        
        # get all projects of user, then delete them
        projects = Project.query.filter_by(user_id=user_id).all()
        for project in projects:
            db.session.delete(project)

        try:
            db.session.delete(user)
            db.session.commit()
        except Exception as e:
            return jsonify({"message": str(e)}), 400
        
        return jsonify({"message": f"User with ID {user_id} deleted successfully."}), 200