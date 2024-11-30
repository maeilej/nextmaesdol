import streamlit as st
import datetime as datetime
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from slack.send_message import send_slack_notification

from dynamodb.add_dummy_data import generate_dummy_logs
from dynamodb.add_dummy_data import insert_logs_to_dynamodb
from dynamodb.read_logs import fetch_logs_from_dynamodb
from dynamodb.read_logs import convert_logs_to_dataframe
from dynamodb.read_logs import fetch_all_logs_from_dynamodb
def generate_sample_logs():
    # 샘플 로그 데이터 생성
    dates = pd.date_range(start='2024-02-01', end='2024-02-08', freq='H')
    n_logs = len(dates)
    
    users = ['admin1', 'admin2', 'user1', 'user2', 'user3']
    actions = ['로그인', '데이터 조회', '설정 변경', '사용자 추가', '보고서 다운로드', '품질 검사']
    status = ['성공', '성공', '성공', '실패', '경고']
    ip_addresses = ['192.168.1.101', '192.168.1.102', '192.168.1.103', '192.168.1.104']
    
    logs = pd.DataFrame({
        'timestamp': dates,
        'user': np.random.choice(users, n_logs),
        'action': np.random.choice(actions, n_logs),
        'status': np.random.choice(status, n_logs, p=[0.8, 0.1, 0.05, 0.03, 0.02]),
        'ip_address': np.random.choice(ip_addresses, n_logs),
        'details': ['작업 세부 내용...'] * n_logs
    })
    
    return logs

def display_admin_page():
    # CSS 스타일
    st.markdown("""
    <style>
        .status-card {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            text-align: center;
            margin: 10px 0;
        }
        .log-card {
            background-color: white;
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }
        .metric-card {
            text-align: center;
            padding: 1rem;
            background: white;
            border-radius: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: #1976D2;
        }
        .metric-label {
            color: #666;
            font-size: 0.9rem;
        }
        .status-success {
            color: #4CAF50;
            font-weight: bold;
        }
        .status-warning {
            color: #FFA726;
            font-weight: bold;
        }
        .status-error {
            color: #EF5350;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("가드")
    st.markdown("""
    <div class="status-card">
        <h3>전체 로그에 대한 평가</h3>
    </div>
    """, unsafe_allow_html=True)

    # 1. 로그 필터링 섹션
    with st.expander("🔍 로그 필터 설정", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            date_range = st.date_input(
                "날짜 범위",
                value=(datetime.now() - timedelta(days=7), datetime.now()),
                max_value=datetime.now()
            )
        
        with col2:
            selected_users = st.multiselect(
                "사용자 선택",
                options=['전체', 'admin1', 'admin2', 'user1', 'user2', 'user3'],
                default=['전체']
            )
            # '전체' 선택 처리
            if '전체' in selected_users and len(selected_users) > 1:
                selected_users.remove('전체')
            elif not selected_users:
                selected_users = ['전체']
        
        with col3:
            selected_status = st.multiselect(
                "상태",
                options=['전체', '성공', '실패', '경고'],
                default=['전체']
            )
            # '전체' 선택 처리
            if '전체' in selected_status and len(selected_status) > 1:
                selected_status.remove('전체')
            elif not selected_status:
                selected_status = ['전체']
    
    # 2. 로그 데이터 가져오기
    logs = fetch_logs_from_dynamodb(date_range, selected_users, selected_status)
    log_data = convert_logs_to_dataframe(logs)
    
    # 수동 새로고침 버튼
    if st.button("🔄 새로고침"):
        logs = fetch_logs_from_dynamodb(date_range, "전체", "전체")
        log_data = convert_logs_to_dataframe(logs)
    
    # 3. 로그 테이블 표시
    if not log_data.empty:
        st.header("📋 상세 로그")
        
        # 로그 테이블 컨트롤
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search_term = st.text_input("🔍 로그 검색", placeholder="검색어를 입력하세요...")
        with col2:
            sort_by = st.selectbox("정렬 기준", ["최신순", "사용자명", "작업유형", "상태"])
        with col3:
            rows_per_page = st.selectbox("페이지당 행 수", [10, 20, 50, 100])
    
        # 검색 필터 적용
        if search_term:
            log_data = log_data[
                log_data['initiator'].str.contains(search_term, case=False) |
                log_data['action'].str.contains(search_term, case=False) |
                log_data['result_details'].str.contains(search_term, case=False)
            ]
        
        # 정렬 적용
        if sort_by == "최신순":
            log_data = log_data.sort_values('timestamp', ascending=False)
        elif sort_by == "사용자명":
            log_data = log_data.sort_values('initiator')
        elif sort_by == "작업유형":
            log_data = log_data.sort_values('action')
        elif sort_by == "상태":
            log_data = log_data.sort_values('status')
    
        # 페이지네이션 구현
        total_pages = max(1, len(log_data) // rows_per_page)
        page_number = st.number_input("페이지", min_value=1, max_value=total_pages, value=1)
        start_idx = (page_number - 1) * rows_per_page
        end_idx = min(start_idx + rows_per_page, len(log_data))
        
        # 슬라이싱된 데이터 표시
        page_data = log_data.iloc[start_idx:end_idx].copy()
        column_orders = ["timestamp", "log_id", "initiator", "action", "status", "result_details", "processing_time", "result_image_url"]
        st.dataframe(page_data, use_container_width=True, height=400, column_order=column_orders)
        
        # 페이지 정보 표시
        st.write(f"총 {len(log_data)}개 중 {start_idx + 1}-{end_idx}개 표시")
    
        # 4. CSV 다운로드 옵션
        st.download_button(
            label="📥 CSV로 내보내기",
            data=log_data.to_csv(index=False).encode('utf-8'),
            file_name=f"logs_{datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv'
        )
    else:
        st.info("조건에 맞는 로그가 없습니다.")


    # 6. 실시간 알림 설정
    st.header("⚙️ 알림 설정")
    with st.expander("알림 규칙 설정"):
        login_fail_alert = st.checkbox("로그인 실패 시 알림", value=True)
        permission_change_alert = st.checkbox("권한 변경 시 알림", value=True)
        settings_change_alert = st.checkbox("중요 설정 변경 시 알림", value=True)
    
    if st.button("테스트 알림 보내기"):
        if login_fail_alert:
            send_slack_notification(
                "🚨 로그인 실패 발생",
                "사용자: `user123`\n위치: `192.168.0.10`"
            )
        if permission_change_alert:
            send_slack_notification(
                "🛠️ 권한 변경 발생",
                "변경 사용자: `manager`\n대상 사용자: `worker01`\n변경된 권한: `Operator → Viewer`"
            )
        if settings_change_alert:
            send_slack_notification(
                "⚠️ 중요 설정 변경",
                "변경 사용자: `admin`\n변경된 설정: `알림 수신 이메일`\n이전 값: `example1@tofu.com`\n변경 값: `example2@tofu.com`"
            )
        st.success("테스트 알림 전송 완료!")
