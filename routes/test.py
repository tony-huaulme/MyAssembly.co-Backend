from models.models import db, AppUser, Project, SharedProject, File3D
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import string
import random

def test():
    test_results = {
        'AppUser': test_app_user(),
        'Project': test_project(),
        'SharedProject': test_shared_project(),
        'File3D': test_file3d(),
       
    }
    return jsonify(test_results), 200

def generate_random_string(length=6):
    """Generate a random string of fixed length"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def test_app_user():
    try:
        # Generate a unique email with random characters to avoid conflicts
        unique_email = f"test_user_{generate_random_string()}@example.com"
        new_user = AppUser(username="test_user", email=unique_email)
        new_user.set_password("testpassword")

        # Check if email already exists
        if AppUser.query.filter_by(email=new_user.email).first():
            raise ValueError(f"User with email {new_user.email} already exists.")

        db.session.add(new_user)
        db.session.commit()

        # Query the user
        user = AppUser.query.filter_by(email=unique_email).first()
        if not user or not user.check_password("testpassword"):
            raise ValueError("User creation or password check failed.")

        # Update the user
        user.username = "updated_user"
        db.session.commit()

        return "Passed"
    except IntegrityError as e:
        db.session.rollback()  # Roll back in case of an integrity error
        return f"Failed: IntegrityError - {str(e)}"
    except SQLAlchemyError as e:
        db.session.rollback()
        return f"Failed: SQLAlchemyError - {str(e)}"
    except Exception as e:
        db.session.rollback()
        return f"Failed: {str(e)}"

def test_project():
    try:
        # Generate a unique email for the user
        unique_email = f"project_user_{generate_random_string()}@example.com"
        new_user = AppUser(username="project_user", email=unique_email)
        db.session.add(new_user)
        db.session.commit()

        # Create a new project for the user
        new_project = Project(user_id=new_user.id, project_name="Test Project", file3d_link="s3://test/project")

        # Check if project name already exists for this user
        if Project.query.filter_by(user_id=new_user.id, project_name=new_project.project_name).first():
            raise ValueError(f"Project '{new_project.project_name}' already exists for user {new_user.email}.")

        db.session.add(new_project)
        db.session.commit()

        # Query the project
        project = Project.query.filter_by(user_id=new_user.id, project_name="Test Project").first()
        if not project:
            raise ValueError("Project creation failed.")
        
        # Update the project
        project.project_name = "Updated Project"
        db.session.commit()

        return "Passed"
    except IntegrityError as e:
        db.session.rollback()
        return f"Failed: IntegrityError - {str(e)}"
    except SQLAlchemyError as e:
        db.session.rollback()
        return f"Failed: SQLAlchemyError - {str(e)}"
    except Exception as e:
        db.session.rollback()
        return f"Failed: {str(e)}"

def test_shared_project():
    try:
        # Generate a unique email for the user
        unique_email = f"shared_user_{generate_random_string()}@example.com"
        new_user = AppUser(username="shared_user", email=unique_email)
        db.session.add(new_user)
        db.session.commit()

        # Create a new project for the user
        new_project = Project(user_id=new_user.id, project_name="Shared Project", file3d_link="s3://shared/project")
        db.session.add(new_project)
        db.session.commit()

        # Create a unique share link
        unique_share_link = f"http://example.com/shared/{generate_random_string()}"
        shared_project = SharedProject(project_id=new_project.id, share_link=unique_share_link)

        # Check if the share link already exists
        if SharedProject.query.filter_by(share_link=unique_share_link).first():
            raise ValueError(f"Shared link '{unique_share_link}' already exists.")

        db.session.add(shared_project)
        db.session.commit()

        # Query the shared project
        shared = SharedProject.query.filter_by(share_link=unique_share_link).first()
        if not shared:
            raise ValueError("SharedProject creation failed.")

        return "Passed"
    except IntegrityError as e:
        db.session.rollback()
        return f"Failed: IntegrityError - {str(e)}"
    except SQLAlchemyError as e:
        db.session.rollback()
        return f"Failed: SQLAlchemyError - {str(e)}"
    except Exception as e:
        db.session.rollback()
        return f"Failed: {str(e)}"

def test_file3d():
    try:
        # Generate a unique email for the user
        unique_email = f"file3d_user_{generate_random_string()}@example.com"
        new_user = AppUser(username="file3d_user", email=unique_email)
        db.session.add(new_user)
        db.session.commit()

        # Create a new project for the user
        new_project = Project(user_id=new_user.id, project_name="3D File Project", file3d_link="s3://3dfile/project",file_size=100)
        db.session.add(new_project)
        db.session.commit()

        # Create a unique S3 file URL
        unique_s3_url = f"s3://3dfile/project/model_{generate_random_string()}.obj"
        file3d = File3D(project_id=new_project.id, s3_file_url=unique_s3_url, file_type=".obj")

        # Check if the file URL already exists
        if File3D.query.filter_by(s3_file_url=unique_s3_url).first():
            raise ValueError(f"File3D with URL '{unique_s3_url}' already exists.")

        db.session.add(file3d)
        db.session.commit()

        # Query the File3D
        file = File3D.query.filter_by(s3_file_url=unique_s3_url).first()
        if not file:
            raise ValueError("File3D creation failed.")

        return "Passed"
    except IntegrityError as e:
        db.session.rollback()
        return f"Failed: IntegrityError - {str(e)}"
    except SQLAlchemyError as e:
        db.session.rollback()
        return f"Failed: SQLAlchemyError - {str(e)}"
    except Exception as e:
        db.session.rollback()
        return f"Failed: {str(e)}"

