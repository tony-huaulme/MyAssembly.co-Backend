import os

# Try to import and load dotenv only if available
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
    print("Loaded .env file")
except ModuleNotFoundError:
    # If dotenv is not available, skip loading the .env file
    print("dotenv not found, skipping .env loading")

class Config:
    # Flask config
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #AWS S3 config
    AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')
    AWS_REGION = os.getenv('AWS_REGION')
    AWS_ACCESS = os.getenv('AWS_ACCESS')
    AWS_SECRET = os.getenv('AWS_SECRET')


    # OAuth config
    OAUTHLIB_RELAX_TOKEN_SCOPE = True
    OAUTHLIB_INSECURE_TRANSPORT = True  # Only for development, disable in production
    GOOGLE_OAUTH_CLIENT_ID = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
    GOOGLE_OAUTH_CLIENT_SECRET = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET')
    GOOGLE_OAUTH_REDIRECT_URI = os.getenv('GOOGLE_OAUTH_REDIRECT_URI')

    # CORS config
    ENV = os.getenv('ENV')