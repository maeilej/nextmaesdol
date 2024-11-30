import streamlit as st
import psutil

def display_main_page_sidebar():

    st.title("System Resource Dashboard")

    # CPU Usage
    cpu_usage = psutil.cpu_percent(interval=1)
    st.metric("CPU Usage", f"{cpu_usage}%")

    # Memory Usage
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    st.metric("Memory Usage", f"{memory_usage}%")

    # Disk Usage
    disk = psutil.disk_usage("/")
    disk_usage = disk.percent
    st.metric("Disk Usage", f"{disk_usage}%")

    # File Upload
    st.subheader("File Upload")
    uploaded_file = st.file_uploader("Choose a file", type=["mp4"])
    if uploaded_file is not None:
        st.write(f"Uploaded file: {uploaded_file.name}")
        st.video(uploaded_file)
