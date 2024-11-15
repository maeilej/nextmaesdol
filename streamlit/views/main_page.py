import streamlit as st

from components.main_page_sidebar import display_main_page_sidebar
from components.video_processing import process_video
import psutil
import os
import cv2
import base64

def display_main_page():
    #css 적용
    st.markdown('<link rel="stylesheet" href="./assets/css/main_page.css">', unsafe_allow_html=True)

    # CSS 스타일
    st.markdown("""
    <style>
        .main{
            width: 100%;
            padding: 0px;      
        }
        .bordered-image {
            display: block;
            width: 100%;
            border: 5px solid #012313; /* 테두리 색상 */
            border-radius: 10px; /* 테두리 둥글기 */
            padding: 50px; /* 테두리 안쪽 여백 */
            background-color: #f0f0f0; /* 테두리 배경 색상 */
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

        .status-ok {
            color: #00c853;
            font-weight: bold;
            font-size: 40px;
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


    # display_main_page_sidebar()
    with st.sidebar:
        st.header("검사 설정")
        threshold = st.slider("불량 판정 임계값", 0.0, 1.0, 0.8, 0.01)

        # inspection_speed = st.select_slider(
        #     "검사 속도",
        #     options=["저속", "중속", "고속"],
        #     value="중속"
        # )
        # st.divider()
        st.subheader("시스템 상태")

        # 정상 작동 여부 확인
        # if psutil.cpu_percent() < 80:
        #     st.success("정상 작동 중")
        # else:
        #     st.error("과부하 상태입니다")

        st.success("정상 작동 중")
        # st.metric("금일 검사 수량", "1,234개")
        st.metric("불량률", "0.8%")

        # File Upload
        st.subheader("영상 업로드")
        uploaded_file = st.file_uploader("Choose a file", type=["mp4"])
        if uploaded_file is not None:
            st.write(f"Uploaded file: {uploaded_file.name}")
            st.video(uploaded_file)

            # 업로드된 파일을 임시 파일로 저장
            temp_video_path = f"temp_{uploaded_file.name}"
            with open(temp_video_path, "wb") as f:
                f.write(uploaded_file.read())

            # 비디오 처리
            frames = process_video(temp_video_path)

            # if frames:
            #     st.success(f"{len(frames)} frames extracted!")
            #     # 첫 번째 프레임 출력
            #     st.image(cv2.cvtColor(frames[0], cv2.COLOR_BGR2RGB), caption="First Frame")

            # 임시 파일 삭제
            os.remove(temp_video_path)
            

    # 메인 화면 2단 레이아웃
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # st.markdown('<p class="inspection-header">실시간 검사</p>', unsafe_allow_html=True)
        
        # 이미지 표시 영역
        placeholder = st.empty()
        with placeholder.container():
            # st.image("./img/tofu.png", caption="실시간 검사 영상")
            
            # 이미지 경로
            image_path = "./img/tofu.png"

            # 이미지 파일이 있는지 확인
            if os.path.exists(image_path):
                # 이미지 파일을 Base64로 인코딩하여 st.markdown에서 사용
                def get_image_base64(image_path):
                    with open(image_path, "rb") as image_file:
                        encoded_image = base64.b64encode(image_file.read()).decode()
                    return encoded_image

                # Base64로 인코딩된 이미지 경로
                img_base64 = get_image_base64(image_path)

                # 스타일 지정 및 이미지 삽입
                st.markdown(f"""
                    <div class="bordered-image">
                        <img class="tofu-img" src="data:image/png;base64,{img_base64}" alt="실시간 검사 영상" width="100%">
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.error("이미지 파일이 존재하지 않습니다.")
        
        # 컨트롤 버튼들
        # col1_1, col1_2, col1_3 = st.columns(3)
        # with col1_1:
        #     if st.button("검사 시작", use_container_width=True):
        #         pass
        # with col1_2:
        #     if st.button("일시정지", use_container_width=True):
        #         pass
        # with col1_3:
        #     if st.button("설정", use_container_width=True):
        #         pass

        # 버튼을 포함하는 div를 스타일에 맞게 표시
        st.markdown("""
        <div class="button-container">
            <button class="button pause" onclick="alert('정지!')">정지</button>
            <button class="button start" onclick="alert('가동!')">가동</button>
            <button class="button settings" onclick="alert('기능!')">기능</button>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # 검사 결과 표시
        st.markdown('<p class="inspection-header">검수 라인 번호</p>', unsafe_allow_html=True)
        
        # 검사 결과 표시
        st.markdown("""
            <div class="quality-card">
                <div class="metric-item">
                    <div class="metric-label">총 검사수</div>
                    <div class="metric-value">1,234개</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">양품수</div>
                    <div class="metric-value">1,200개</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">불량수</div>
                    <div class="metric-value">34개</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(
            '''
                <div class="status-box">
                    <span class="status-ok">OK</span>
                </div>
            ''',
            unsafe_allow_html=True
        )

        # 에이전트 분석 결과
        st.markdown("""
            <div class="agent-box">
                <div class="agent-label">Agent</div>
                <div class="agent-value">
                    <span class="agent-result">베스트 프렉티스</span>    
                </div>
            </div>              
        """, unsafe_allow_html=True)
