from flask import request, send_file, jsonify, redirect
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from config import Config
from botocore.config import Config as BotoConfig
from models.models import AppUser
from flask import session

s3 = boto3.client(
    's3',
    aws_access_key_id=Config.AWS_ACCESS,
    aws_secret_access_key=Config.AWS_SECRET,
    region_name="eu-west-3",  # Assuming Frankfurt (change this to your correct region)
    config=BotoConfig(s3={'addressing_style': 'virtual'})  # Enforce virtual-hosted style
)


def add_files_routes(app):
    @app.route('/files/upload', methods=['POST'])
    def upload_file_to_s3():
        # Get the file from the request
        file = request.files.get('file')

        if not file:
            return jsonify({"message": "No file provided"}), 400

        # Retrieve the user session and user information
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"message": "User not authenticated"}), 401
        
        user = AppUser.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        user_email = user.email  # Assuming the user model has an 'email' field
        
        try:
            # Generate a unique filename (can be original or a generated one)
            filename = file.filename

            # Create the folder path within the S3 bucket using the user's email
            s3_folder = f"{user_email}/"  # Folder structure with user's email
            s3_key = f"{s3_folder}{filename}"  # Full path with folder and filename

            # Upload the file to the S3 bucket in the specific folder
            s3.upload_fileobj(file, Config.AWS_BUCKET_NAME, s3_key)

            # Construct the S3 URL for the uploaded file
            file_url = f"https://{Config.AWS_BUCKET_NAME}.s3.amazonaws.com/{s3_key}"

            # Return a success message with the file URL
            return jsonify({
                "message": "File uploaded successfully",
                "file_url": file_url
            }), 201

        except NoCredentialsError:
            return jsonify({"message": "Credentials not available"}), 403

        except ClientError as e:
            return jsonify({"message": str(e)}), 500

    @app.route('/files/download', methods=['GET'])
    def download_file_from_s3():
        # Get the file key from the query parameters
        file_key = request.args.get('file_key')

        if not file_key:
            return jsonify({"message": "No file key provided"}), 400

        try:
            # Generate a temporary URL for the file
            url = s3.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': Config.AWS_BUCKET_NAME,  # Just the bucket name here
                        'Key': file_key  # The file key (with any folder structure)
                    },
                    ExpiresIn=3600  # URL expires in 1 hour
                )

            print("GENERATED URL :",url)
            print("USED KEY :",file_key)
            # Redirect the user to the temporary URL for download
            return jsonify({"presigned_url": url}), 200
            # return redirect(url)

        except NoCredentialsError:
            return jsonify({"message": "Credentials not available"}), 403

        except ClientError as e:
            return jsonify({"message": str(e)}), 500