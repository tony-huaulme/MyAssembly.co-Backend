from config import Config
from models.models import db, AppUser, Project, SharedProject, File3D, ProjectSettings
from sqlalchemy import create_engine
from sqlalchemy.sql import text

# Get the database URL from the config
DATABASE_URL = Config.SQLALCHEMY_DATABASE_URI

# Create an engine using the database URL
engine = create_engine(DATABASE_URL)

# Manually truncate all tables
with engine.connect() as connection:
    connection.execute(text("TRUNCATE file3d, shared_project, project_settings, project, appuser RESTART IDENTITY CASCADE;"))

# Recreate all tables based on the new models (optional if they are still in place)
db.metadata.create_all(engine)

print("Database has been reset successfully.")
