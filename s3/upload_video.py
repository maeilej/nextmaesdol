import boto3
import streamlit as st
import os
from botocore.exceptions import NoCredentialsError
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Set up AWS S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv("aws_access_key_id"),
    aws_secret_access_key=os.getenv("aws_secret_access_key"),
    region_name=os.getenv("region_name")
)

# Replace with your actual bucket name
BUCKET_NAME = os.getenv("BUCKET_NAME")

# Function to upload video to S3
def upload_to_s3(file, bucket_name, object_name):
    try:
        s3_client.upload_fileobj(file, bucket_name, object_name)
        print(f"File uploaded successfully to S3: {object_name}")
        return f"https://{bucket_name}.s3.amazonaws.com/videos/{object_name}"
    except FileNotFoundError:
        print("The file was not found.")
        return None
    except NoCredentialsError:
        print("Credentials not available.")
        return None
