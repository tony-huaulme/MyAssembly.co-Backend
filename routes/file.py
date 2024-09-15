from flask import request, send_file, jsonify
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from io import BytesIO
from config import Config

s3 = boto3.client(
    's3',
    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
)

def handle_file(filename):
    if request.method == 'GET':
        try:
            response = s3.get_object(Bucket=Config.AWS_BUCKET_NAME, Key=filename)
            file_stream = BytesIO(response['Body'].read())
            return send_file(file_stream, as_attachment=True, download_name=filename.split('/')[-1])
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return jsonify({'error': 'File not found'}), 404
            else:
                return jsonify({'error': str(e)}), 500
        except NoCredentialsError:
            return jsonify({'error': 'Credentials not available'}), 403

    elif request.method == 'POST':
        file = request.files.get('file')
        if file:
            try:
                s3.upload_fileobj(file, Config.AWS_BUCKET_NAME, filename)
                return jsonify({'message': 'File uploaded successfully'}), 201
            except NoCredentialsError:
                return jsonify({'error': 'Credentials not available'}), 403
            except ClientError as e:
                return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'No file provided'}), 400

    elif request.method == 'DELETE':
        try:
            s3.delete_object(Bucket=Config.AWS_BUCKET_NAME, Key=filename)
            return jsonify({'message': 'File deleted successfully'}), 200
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return jsonify({'error': 'File not found'}), 404
            else:
                return jsonify({'error': str(e)}), 500
        except NoCredentialsError:
            return jsonify({'error': 'Credentials not available'}), 403
