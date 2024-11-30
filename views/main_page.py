import streamlit as st

from components.main_page_sidebar import display_main_page_sidebar
from video_process.video_processing import process_video
import psutil
import os
import cv2
import base64
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from dynamodb.add_dummy_data import insert_logs_to_dynamodb
from s3.upload_video import upload_to_s3
from s3.download_video import download_from_s3
from sagemaker.call_endpoint import process_frames_with_endpoint
import re
import boto3
from datetime import datetime
import time

def natural_sort_key(s):
    """Sort files naturally by extracting numbers."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def display_results(results_summary, img_path):
    # Ensure session state variables are initialized
    if "current_image_index" not in st.session_state:
        st.session_state.current_image_index = 0

    # Ensure there are results to display
    if not results_summary:
        st.error("결과 데이터가 없습니다.")
        return

    # Current image index
    current_index = st.session_state.current_image_index

    # Main 2-column layout
    col1, col2 = st.columns([2, 1])

    with col1:
        # Get current result
        current_result = results_summary[current_index]
        current_image_path = current_result['frame_path']
        current_status = current_result['status']
        defect_type = current_result.get('result_details', 'N/A')

        # Convert image to base64 for inline display
        def get_image_base64(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode()

        img_base64 = get_image_base64(current_image_path)

        # Border color based on status
        border_color = "#00c853" if current_status == "OK" else "#d32f2f"

        st.markdown(f"""
        <div class="bordered-image" style="border: 5px solid {border_color};">
            <img class="tofu-img" src="data:image/png;base64,{img_base64}" alt="이미지">
        </div>
        """, unsafe_allow_html=True)

        # Display button controls to navigate images
        col1_1, col1_2, col1_3 = st.columns(3)

        with col1_1:
            if st.button("이전", key="prev"):
                if current_index > 0:
                    st.session_state.current_image_index -= 1

        with col1_2:
            if st.button("다음", key="next"):
                if current_index < len(results_summary) - 1:
                    st.session_state.current_image_index += 1

        with col1_3:
            if st.button("처음으로", key="first"):
                st.session_state.current_image_index = 0

    with col2:
        # 상태 및 결함 유형 출력
        status_color = "status-ok" if current_status == "OK" else "status-error"
        st.markdown(f"""
        <div class="status-box">
            <span class="{status_color}">{current_status}</span>
        </div>
        """, unsafe_allow_html=True)

        if current_status == "NG":
            st.markdown(f"""
            <div class="result-box">
                <span class="ng-result">{defect_type}</span>
            </div>
            """, unsafe_allow_html=True)

        # 검사 결과 요약
        total_inspected = len(results_summary)
        total_ok = sum(1 for result in results_summary if result['status'] == "OK")
        total_ng = total_inspected - total_ok

        st.markdown(f"""
        <div class="quality-card">
            <div class="metric-item">
                <div class="metric-label">총 검사수</div>
                <div class="metric-value">{total_inspected}개</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">양품수</div>
                <div class="metric-value">{total_ok}개</div>
            </div>
            <div class="metric-item">
                <div class="metric-label">불량수</div>
                <div class="metric-value">{total_ng}개</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 불량 유형 그래프
        st.subheader("불량 종류별 수량")

        # Collect defect types for NG results
        ng_defects = [result['result_details'] for result in results_summary if result['status'] == "NG"]
        defect_counts = {defect: ng_defects.count(defect) for defect in set(ng_defects)}

        labels = list(defect_counts.keys())
        values = list(defect_counts.values())

        # 수평 막대그래프 생성
        fig = go.Figure(data=[go.Bar(
            x=values,
            y=labels,
            orientation='h',
            marker=dict(
                color=['#1976D2', '#64B5F6', '#90CAF9', '#BBDEFB']
            )
        )])

        # 레이아웃 설정
        fig.update_layout(
            title='불량 유형 비율',
            xaxis_title='수량',
            yaxis_title='불량 유형',
            height=400,
            margin=dict(l=50, r=50, t=50, b=50)
        )

        # 그래프 출력
        st.plotly_chart(fig, use_container_width=True)


# 메인 페이지 표시 함수
def display_main_page():
    st.markdown('<link rel="stylesheet" href="./assets/css/main_page.css">', unsafe_allow_html=True)

    # CSS 스타일
    st.markdown("""
        <style>
            .bordered-image {
                display: block;
                width: 100%;
                border: 5px solid #012313; /* 테두리 색상 */
                border-radius: 10px; /* 테두리 둥글기 */
                padding: 20px; /* 테두리 안쪽 여백 */
                background-color: #f0f0f0; /* 테두리 배경 색상 */
                margin-bottom: 10px;
            }
            .tofu-img{
                width: 100%;  /* 이미지가 전체 폭에 맞게 크기 확장 */
                max-width: 1000px;  /* 최대 너비를 설정해 너무 커지지 않게 조정 */
                height: auto;  /* 이미지 크기 비율 유지하며, 부모 요소에 맞게 확장 */
            }
            .stButton>button {
                background-color: #0483ee;
                color: white;
                font-weight: bold;
                padding: 0.5rem 1rem;
                border: none;
                border-radius: 4px;
            }
            /* 스타일 정의 */
            .button-container {
                margin-top: 1rem;
                margin-bottom: 35px;
                display: flex;
                justify-content: space-between;
            }
            .button-container .button {
                flex: 1;
                padding: 10px;
                color: white;
                border: none;
                cursor: pointer;
            }
           .button-container .button.start {
                background-color: green;
                margin-right: 10px;
            }
        
            .button-container .button.pause {
                background-color: red;
                margin-right: 10px;
            }
        
            .button-container .button.settings {
                background-color: blue;
            }
    
            /* Quality Card 스타일 */
            .quality-card {
                padding: 1rem;
                background-color: #f8f8f8;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                margin-bottom: 1rem;
            }
        
            /* 수평 정렬을 위한 스타일 */
            .quality-card .metric-label,
            .quality-card .metric-value {
                display: flex;
                align-items: center;
                margin-bottom: 0.5rem;
            }
        
            .quality-card .metric-label {
                font-weight: bold;
                width: 120px;  /* 레이블에 고정 너비 지정 */
            }
        
            .quality-card .metric-value {
                color: #4caf50;  /* 수치 값에 색상 적용 */
                margin-left: 6px;  /* 레이블과 수치 사이 간격 */
            }
        
            /* 수평 배치 */
            .quality-card .metric-item {
                display: flex;
                justify-content: flex-start;  /* 항목들이 수평으로 배치되도록 설정 */
                margin-bottom: 0.5rem;
            }
                        
            /* 상태 박스 스타일 */
            .status-box {
                display: flex;
                justify-content: center;
                align-items: center;
                width: 100%;
                height: 100px;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                margin-bottom: 1rem;       
            }
            
            .result-box {
                display: flex;
                justify-content: center;
                align-items: center;
                width: 100%;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                margin-top: 10px
                margin-bottom: 1rem;       
            }
            
            .ng-result {
                color: #d32f2f;
                font-weight: bold;
                font-size: 30px;   
            }
        
            .status-ok {
                color: #00c853;
                font-weight: bold;
                font-size: 100px;
            }
            .status-error {
                color: #d32f2f;
                font-weight: bold;
                font-size: 100px;
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
            .agent-box {
                padding: 1rem;
                background-color: #f8f8f8;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                margin-bottom: 1rem;
            }
            .agent-label {
                font-weight: bold;
                margin-bottom: 0.5rem;
                font-size: 20px;
            }
            .agent-value {
                display: flex;
                align-items: center;
            }
        </style>
    """, unsafe_allow_html=True)
    
    if "current_image_path" not in st.session_state:
        st.session_state.current_image_path = ""
    if "video_processed" not in st.session_state:
        st.session_state.video_processed = False

    # 사이드바 설정
    with st.sidebar:
        st.header("검사 설정")
        threshold = st.slider("불량 판정 임계값", 0.0, 1.0, 0.8, 0.01)

        st.success("정상 작동 중")

        UPLOAD_DIR = "uploaded_videos"
        os.makedirs(UPLOAD_DIR, exist_ok=True)  # 디렉토리가 없으면 생성
        
        # File Upload
        st.subheader("영상 업로드")
        uploaded_file = st.file_uploader("Choose a file", type=["mp4"])
        if uploaded_file is not None:
            st.write(f"Uploaded file: {uploaded_file.name}")
            
            file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())
        
            st.success(f"Video successfully uploaded: {uploaded_file.name}")
            
            # 동영상 재생
            st.video(file_path, autoplay=True)
            
            # 비디오가 아직 처리되지 않았다면 처리
            if not st.session_state.video_processed:
                st.write("Processing video...")
                frames = process_video(file_path)
                st.session_state.current_image_path = frames
                st.session_state.video_processed = True
                st.success("Video processing completed!")
                results = process_frames_with_endpoint(frames)
                os.remove(file_path)
    
            # 세션 상태 업데이트
            st.session_state["video_uploaded"] = True
            st.session_state["last_uploaded_file"] = uploaded_file.name


    # 메인 페이지 컨텐츠
    if st.session_state.current_image_path == "":
        st.write("Please Upload Video")
    else:
        display_results(results, st.session_state.current_image_path)

    # # 이미지 출력
    # if st.session_state.current_image_path == "":
    #     st.write("Please Upload Video")
    # else:
        
    #     # Ensure session state variables are initialized
    #     if "current_image_index" not in st.session_state:
    #         st.session_state.current_image_index = 0
            
    #     if "current_image_path" not in st.session_state:
    #         st.session_state.current_image_path = ""
        
    #     img_path = st.session_state.current_image_path
        
    #     # Check if the image path is set
    #     if not img_path:
    #         st.write("st.session_state.current_image_path: ", st.session_state.current_image_path)
    #         st.error("이미지 경로가 설정되지 않았습니다.")
    #         return
        
    #     # Ensure the image path exists
    #     if os.path.exists(img_path):
    #         # Main 2-column layout
    #         col1, col2 = st.columns([2, 1])

    #         with col1:
                
    #             # Get all image files (png, jpg, jpeg) from the directory
    #             image_files = sorted(
    #                 [f for f in os.listdir(img_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))],
    #                 key=natural_sort_key  # Sort using natural sorting
    #             )

    #             if not image_files:
    #                 st.error("이미지가 없습니다.")
    #                 return

    #             # Ensure session state variables are initialized
    #             if "current_image_index" not in st.session_state:
    #                 st.session_state.current_image_index = 0  # Start at the first image index

    #             current_index = st.session_state.current_image_index
    #             current_image_path = os.path.join(img_path, image_files[current_index])

    #             # Convert the image to base64 for inline display
    #             def get_image_base64(image_path):
    #                 with open(image_path, "rb") as image_file:
    #                     return base64.b64encode(image_file.read()).decode()

    #             img_base64 = get_image_base64(current_image_path)

    #             # 테두리 색상 상태에 따라 변경
    #             current_status = status_list[current_index]
    #             border_color = "#00c853" if current_status == "OK" else "#d32f2f"

    #             st.markdown(f"""
    #             <div class="bordered-image" style="border: 5px solid {border_color};">
    #                 <img class="tofu-img" src="data:image/png;base64,{img_base64}" alt="이미지">
    #             </div>
    #             """, unsafe_allow_html=True)

    #             # 현재 이미지와 상태 정보 출력
    #             # st.write(f"현재 이미지: {image_files[current_index]} ({current_index + 1}/{len(image_files)})")
    #             # st.write(f"검사 상태: {status_list[current_index]}")

    #             # Display button controls to navigate images
    #             col1_1, col1_2, col1_3 = st.columns(3)

    #             with col1_1:
    #                 if st.button("이전"):
    #                     if current_index > 0:
    #                         st.session_state.current_image_index -= 1  # Go to previous image

    #             with col1_2:
    #                 if st.button("다음"):
    #                     if current_index < len(image_files) - 1:
    #                         st.session_state.current_image_index += 1  # Go to next image

    #             with col1_3:
    #                 if st.button("처음으로"):
    #                     st.session_state.current_image_index = 0  # Go to first image

    #         with col2:
    #             # 현재 상태 기반으로 색상 표시
    #             current_status = status_list[current_index]
    #             status_color = "status-ok" if current_status == "OK" else "status-error"
    #             st.markdown(
    #                 f'''
    #                     <div class="status-box">
    #                         <span class="{status_color}">{current_status}</span>
    #                     </div>
    #                 ''',
    #                 unsafe_allow_html=True
    #             )

    #             # 상태 리스트와 defect 타입에 맞는 결과 출력
    #             current_status = status_list[current_index]
    #             defect_type = None
                
    #             # Display defect type for "NG"
    #             if current_status == "NG":
    #                 defect_type = ng_defect_types[current_index]
    #                 st.markdown(f"""
    #                 <div class="result-box">
    #                     <span class="ng-result">{defect_type}</span>
    #                 </div>
    #                 """, unsafe_allow_html=True)
    #             else:
    #                 st.markdown(
    #                     '''
    #                     <div class="result-box>
    #                     </div>
    #                     ''',
    #                     unsafe_allow_html=True
    #                 )
    
    #             # 검사 결과 표시
    #             # st.markdown('<p class="inspection-header">검수 라인 번호</p>', unsafe_allow_html=True)
                
    #             # 검사 결과 표시
    #             st.markdown("""
    #                 <div class="quality-card">
    #                     <div class="metric-item">
    #                         <div class="metric-label">총 검사수</div>
    #                         <div class="metric-value">40개</div>
    #                     </div>
    #                     <div class="metric-item">
    #                         <div class="metric-label">양품수</div>
    #                         <div class="metric-value">20개</div>
    #                     </div>
    #                     <div class="metric-item">
    #                         <div class="metric-label">불량수</div>
    #                         <div class="metric-value">20개</div>
    #                     </div>
    #                 </div>
    #             """, unsafe_allow_html=True)

    #              # 불량 유형 그래프
    #             st.subheader("불량 종류별 수량")
    
    #             labels = ["패임", "찢김", "기포", "이물질"]
    #             values = [6, 7, 6, 1]
    
    #             # 수평 막대그래프 생성
    #             fig = go.Figure(data=[go.Bar(
    #                 x=values,
    #                 y=labels,
    #                 orientation='h',
    #                 marker=dict(
    #                     color=['#1976D2', '#64B5F6', '#90CAF9', '#BBDEFB']
    #                 )
    #             )])
    
    #             # 레이아웃 설정
    #             fig.update_layout(
    #                 title='불량 유형 비율',
    #                 xaxis_title='비율 (%)',
    #                 yaxis_title='불량 유형',
    #                 height=400,
    #                 margin=dict(l=50, r=50, t=50, b=50)
    #             )
    
    #             # 그래프 출력
    #             st.plotly_chart(fig, use_container_width=True)
