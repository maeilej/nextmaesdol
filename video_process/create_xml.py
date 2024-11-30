import shutil
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

def create_xml(frame_filename):
    # XML 파일 이름 설정
    xml_filename = frame_filename.replace('.jpg', '.xml')
    
    # 기본 주석 정보 설정 (예제: 이미지 크기와 더미 오브젝트 정보)
    width, height = 1920, 1080  # 예제 크기 (실제 영상에 맞게 조정 필요)
    depth = 3  # 컬러 이미지 기준
    
    # 루트 태그 생성
    annotation = ET.Element('annotation')
    
    # 폴더 정보 추가
    folder = ET.SubElement(annotation, 'folder')
    folder.text = os.path.basename(os.path.dirname(frame_filename))
    
    # 파일 이름 추가
    filename = ET.SubElement(annotation, 'filename')
    filename.text = os.path.basename(frame_filename)
    
    # 경로 추가
    path = ET.SubElement(annotation, 'path')
    path.text = os.path.abspath(frame_filename)
    
    # 소스 정보 추가
    source = ET.SubElement(annotation, 'source')
    database = ET.SubElement(source, 'database')
    database.text = 'Unknown'
    
    # 이미지 크기 정보 추가
    size = ET.SubElement(annotation, 'size')
    width_elem = ET.SubElement(size, 'width')
    width_elem.text = str(width)
    height_elem = ET.SubElement(size, 'height')
    height_elem.text = str(height)
    depth_elem = ET.SubElement(size, 'depth')
    depth_elem.text = str(depth)
    
    # segmented 태그 추가 (기본값 0)
    segmented = ET.SubElement(annotation, 'segmented')
    segmented.text = '0'
    
    # 객체 추가 예제 (더미 데이터)
    object_elem = ET.SubElement(annotation, 'object')
    name = ET.SubElement(object_elem, 'name')
    name.text = 'example_object'  # 객체 이름
    pose = ET.SubElement(object_elem, 'pose')
    pose.text = 'Unspecified'
    truncated = ET.SubElement(object_elem, 'truncated')
    truncated.text = '0'
    difficult = ET.SubElement(object_elem, 'difficult')
    difficult.text = '0'
    
    # 경계 상자 정보 추가
    bndbox = ET.SubElement(object_elem, 'bndbox')
    xmin = ET.SubElement(bndbox, 'xmin')
    xmin.text = '50'  # 시작 x 좌표
    ymin = ET.SubElement(bndbox, 'ymin')
    ymin.text = '50'  # 시작 y 좌표
    xmax = ET.SubElement(bndbox, 'xmax')
    xmax.text = '150'  # 끝 x 좌표
    ymax = ET.SubElement(bndbox, 'ymax')
    ymax.text = '150'  # 끝 y 좌표
    
    # XML 파일 저장
    tree = ET.ElementTree(annotation)
    tree.write(xml_filename, encoding='utf-8', xml_declaration=True)
    print(f"XML file created: {xml_filename}")
    
    