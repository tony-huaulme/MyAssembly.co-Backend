from flask import request, send_file, jsonify
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from config import Config
from models.models import AppUser
from flask import session

s3 = boto3.client(
    's3',
    aws_access_key_id=Config.AWS_ACCESS,
    aws_secret_access_key=Config.AWS_SECRET
)

# def handle_file(filename):
#     if request.method == 'GET':
#         try:
#             response = s3.get_object(Bucket=Config.AWS_BUCKET_NAME, Key=filename)
#             file_stream = BytesIO(response['Body'].read())
#             return send_file(file_stream, as_attachment=True, download_name=filename.split('/')[-1])
#         except ClientError as e:
#             if e.response['Error']['Code'] == 'NoSuchKey':
#                 return jsonify({'error': 'File not found'}), 404
#             else:
#                 return jsonify({'error': str(e)}), 500
#         except NoCredentialsError:
#             return jsonify({'error': 'Credentials not available'}), 403

#     elif request.method == 'POST':
#         file = request.files.get('file')
#         if file:
#             try:
#                 s3.upload_fileobj(file, Config.AWS_BUCKET_NAME, filename)
#                 return jsonify({'message': 'File uploaded successfully'}), 201
#             except NoCredentialsError:
#                 return jsonify({'error': 'Credentials not available'}), 403
#             except ClientError as e:
#                 return jsonify({'error': str(e)}), 500
#         else:
#             return jsonify({'error': 'No file provided'}), 400

#     elif request.method == 'DELETE':
#         try:
#             s3.delete_object(Bucket=Config.AWS_BUCKET_NAME, Key=filename)
#             return jsonify({'message': 'File deleted successfully'}), 200
#         except ClientError as e:
#             if e.response['Error']['Code'] == 'NoSuchKey':
#                 return jsonify({'error': 'File not found'}), 404
#             else:
#                 return jsonify({'error': str(e)}), 500
#         except NoCredentialsError:
#             return jsonify({'error': 'Credentials not available'}), 403


# from flask import request, jsonify
# import boto3
# from botocore.exceptions import ClientError, NoCredentialsError
# from config import Config
# import os

# s3 = boto3.client(
#     's3',
#     aws_access_key_id=Config.AWS_ACCESS,
#     aws_secret_access_key=Config.AWS_SECRET
# )
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
       