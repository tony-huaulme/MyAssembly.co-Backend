from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)

# Define your models here as needed

# Import your models
from models.models import AppUser, Project, SharedProject, File3D



def create_all():
    with app.app_context():
        db.create_all()
        print("All tables have been created.")

if __name__ == "__main__":
    create_all()