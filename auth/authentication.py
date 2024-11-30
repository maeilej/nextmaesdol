import streamlit as st
from views.sign_page import display_sign_in_page

def require_login():
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.warning("로그인이 필요합니다.")
        # display_sign_in_page()
        st.stop()