import streamlit as st
import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib import animation
from PIL import Image
from xml.etree import ElementTree as ET
import shutil
import subprocess
import sys
from video_process.create_xml import create_xml

# 영상 처리 함수
def process_video(video_path):
    frames_dir = "video_2_frame"
    frames_dir_yolo = "frame_2_yolo"

    # 기존 디렉토리 삭제 및 생성
    if os.path.exists(frames_dir):
        shutil.rmtree(frames_dir)
    os.makedirs(frames_dir, exist_ok=True)

    # 비디오 파일 열기
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Unable to open video file.")
        return None

    ret, previous_frame = cap.read()
    if not ret:
        print("Error: Unable to read the first frame.")
        cap.release()
        return None

    # 화면 크기 가져오기
    frame_height, frame_width = previous_frame.shape[:2]
    center_x, center_y = frame_width // 2, frame_height // 2
    threshold_distance = 50  # 중심으로부터 허용할 거리 (픽셀)
    similarity_threshold = 100  # 유사성 임계값 (작을수록 더 엄격)

    frame_number = 0
    last_saved_frame = None  # 마지막으로 저장된 프레임
    last_saved_frame_number = -1  # 마지막 저장된 프레임 번호

    while ret:
        ret, current_frame = cap.read()
        if not ret:
            print("End of video or unable to read frame.")
            break  # 프레임을 더 이상 읽을 수 없으면 종료

        # 1. 그레이스케일 변환
        gray_frame = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)

        # 2. 대비 향상 (히스토그램 평활화)
        enhanced_frame = cv2.equalizeHist(gray_frame)

        # 3. 특정 밝기 영역 마스크 처리
        _, mask = cv2.threshold(enhanced_frame, 50, 255, cv2.THRESH_BINARY)

        # 4. 윤곽선 찾기
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)

            # 중심 좌표 계산
            roi_center_x = x + w // 2
            roi_center_y = y + h // 2

            # ROI 중심이 화면 중심에 가까운지 확인
            distance_to_center = np.sqrt((roi_center_x - center_x) ** 2 + (roi_center_y - center_y) ** 2)
            if distance_to_center <= threshold_distance:
                # 프레임 유사성 검사
                if last_saved_frame is not None:
                    difference = cv2.absdiff(last_saved_frame, gray_frame)
                    difference_sum = np.sum(difference)

                    # 유사한 프레임은 건너뛰기
                    if difference_sum < similarity_threshold:
                        print(f"Skipped similar frame at {frame_number}, difference: {difference_sum}")
                        continue  # 유사한 프레임은 저장하지 않음

                # 연속된 프레임 번호인지 확인
                if frame_number - last_saved_frame_number == 1:
                    print(f"Skipped consecutive frame at {frame_number}")
                    continue

                # 새로운 프레임 저장
                frame_filename = os.path.join(frames_dir, f'frame_{frame_number}.jpg')
                cv2.imwrite(frame_filename, current_frame)
                print(f"Saved unique centered frame: {frame_filename}")
                create_xml(frame_filename)

                # 현재 프레임을 마지막 저장된 프레임으로 업데이트
                last_saved_frame = gray_frame.copy()
                last_saved_frame_number = frame_number  # 마지막 저장된 프레임 번호 업데이트

        frame_number += 1

    cap.release()
    return frames_dir
