import streamlit as st
from components.main_page_sidebar import display_main_page_sidebar
import psutil

def display_main_page():
    # display_main_page_sidebar()
    with st.sidebar:
        st.title("검사 설정")

        threshold = st.slider("불량 판정 임계값", 0.0, 1.0, 0.01)
        speed_level = st.slider("두부 불량 탐지 속도", 1, 3, 2, step=1, help="1: 저속, 2: 중속, 3: 고속")

        # File Upload
        st.subheader("File Upload")
        uploaded_file = st.file_uploader("Choose a file", type=["mp4"])
        if uploaded_file is not None:
            st.write(f"Uploaded file: {uploaded_file.name}")
        

    st.title("두부 품질 검사 시스템")
    st.write("실시간 검사", color="blue")