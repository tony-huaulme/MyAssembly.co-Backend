from flask import request, jsonify
from models.models import db, Project, AppUser
from flask import session

def add_project_routes(app):
    @app.route('/projects', methods=['POST', 'OPTIONS'])
    def create_project():

        if request.method == 'OPTIONS':
            response = jsonify({'message': 'CORS Preflight'})
            response.headers.add('Access-Control-Allow-Origin', 'https://www.myassembly.co')
            response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response, 200

        # Access form data instead of JSON
        project_name = request.form.get('project_name')
        file3d_link = request.form.get('file3d_link')

        if not project_name or not file3d_link:
            return jsonify({"message": "Project name and file3d link are required"}), 400

        user_id = session.get('user_id')

        if not user_id:
            return jsonify({"message": "User ID is required"}), 400

        user = AppUser.query.get(user_id)
        if not user:
            return jsonify({"message": f"User with ID {user_id} does not exist."}), 400

        try:
            new_project = Project(
                user_id=user_id,
                project_name=project_name,
                file3d_link=file3d_link
            )
            db.session.add(new_project)
            db.session.commit()

        except Exception as e:
            return jsonify({"message": str(e)}), 400

        return jsonify({
            "id": new_project.id,
            "user_id": new_project.user_id,
            "project_name": new_project.project_name,
            "file3d_link": new_project.file3d_link,
            "created_at": new_project.created_at.isoformat(),
            "updated_at": new_project.updated_at.isoformat()
        }), 201


    @app.route('/projects', methods=['GET'])
    def get_projects():

        # Get the user_id from the session
        user_id = session['user_id']

        # Query the database for projects that belong to the logged-in user
        projects = Project.query.filter_by(user_id=user_id).all()

        # Convert the list of projects to a JSON-serializable format using the to_dict method
        projects_list = [project.to_dict() for project in projects]

        return jsonify({'projects': projects_list}), 200
    
    @app.route('/projects/<int:project_id>', methods=['GET'])
    def get_project(project_id):
        # Query the database for the project with the given project_id
        project = Project.query.filter_by(id=project_id).first()

        if not project:
            return jsonify({"message": "Project not found"}), 404

        return jsonify(project.to_dict()), 200
