import streamlit as st
from streamlit_option_menu import option_menu

def display_sidebar_menu():
    with st.sidebar:
        with st.expander("NXTmaesdol"):
            #selected_menu = st.radio("", ["Login", "두부 불량 탐지", "Dashboard", "관리자"])
            selected_menu = option_menu("", ["두부 불량 탐지", "Dashboard", "관리자"])
    return selected_menu

