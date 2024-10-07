from flask import request, send_file, jsonify
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from io import BytesIO
from config import Config

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

        try:
            # Generate a unique filename if necessary (e.g., use the original filename or generate one)
            filename = file.filename

            # Upload the file to the S3 bucket
            s3.upload_fileobj(file, Config.AWS_BUCKET_NAME, filename)

            # Construct the S3 URL for the uploaded file
            file_url = f"https://{Config.AWS_BUCKET_NAME}.s3.amazonaws.com/{filename}"

            # Return a success message with the file URL
            return jsonify({
                "message": "File uploaded successfully",
                "file_url": file_url
            }), 201

        except NoCredentialsError:
            return jsonify({"message": "Credentials not available"}), 403

        except ClientError as e:
            return jsonify({"message": str(e)}), 500