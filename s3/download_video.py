import boto3
import streamlit as st
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
BUCKET_NAME = os.getenv("region_name")

# Function to download video from S3
def download_from_s3(bucket_name, object_name, local_file_name):
    try:
        s3_client.download_file(bucket_name, object_name, local_file_name)
        return local_file_name
    except Exception as e:
        print(f"Error downloading file: {e}")
        return None