import streamlit as st

def display_sign_in_page():
    st.header("Login")
    
    # 사용자 입력 받기
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    # 기본 계정 정보
    valid_users = {
        "user": {"password": "user123", "role": "user"},
        "manager": {"password": "manager123", "role": "manager"},
    }

    if st.button("로그인"):
        if username in valid_users and valid_users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = valid_users[username]["role"]
            st.success(f"{username}님, 안녕하세요!")
        else:
            st.error("아이디 또는 비밀번호가 틀렸습니다.")
