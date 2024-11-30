import streamlit as st
import boto3
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

from dynamodb.add_dummy_data import generate_dummy_logs
from dynamodb.add_dummy_data import insert_logs_to_dynamodb
from dynamodb.read_logs import fetch_logs_from_dynamodb
from dynamodb.read_logs import convert_logs_to_dataframe
from dynamodb.read_logs import filter_logs_by_date_range

def display_dashboard_page():
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
        .status-normal {
            background-color: #4CAF50;
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-weight: bold;
        }
        .status-warning {
            background-color: #FFA726;
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-weight: bold;
        }
        .status-danger {
            background-color: #EF5350;
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-weight: bold;
        }
        .big-number {
            font-size: 36px;
            font-weight: bold;
            margin: 10px 0;
        }
        .header-style {
            font-size: 24px;
            font-weight: bold;
            margin: 20px 0;
            color: #1976D2;
        }
    </style>
    """, unsafe_allow_html=True)


    st.title("📊 두부 품질 모니터링 시스템")

    col1, col2, col3 = st.columns(3)
        
    with col1:
        quality_score = 95  # 예시 값
        status = ("status-normal" if quality_score >= 90 
                else "status-warning" if quality_score >= 80 
                else "status-danger")
            
        st.markdown(f"""
        <div class="status-card">
            <h3>품질 점수</h3>
            <div class="big-number" style="color: #1976D2">{quality_score}점</div>
            <div class="{status}">
                {("정상" if quality_score >= 90 
                else "주의" if quality_score >= 80 
                else "위험")}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
            st.markdown(f"""
            <div class="status-card">
                <h3>오늘의 생산량</h3>
                <div class="big-number" style="color: #1976D2">2,450개</div>
                <div class="status-normal">목표달성 95%</div>
            </div>
            """, unsafe_allow_html=True)
        
    with col3:
            defect_rate = 0.8  # 예시 값
            status = ("status-normal" if defect_rate < 1 
                    else "status-warning" if defect_rate < 2 
                    else "status-danger")
            
            st.markdown(f"""
            <div class="status-card">
                <h3>불량률</h3>
                <div class="big-number" style="color: #1976D2">{defect_rate}%</div>
                <div class="{status}">
                    {("정상" if defect_rate < 1 
                    else "주의" if defect_rate < 2 
                    else "위험")}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        
    # 3. 불량 유형 분석
    st.markdown('<p class="header-style">🔍 불량 유형 분석</p>', unsafe_allow_html=True)
        
    col1, col2 = st.columns(2)
        
    with col1:
       # 데이터
        labels = ['모양 불량', '크기 이상', '색상 불량', '기타']
        values = [45, 30, 15, 10]
        
        # 수평 막대그래프 생성
        fig = go.Figure(data=[go.Bar(
            x=values,
            y=labels,
            orientation='h',  # 막대 방향: 수평
            marker=dict(
                color=['#1976D2', '#64B5F6', '#90CAF9', '#BBDEFB']  # 막대 색상
            )
        )])
        
        # 레이아웃 설정
        fig.update_layout(
            title='불량 유형 비율',
            xaxis_title='비율 (%)',
            yaxis_title='불량 유형',
            height=400,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        # 그래프 출력
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        # 샘플 데이터 생성
        hours = list(range(9, 18))  # 9시부터 17시까지
        quality_scores = [95, 94, 93, 92, 91, 90, 92, 93, 94]
            
        fig = go.Figure()
            
        # 품질 점수 라인
        fig.add_trace(go.Scatter(
            x=hours,
            y=quality_scores,
            mode='lines+markers',
            name='품질 점수',
            line=dict(color='#1976D2', width=3),
            marker=dict(size=10)
        ))
            
            # 기준선 추가
        fig.add_hline(y=90, line_dash="dash", line_color="green",
                    annotation_text="정상 기준")
        fig.add_hline(y=80, line_dash="dash", line_color="red",
                    annotation_text="위험 기준")
            
        fig.update_layout(
                title='품질 예측',
                xaxis_title='시간',
                yaxis_title='품질 점수',
                yaxis_range=[75, 100],
                height=400,
                showlegend=False
        )
            
        st.plotly_chart(fig, use_container_width=True)
        
    # 4. 품질 예측 알림
    st.markdown('<p class="header-style">⚠️ 품질 예측 알림</p>', unsafe_allow_html=True)
        
    # 현재 상태에 따른 알림 메시지
    if quality_score >= 90:
        st.success("✅ 현재 모든 품질 지표가 정상 범위 내에 있습니다!")
    elif quality_score >= 80:
            st.warning("""
            ⚠️ 주의가 필요한 항목이 있습니다:
            - 모양 품질 지수가 기준보다 조금 낮습니다
            - 크기 편차가 증가하는 추세입니다
            """)
    else:
            st.error("""
            🚨 긴급 확인이 필요합니다:
            - 품질 점수가 위험 수준입니다
            - 즉시 생산 라인 점검이 필요합니다
            """)
    date_range = "전체"
    selected_users = "전체"
    selected_status = "전체"
    

    # 2. 로그 데이터 가져오기
    logs = fetch_logs_from_dynamodb(date_range, selected_users, selected_status)
    log_data = convert_logs_to_dataframe(logs)
    
    # 수동 새로고침 버튼
    if st.button("🔄 새로고침"):
        logs = fetch_logs_from_dynamodb(date_range, "전체", "전체")
        log_data = convert_logs_to_dataframe(logs)
        
            
    if not log_data.empty:
        # 주간 및 월간 로그 필터링
        weekly_logs, monthly_logs = filter_logs_by_date_range(log_data)
    
        # 주간 로그 섹션
        st.subheader("📅 주간 로그")
        if not weekly_logs.empty:
            column_orders = ["timestamp", "log_id", "initiator", "action", "status", "result_details", "processing_time", "result_image_url"]
            st.dataframe(weekly_logs, use_container_width=True, height=300, column_order=column_orders)
            st.write(f"총 {len(weekly_logs)}개의 로그를 표시 중입니다.")
        else:
            st.info("주간 로그가 없습니다.")
    
        # 월간 로그 섹션
        st.subheader("🗓️ 월간 로그")
        if not monthly_logs.empty:
            column_orders = ["timestamp", "log_id", "initiator", "action", "status", "result_details", "processing_time", "result_image_url"]
            st.dataframe(monthly_logs, use_container_width=True, height=300, column_order=column_orders)
            st.write(f"총 {len(monthly_logs)}개의 로그를 표시 중입니다.")
        else:
            st.info("월간 로그가 없습니다.")
        
    # 5. 간단한 제어 패널
    with st.sidebar:
            st.header("⚙️ 모니터링 설정")
            st.multiselect(
                "모니터링 항목",
                ["모양", "크기", "색상", "밀도"],
                ["모양", "크기", "색상"]
            )
            
            st.divider()
            st.caption(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    
    
            