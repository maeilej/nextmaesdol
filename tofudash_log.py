import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(
    page_title="관리자 로그 대시보드",
    page_icon="📊",
    layout="wide"
)

# CSS 스타일
st.markdown("""
<style>
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

def main():
    st.title("관리자 로그 관리 시스템")
    
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
                ['전체', 'admin1', 'admin2', 'user1', 'user2', 'user3'],
                default=['전체']
            )
        
        with col3:
            selected_status = st.multiselect(
                "상태",
                ['전체', '성공', '실패', '경고'],
                default=['전체']
            )
    
    # 2. 로그 통계 요약
    st.header("📊 로그 통계 요약")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">1,234</div>
            <div class="metric-label">전체 로그 수</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">95.5%</div>
            <div class="metric-label">성공률</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">42</div>
            <div class="metric-label">금일 활성 사용자</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">12</div>
            <div class="metric-label">경고 발생 수</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 3. 로그 시각화
    st.header("📈 로그 분석")
    
    tab1, tab2 = st.tabs(["시간별 분석", "사용자별 분석"])
    
    with tab1:
        # 시간별 로그 발생 추이
        logs_df = generate_sample_logs()
        hourly_logs = logs_df.groupby([pd.Grouper(key='timestamp', freq='D'), 'status']).size().unstack()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hourly_logs.index,
            y=hourly_logs['성공'],
            name='성공',
            line=dict(color='#4CAF50')
        ))
        fig.add_trace(go.Scatter(
            x=hourly_logs.index,
            y=hourly_logs['실패'],
            name='실패',
            line=dict(color='#EF5350')
        ))
        
        fig.update_layout(
            title='시간별 로그 발생 추이',
            xaxis_title='시간',
            yaxis_title='로그 수',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # 사용자별 작업 분포
        user_actions = logs_df.groupby(['user', 'action']).size().unstack()
        
        fig = px.bar(
            user_actions,
            barmode='group',
            title='사용자별 작업 분포',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # 4. 상세 로그 테이블 부분 수정
    st.header("📋 상세 로그")
    
    # 로그 테이블 컨트롤
    col1, col2, col3 = st.columns([2,1,1])
    with col1:
        search_term = st.text_input("🔍 로그 검색", placeholder="검색어를 입력하세요...")
    with col2:
        sort_by = st.selectbox("정렬 기준", ["최신순", "사용자명", "작업유형", "상태"])
    with col3:
        rows_per_page = st.selectbox("페이지당 행 수", [10, 20, 50, 100])
    
    # 로그 테이블 표시
    log_data = generate_sample_logs()
    
    # 검색 필터 적용
    if search_term:
        log_data = log_data[
            log_data['user'].str.contains(search_term, case=False) |
            log_data['action'].str.contains(search_term, case=False) |
            log_data['details'].str.contains(search_term, case=False)
        ]
    
    # 정렬 적용
    if sort_by == "최신순":
        log_data = log_data.sort_values('timestamp', ascending=False)
    elif sort_by == "사용자명":
        log_data = log_data.sort_values('user')
    elif sort_by == "작업유형":
        log_data = log_data.sort_values('action')
    elif sort_by == "상태":
        log_data = log_data.sort_values('status')
    
    # 페이지네이션 구현
    total_pages = max(1, len(log_data) // rows_per_page)
    page_number = st.number_input("페이지", min_value=1, max_value=total_pages, value=1)
    start_idx = (page_number-1) * rows_per_page
    end_idx = min(start_idx + rows_per_page, len(log_data))
    
    # 먼저 데이터를 슬라이싱
    page_data = log_data.iloc[start_idx:end_idx].copy()
    
    # 스타일 함수 정의
    def color_status(val):
        if val == '성공':
            return 'color: #4CAF50'
        elif val == '실패':
            return 'color: #EF5350'
        elif val == '경고':
            return 'color: #FFA726'
        return ''
    
    # 슬라이싱된 데이터에 스타일 적용
    styled_logs = page_data.style.applymap(color_status, subset=['status'])
    
    # 스타일이 적용된 데이터프레임 표시
    st.dataframe(
        styled_logs,
        use_container_width=True,
        height=400
    )
    
    # 페이지 정보 표시
    st.write(f"총 {len(log_data)}개 중 {start_idx + 1}-{end_idx}개 표시")
    
    # 5. 로그 내보내기 옵션
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 CSV로 내보내기",
            data=log_data.to_csv(index=False).encode('utf-8'),
            file_name=f"admin_logs_{datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv'
        )
    with col2:
        if st.button("🗑 오래된 로그 삭제"):
            st.warning("30일 이상 된 로그를 삭제하시겠습니까?")
            if st.button("확인"):
                st.success("로그가 삭제되었습니다.")

    # 6. 실시간 알림 설정
    st.header("⚙️ 알림 설정")
    with st.expander("알림 규칙 설정"):
        st.checkbox("로그인 실패 시 알림", value=True)
        st.checkbox("권한 변경 시 알림", value=True)
        st.checkbox("중요 설정 변경 시 알림", value=True)
        st.text_input("알림 수신 이메일", placeholder="email@example.com")
        st.selectbox("알림 수신 방법", ["이메일", "슬랙", "모두"])

if __name__ == "__main__":
    main()