import boto3
from datetime import datetime, timedelta
import streamlit as st
import random
import uuid
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# DynamoDB 테이블 이름
TABLE_NAME = os.getenv("TABLE_NAME")

# DynamoDB 리소스 생성
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

# 더미 데이터 생성 함수
def generate_dummy_logs(num_logs=100):
    status_options = ["성공", "실패", "진행 중"]
    action_options = ["데이터 조회", "보고서 다운로드", "검수", "설정 변경", "권한 변경"]
    initiator_options = ["admin1", "admin2", "user1", "user2", "user3"]
    result_details_options = [
        "결함 없음 (정확도: 99.7%)",
        "미세 결함 발견 (정확도: 95.4%)",
        "결함 발생 (정확도: 92.1%)"
    ]

    logs = []
    for i in range(num_logs):
        timestamp = (datetime.now() - timedelta(minutes=i)).strftime('%Y-%m-%dT%H:%M:%SZ')  # ISO 8601 형식
        log_id = str(uuid.uuid4())
        action = random.choice(action_options)
        status = random.choice(status_options)
        if(action == "검수"):
            result_details = random.choice(result_details_options)
        else:
            result_details = ""
        result_image_url = f"S3://nxtm/log/image-{i}.jpg"
        initiator = random.choice(initiator_options)
        processing_time = random.randint(100, 500)  # 처리 시간 (ms)

        logs.append({
            'timestamp': timestamp,
            'log_id': log_id,
            'action': action,
            'status': status,
            'result_details': result_details,
            'result_image_url': result_image_url,
            'initiator': initiator,
            'processing_time': processing_time
        })
    return logs

# 데이터 DynamoDB에 삽입
def insert_logs_to_dynamodb(logs):
    for log in logs:
        table.put_item(Item=log)
        print(f"Inserted log: {log}")
        # st.write(f"Inserted log: {log}")
