from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

db = SQLAlchemy()

class AppUser(db.Model):
    __tablename__ = 'appuser'  # Define the table name
    

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=False, nullable=True)  # Non-unique username, allowed to be nullable
    email = db.Column(db.String(150), unique=True, nullable=False)  # Unique and required
    password_hash = db.Column(db.String(128), nullable=True)  # Password can be null for OAuth users
    
    created_at = db.Column(db.DateTime, default=db.func.now())  # Timestamp when user was created
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())  # Auto-update timestamp when user info changes
    
    def set_password(self, password):
        """Hash the password before storing it."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<AppUser {self.username}>"


class Project(db.Model):
    __tablename__ = 'project'  # Define the table name
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key linking project to a user
    user_id = db.Column(db.Integer, db.ForeignKey('appuser.id'), nullable=False)
    
    # Project details
    project_name = db.Column(db.String(150), nullable=False)  # Required project name
    description = db.Column(db.Text, nullable=True)  # Optional project description
    s3_folder = db.Column(db.String(300), nullable=False)  # Path to the S3 folder where files are stored
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))  # Project creation time
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))  # Last update time
    
    # Relationship to the user
    user = db.relationship('AppUser', backref=db.backref('projects', lazy=True))

    def __repr__(self):
        return f"<Project {self.project_name}>"


class SharedProject(db.Model):
    __tablename__ = 'shared_project'  # Define the table name
    
    id = db.Column(db.Integer, primary_key=True)

    # Foreign key linking shared project to a project
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

    # Sharing details
    share_link = db.Column(db.String(200), unique=True, nullable=False)  # Unique shareable link
    access_permissions = db.Column(db.String(50), nullable=False, default="read-only")  # E.g., 'read-only', 'read-write'

    # Timestamps
    shared_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))  # When the project was shared

    # Relationship to the project
    project = db.relationship('Project', backref=db.backref('shared_projects', lazy=True))

    def __repr__(self):
        return f"<SharedProject {self.share_link} - Permissions: {self.access_permissions}>"


class File3D(db.Model):
    __tablename__ = 'file3d'  # Define the table name
    
    id = db.Column(db.Integer, primary_key=True)

    # Foreign key linking file to a project
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

    # File details
    s3_file_url = db.Column(db.String(300), nullable=False)  # The S3 URL where the file is stored
    file_type = db.Column(db.String(10), nullable=False)  # E.g., '.obj', '.stl'
    
    # Timestamps
    uploaded_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))  # When the file was uploaded

    # Relationship to the project
    project = db.relationship('Project', backref=db.backref('files', lazy=True))

    def __repr__(self):
        return f"<File3D {self.s3_file_url} - Type: {self.file_type}>"


class ProjectSettings(db.Model):
    __tablename__ = 'project_settings'  # Define the table name
    
    id = db.Column(db.Integer, primary_key=True)

    # Foreign key linking settings to a project
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

    # Store the URL to the JSON settings file in S3
    s3_settings_url = db.Column(db.String(300), nullable=False)  # URL to the S3-stored JSON file
    
    # Timestamps
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to the project
    project = db.relationship('Project', backref=db.backref('project_settings', uselist=False, lazy=True))

    def __repr__(self):
        return f"<ProjectSettings S3 URL: {self.s3_settings_url}>"


# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(150), unique=False, nullable=True)  # Make username unique and required
#     email = db.Column(db.String(150), unique=True, nullable=False)
#     password_hash = db.Column(db.String(128), nullable=True)  # Nullable for OAuth users

#     def set_password(self, password):
#         """Hash the password before storing it."""
#         self.password_hash = generate_password_hash(password)

#     def check_password(self, password):
#         """Check hashed password."""
#         return check_password_hash(self.password_hash, password)

#     def __repr__(self):
#         return f"<User {self.username}>"
