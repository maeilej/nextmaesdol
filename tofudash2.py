import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(
    page_title="두부 품질 모니터링",
    page_icon="🧊",
    layout="wide"
)

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

def main():
    st.title("📊 두부 품질 모니터링 시스템")
    
    # 5. 간단한 제어 패널
    with st.sidebar:
        st.header("⚙️ 모니터링 설정")
        st.toggle("자동 새로고침", value=True)
        st.slider("새로고침 주기(초)", 5, 60, 30)
        selected_items = st.multiselect(
            "모니터링 항목",
            ["모서리", "패임", "기포", "이물"],  # 순서 변경
            ["모서리", "패임", "기포", "이물"]   # 순서 변경
        )
        
        st.divider()
        st.caption(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 현재 상태 개요
    st.markdown('<p class="header-style">현재 생산 상태</p>', unsafe_allow_html=True)
    
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
    
    # 2. 시간별 품질 추이
    st.markdown('<p class="header-style">📈 시간별 품질 추이</p>', unsafe_allow_html=True)
    
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
        title='시간별 품질 점수',
        xaxis_title='시간',
        yaxis_title='품질 점수',
        yaxis_range=[75, 100],
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 3. 불량 유형 분석
    st.markdown('<p class="header-style">🔍 불량 유형 분석</p>', unsafe_allow_html=True)
    
    # 파이 차트 데이터 업데이트 - 순서와 값을 이미지와 동일하게 수정
    defect_data = {
        "모서리": 0.45,  # 45%
        "패임": 0.30,    # 30%
        "기포": 0.15,    # 15%
        "이물": 0.10     # 10%
    }
    
    # 모든 데이터를 파이 차트에 표시
    values = list(defect_data.values())
    
    fig = go.Figure(data=[go.Pie(
        labels=list(defect_data.keys()),
        values=values,
        hole=.3,
        marker_colors=['#1976D2', '#64B5F6', '#90CAF9', '#BBDEFB'],
        textfont_size=14,
        marker=dict(line=dict(color='#FFFFFF', width=2))
    )])
    
    fig.update_layout(
        title={
            'text': '불량 유형 비율',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24}
        },
        height=1000,
        width=1200,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        )
    )
    
    # container를 사용하여 차트를 중앙에 배치
    with st.container():
        col1, col2, col3 = st.columns([1,3,1])
        with col2:
            st.plotly_chart(fig, use_container_width=True)
    
    # 4. 품질 예측 알림
    st.markdown('<p class="header-style">⚠️ 품질 예측 알림</p>', unsafe_allow_html=True)
    
    # 현재 상태에 따른 알림 메시지
    if quality_score >= 90:
        st.success("✅ 현재 모든 품질 지표가 정상 범위 내에 있습니다!")
    elif quality_score >= 80:
        warning_items = [item for item in selected_items if defect_data[item] > 0.5]
        if warning_items:
            warning_msg = "\n".join([f"- {item} 발생률이 기준보다 높습니다" for item in warning_items])
            st.warning(f"""
            ⚠️ 주의가 필요한 항목이 있습니다:
            {warning_msg}
            """)
        else:
            st.warning("⚠️ 일부 품질 지표가 주의 수준입니다.")
    else:
        st.error("""
        🚨 긴급 확인이 필요합니다:
        - 품질 점수가 위험 수준입니다
        - 즉시 생산 라인 점검이 필요합니다
        """)

if __name__ == "__main__":
    main()