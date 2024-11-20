import streamlit as st
import cv2
import numpy as np
from datetime import datetime
import time

# 페이지 설정
st.set_page_config(
    page_title="두부 품질 검사 시스템",
    page_icon="🧊",
    layout="wide"
)

# CSS 스타일
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        background-color: #0483ee;
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 4px;
    }
    .quality-card {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .status-ok {
        color: #00c853;
        font-weight: bold;
        font-size: 24px;
    }
    .status-error {
        color: #d32f2f;
        font-weight: bold;
        font-size: 24px;
    }
    .metric-label {
        font-size: 14px;
        color: #666;
    }
    .metric-value {
        font-size: 20px;
        font-weight: bold;
        color: #333;
    }
    .inspection-header {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 1rem;
        color: #1976d2;
    }
</style>
""", unsafe_allow_html=True)

def get_inspection_image():
    # 이미지를 grayscale로 읽기
    img = cv2.imread('tofuimage.png', cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    return img

def main():
    st.title("두부 품질 검사 시스템")
    
    # 사이드바 - 검사 설정
    with st.sidebar:
        st.header("검사 설정")
        threshold = st.slider("불량 판정 임계값", 0.0, 1.0, 0.8, 0.01)
        inspection_speed = st.select_slider(
            "검사 속도",
            options=["저속", "중속", "고속"],
            value="중속"
        )
        st.divider()
        st.subheader("시스템 상태")
        st.success("정상 작동 중")
        st.metric("금일 검사 수량", "1,234개")
        st.metric("불량률", "0.8%")

    # 메인 화면 2단 레이아웃
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<p class="inspection-header">실시간 검사</p>', unsafe_allow_html=True)
        
        # 이미지 표시 영역
        placeholder = st.empty()
        with placeholder.container():
            # 실제 검사 이미지 표시
            inspection_image = get_inspection_image()
            if inspection_image is not None:
                st.image(inspection_image, caption="실시간 검사 영상", use_column_width=True)
            else:
                st.error("이미지를 불러올 수 없습니다.")
        
        # 컨트롤 버튼들
        col1_1, col1_2, col1_3 = st.columns(3)
        with col1_1:
            if st.button("검사 시작", use_container_width=True):
                pass
        with col1_2:
            if st.button("일시정지", use_container_width=True):
                pass
        with col1_3:
            if st.button("설정", use_container_width=True):
                pass

    with col2:
        # 검사 결과 표시
        st.markdown('<p class="inspection-header">검사 결과</p>', unsafe_allow_html=True)
        
        # 현재 검사 결과
        st.markdown("""
        <div class="quality-card">
            <p class="status-ok">OK</p>
            <hr>
            <p class="metric-label">검사 시간</p>
            <p class="metric-value">2024-02-08 14:30:45</p>
            <p class="metric-label">품질 점수</p>
            <p class="metric-value">98.5%</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 품질 지표
        st.subheader("품질 지표")
        
        # 진행 바로 각 지표 표시
        metrics = {
            "패임": 0.65,
            "모서리": 0.55,
            "기포": 0.45,
            "이물질": 0.25
        }
        
        for name, value in metrics.items():
            st.markdown(f"**{name}**")
            st.progress(value)
            
        # 최근 검사 이력
        st.subheader("최근 검사 이력")
        history = [
            {"time": "14:30:45", "result": "OK", "score": "98.5%"},
            {"time": "14:30:42", "result": "OK", "score": "97.8%"},
            {"time": "14:30:39", "result": "NG", "score": "75.2%"},
            {"time": "14:30:36", "result": "OK", "score": "99.1%"},
        ]
        
        for item in history:
            st.markdown(
                f"<div style='padding: 0.5rem; background-color: {'#e8f5e9' if item['result']=='OK' else '#ffebee'}; "
                f"border-radius: 4px; margin-bottom: 0.5rem;'>"
                f"<span style='color: {'#00c853' if item['result']=='OK' else '#d32f2f'}'>{item['result']}</span> | "
                f"{item['time']} | {item['score']}</div>",
                unsafe_allow_html=True
            )

if __name__ == "__main__":
    main()