import boto3
from datetime import datetime
import pytz
import uuid
import os
import re
import time
from dynamodb.add_dummy_data import insert_logs_to_dynamodb
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

# SageMaker 및 S3 클라이언트 생성
sagemaker_client = boto3.client('runtime.sagemaker')
s3_client = boto3.client('s3')

# DynamoDB 테이블 이름
TABLE_NAME = os.getenv("TABLE_NAME")
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

# S3 버킷 이름
S3_BUCKET_NAME = os.getenv("BUCKET_NAME")

def natural_sort_key(s):
    """Sort files naturally by extracting numbers."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

# 엔드포인트 호출 및 DynamoDB 로그 저장
def process_frames_with_endpoint(frames_directory):
    # SageMaker 엔드포인트 이름
    endpoint_name = os.getenv("endpoint_name")

    # 프레임 파일 읽기
    image_files = sorted(
        [os.path.join(frames_directory, f) for f in os.listdir(frames_directory) if f.lower().endswith(('.png', '.jpg', '.jpeg'))],
        key=natural_sort_key  # Sort using natural sorting
    )

    # 결과값을 저장할 리스트
    results_summary = []

    for frame_path in image_files:
        with open(frame_path, 'rb') as image_file:
            # 프레임 데이터를 바이트로 읽기
            image_bytes = image_file.read()

        # SageMaker 호출 시작 시간 측정
        start_time = time.time()

        try:
            # SageMaker 엔드포인트 호출
            response = sagemaker_client.invoke_endpoint(
                EndpointName=endpoint_name,
                ContentType='application/x-image',
                Body=image_bytes
            )

            # 응답 파싱
            result = response['Body'].read().decode('utf-8')  # JSON 형식 결과 가정
            result_details = result  # 전체 결과 저장 (구체적인 파싱은 필요에 따라 추가)
            status = "성공"

        except Exception as e:
            print(f"Error processing frame {frame_path}: {e}")
            result_details = str(e)
            status = "실패"

        # SageMaker 응답 시간 측정
        processing_time = time.time() - start_time  # 초 단위로 응답 시간 측정

        # 이미지 S3에 업로드 후 URL 생성
        result_image_url = None
        try:
            # S3에 업로드할 파일 이름 생성
            s3_key = f"processed_images/{uuid.uuid4()}.jpg"
            
            # S3에 이미지 업로드
            with open(frame_path, 'rb') as image_file:
                s3_client.upload_fileobj(image_file, S3_BUCKET_NAME, s3_key)
            
            # S3 URL 생성
            result_image_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{s3_key}"

        except Exception as e:
            print(f"Error uploading image to S3: {e}")

        # 로그 데이터 생성
        timestamp = datetime.now(pytz.utc).isoformat()
        log_id = f"log_{uuid.uuid4()}"
        initiator = "user1"  # 임시 값. 로그인 기능 추가 시 현재 로그인 사용자로 대체
        action = "프레임 분석"

        # 로그 저장
        log_entry = {
            'timestamp': timestamp,
            'log_id': log_id,
            'action': action,
            'status': status,
            'result_details': result_details,
            'result_image_url': result_image_url,
            'initiator': initiator,
            'processing_time': processing_time
        }

        # DynamoDB에 로그 저장
        try:
            table.put_item(Item=log_entry)
            print(f"Log saved for frame {frame_path}: {log_entry}")
        except Exception as db_error:
            print(f"Error saving log to DynamoDB: {db_error}")

        # 결과 요약 저장
        results_summary.append({
            'frame_path': frame_path,
            'status': status,
            'result_details': result_details,
            'result_image_url': result_image_url,
            'processing_time': processing_time
        })

    # 모든 결과를 리스트로 반환
    return results_summary
