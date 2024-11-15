import streamlit as st
import cv2
import numpy as np
import os

# 영상 처리 함수
def process_video(video_file):
    # OpenCV로 영상 읽기
    video = cv2.VideoCapture(video_file)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(video.get(cv2.CAP_PROP_FPS))
    st.write(f"총 프레임: {frame_count}, FPS: {fps}")
    
    # 저장된 프레임들
    frames = []
    
    # 프레임 추출
    frame_idx = 0
    while True:
        ret, frame = video.read()
        if not ret:
            break
        frames.append(frame)
        
        # 프레임을 이미지로 저장 (옵션)
        if frame_idx < 5:  # 처음 5개 프레임만 화면에 표시
            st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), caption=f"Frame {frame_idx}")
        frame_idx += 1
    
    video.release()
    return frames