from flask import request, send_file, jsonify, redirect
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from config import Config
from botocore.config import Config as BotoConfig
from models.models import AppUser
from flask import session
from datetime import datetime
from utils import sendLog

#conversion imports
import os
import subprocess
import ifcopenshell
from werkzeug.utils import secure_filename
from collections import defaultdict
from time import time

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
            sendLog("error", {"logId" : 0, "LogMessage" : "Credentials not available"})
            return jsonify({"message": "Credentials not available"}), 403

        except ClientError as e:
            sendLog("error", {"logId" : 1, "LogMessage" : str(e)})
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

            # print("GENERATED URL :",url)
            # print("USED KEY :",file_key)

            url_to_send = url if Config.ENV == "production" else "https://www.myassembly.co/src/assets/models/DemoModel.glb"

            # Redirect the user to the temporary URL for download
            return jsonify({"presigned_url": url_to_send}), 200
            # return redirect(url)

        except NoCredentialsError:
            sendLog("error", {"logId" : 3, "LogMessage" : "Credentials not available"})
            return jsonify({"message": "Credentials not available"}), 403

        except ClientError as e:
            sendLog("error", {"logId" : 4, "LogMessage" : str(e)})
            return jsonify({"message": str(e)}), 500
        
    # delete file from s3
    @app.route('/files/delete', methods=['DELETE'])
    def delete_file_from_s3():
        # Get the file key from the query parameters
        file_key = request.args.get('file_key')

        # file key is user_email/filename
        # check if user own the file
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"message": "User ID is required"}), 400
        
        user = AppUser.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        user_email = user.email  # Assuming the user model has an 'email' field
        s3_folder = f"{user_email}/"
        if not file_key.startswith(s3_folder):
            return jsonify({"message": "User does not own this file"}), 403
        
        

        if not file_key:
            return jsonify({"message": "No file key provided"}), 400

        try:
            # Delete the file from the S3 bucket
            s3.delete_object(Bucket=Config.AWS_BUCKET_NAME, Key=file_key)

            return jsonify({"message": "File deleted successfully"}), 200

        except NoCredentialsError:
            sendLog("error", {"logId" : 5, "LogMessage" : "Credentials not available"})
            return jsonify({"message": "Credentials not available"}), 403

        except ClientError as e:
            sendLog("error", {"logId" : 6, "LogMessage" : str(e)})
            return jsonify({"message": str(e)}), 500

    @app.route('/files/convert_getsettings_upload', methods=['POST'])
    def upload_and_convert_file_to_s3():
        file = request.files.get('file')
        start_time = time()

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

        if not file.filename.lower().endswith('.ifc'):
            print("File type validation failed: Only IFC files are allowed.")
            return jsonify({"message": "Only IFC files are allowed"}), 400

        try:

            # Save the uploaded file on amazon s3, in the directory IFCs
            filename = secure_filename(file.filename)


            # print("Constructing input path.")
            input_path = f'./{filename}'#os.path.join(app.config['UPLOAD_FOLDER'], filename)
            # print(f"Input path constructed: {input_path}")

            # print("Saving file locally.")
            file.save(input_path)


            with open(input_path, 'rb') as ifc_file:
                # make sure the file name is unique adding timestampnumbers
                try:
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    unique_filename = f"{user_email}_{filename}_{timestamp}"
                    s3_folder = "IFCs/"
                    s3_key = f"{s3_folder}{unique_filename}"
                    s3.upload_fileobj(ifc_file, Config.AWS_BUCKET_NAME, s3_key)

                    sendLog("success", {"logId" : 14, "LogMessage" : "IFC file uploaded successfully", "file_key" : s3_key, user_email : user_email})

                except Exception as e:
                    sendLog("error", {"logId" : 15, "LogMessage" : str(e)})
                    return jsonify({"message": str(e)}), 500


            output_filename = f"{os.path.splitext(filename)[0]}.glb"
            output_path = f'./{output_filename}'#os.path.join(app.config['CONVERTED_FOLDER'], output_filename)

            # Dynamically locate IfcConvert in the current directory or subdirectories
            current_dir = os.getcwd()  # Get the current working directory
            ifcconvert_path = os.path.join(current_dir, 'IfcConvert')

            args = ["--use-element-guids"]
            sendLog("info", {"logId" : 7, "LogMessage" : "Conversion started"})
            # Use the resolved path in the subprocess call
            subprocess.run(
                [
                    ifcconvert_path,  # Use the full resolved path
                    input_path,
                    output_path,
                    *args,
                ],
                capture_output=True, text=True, check=True, timeout=1200
            )

            end_t = time()
            time_s = round(end_t - start_time, 2)
            # print("Conversion completed successfully.")
            sendLog("success", {"logId" : 16, "LogMessage" : "Conversion completed successfully", "file_key" : s3_key, "time_spent" : time_s})
            # Extract GUIDs and Descriptions
            # print("Opening IFC file for extraction.")
            ifc_file = ifcopenshell.open(input_path)
            # print("IFC file opened.")

            description_dict = defaultdict(list)
            # print("Extracting elements.")
            for element in ifc_file.by_type('IfcElement'):
                # print(f"Processing element: {element}")
                guid = element.GlobalId
                description = getattr(element, 'Description', None)
                if description:
                    # print(f"Adding GUID {guid} to description '{description}'.")
                    description_dict[description].append(guid)

            # Upload the GLB file to S3
            # print("Uploading GLB file to S3.")
            with open(output_path, 'rb') as glb_file:
                s3_folder = f"{user_email}/"  # Folder structure with user's email
                # print(f"S3 folder: {s3_folder}")
                s3_key = f"{s3_folder}{output_filename}"
                # print(f"S3 key: {s3_key}")
                s3.upload_fileobj(glb_file, Config.AWS_BUCKET_NAME, s3_key)
                # print(f"File uploaded to S3 with key: {s3_key}")

            # Construct the S3 URL for the uploaded GLB file
            # print("Constructing S3 URL.")
            file_url = f"https://{Config.AWS_BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
            # print(f"S3 URL: {file_url}")

            # Clean up local files (optional)
            # print("Removing local files.")
            os.remove(input_path)
            # print(f"Removed file: {input_path}")
            os.remove(output_path)
            # print(f"Removed file: {output_path}")

            # Return a success message with the file URL and extracted data
            # print("Returning success response.")

            # Your existing code here

            end_time = time()
            time_spent = round(end_time - start_time, 2)

            return jsonify({
                "message": "File converted, uploaded, and data extracted successfully",
                "file_url": file_url,
                "model_structure": description_dict,
                "time_spent": time_spent
            }), 201

        except subprocess.CalledProcessError as e:
            error_message = e.stderr or e.stdout or "No error output captured"
            sendLog("error", {"logId": 8, "LogMessage": error_message})
            return jsonify({"message": "Conversion failed", "details": error_message}), 500


        except NoCredentialsError:
            sendLog("error", {"logId" : 9, "LogMessage" : "Credentials not available"})
            return jsonify({"message": "Credentials not available"}), 403

        except ClientError as e:
            sendLog("error", {"logId" : 10, "LogMessage" : str(e)})
            return jsonify({"message": str(e)}), 500

        except Exception as e:
            sendLog("error", {"logId" : 11, "LogMessage" : str(e)})
            return jsonify({"message": f"Unexpected error: {str(e)}"}), 500

