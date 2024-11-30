import boto3
import pandas as pd
import pytz
from datetime import datetime, timedelta
import boto3
import streamlit as st
from boto3.dynamodb.conditions import Key, Attr
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# DynamoDB 테이블 이름
TABLE_NAME = os.getenv("TABLE_NAME")
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

# DynamoDB에서 최신 로그 가져오기
def fetch_all_logs_from_dynamodb(
):
    # 기본 키와 정렬 키 사용 여부 확인
    table = dynamodb.Table(TABLE_NAME)

    # 스캔 대신 최신 데이터를 쿼리 방식으로 가져오기
    try:
        response = table.scan(Limit=100)

        logs = response.get('Items', [])

        # `LastEvaluatedKey`가 있을 경우 추가 페이지 처리
        while 'LastEvaluatedKey' in response:
            response = table.scan(
                ExclusiveStartKey=response['LastEvaluatedKey'],
            )
            logs.extend(response.get('Items', []))

        return logs

    except Exception as e:
        st.error(f"DynamoDB 데이터를 가져오는 중 오류 발생: {e}")
        return []


# DynamoDB에서 로그 가져오기
def fetch_logs_from_dynamodb(
    date_range=None,  # 날짜 범위 (start_date, end_date) 형태의 튜플
    selected_users=None,  # 선택된 사용자 리스트
    selected_status=None  # 선택된 상태 리스트
):
    # DynamoDB 클라이언트 초기화
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE_NAME)
    
    # 기본 스캔 조건
    filter_expression = None

    # 날짜 필터 추가
    if date_range and date_range[0] != '전체' and date_range[1] != '전체':
        try:
            # date_range 값이 문자열인 경우 datetime 객체로 변환
            if isinstance(date_range[0], str):
                start_date = datetime.strptime(date_range[0], '%Y-%m-%d')
            else:
                start_date = date_range[0]

            if isinstance(date_range[1], str):
                end_date = datetime.strptime(date_range[1], '%Y-%m-%d')
            else:
                end_date = date_range[1]

            # 날짜를 ISO 8601 형식으로 변환
            start_date_iso = start_date.strftime('%Y-%m-%dT00:00:00Z')
            end_date_iso = end_date.strftime('%Y-%m-%dT23:59:59Z')

            date_filter = Key('timestamp').between(start_date_iso, end_date_iso)
            filter_expression = date_filter

        except ValueError:
            # 날짜 파싱 실패 시, 기본적으로 필터링을 추가하지 않음
            pass

    # 사용자 필터 추가
    if selected_users and '전체' not in selected_users:
        user_filter = Attr('initiator').is_in(selected_users)
        filter_expression = user_filter if not filter_expression else filter_expression & user_filter

    # 상태 필터 추가
    if selected_status and '전체' not in selected_status:
        status_filter = Attr('status').is_in(selected_status)
        filter_expression = status_filter if not filter_expression else filter_expression & status_filter

    # DynamoDB 스캔
    if filter_expression:
        response = table.scan(FilterExpression=filter_expression, Limit=100)
    else:
        response = table.scan(Limit=100)

    # 반환된 데이터 정리
    logs = response.get('Items', [])

    # 전체 스캔 결과 페이지 처리
    while 'LastEvaluatedKey' in response:
        if filter_expression:
            response = table.scan(
                ExclusiveStartKey=response['LastEvaluatedKey'],
                FilterExpression=filter_expression
            )
        else:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        logs.extend(response.get('Items', []))

    return logs

# 데이터프레임으로 변환
def convert_logs_to_dataframe(logs):
    if not logs:
        return pd.DataFrame(columns=["timestamp", "log_id", "action", "status", "result_details", "result_image_url", "initiator", "processing_time"])

    df = pd.DataFrame(logs)
    # timestamp 기준으로 정렬
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')  # datetime 형식 변환
    df = df.sort_values(by='timestamp', ascending=True).reset_index(drop=True)
    return df
    
# 주간 및 월간 로그 필터링
def filter_logs_by_date_range(log_data):
    if log_data.empty:
        return pd.DataFrame(), pd.DataFrame()

    # 현재 날짜를 UTC로 설정
    now = datetime.now(pytz.utc)

    # 주간 및 월간 범위 계산
    weekly_start = now - timedelta(days=7)
    monthly_start = now - timedelta(days=30)

    # 데이터의 timestamp를 UTC로 변환
    log_data['timestamp'] = pd.to_datetime(log_data['timestamp']).dt.tz_convert(pytz.utc)

    # 주간 및 월간 데이터 필터링
    weekly_logs = log_data[log_data['timestamp'] >= weekly_start]
    monthly_logs = log_data[log_data['timestamp'] >= monthly_start]

    return weekly_logs, monthly_logs