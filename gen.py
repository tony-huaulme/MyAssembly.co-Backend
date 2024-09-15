# import os
# secret_key = os.urandom(24).hex()  # 24 bytes (192 bits) is a good size
# print(secret_key)

from models.models import db, AppUser, Project

# Create a new user
new_user = AppUser(username="testuser", email="testuser@example.com")
new_user.set_password("testpassword")  # Set password if required

# Add user to session and commit
db.session.add(new_user)
db.session.commit()

# Now you can use new_user.id as the user_id for your project
# Assuming new_user.id is the ID of the user we just created
new_project = Project(
    user_id=new_user.id,
    project_name="New Project",
    description="A new project description",
    s3_folder="path/to/s3/folder"
)

db.session.add(new_project)
db.session.commit()
