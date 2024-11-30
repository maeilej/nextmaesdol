import streamlit as st
from components.menu import display_sidebar_menu
from views.sign_page import display_sign_in_page
from views.main_page import display_main_page  # 추가로 페이지가 있을 경우 사용
from views.dashboard_page import display_dashboard_page
from views.admin_page import display_admin_page
from auth.authentication import require_login


st.set_page_config(layout="wide")
# 선택한 메뉴에 따라 다른 페이지 표시
selected_menu = display_sidebar_menu()  # 선택된 메뉴를 반환받습니다.


# if selected_menu == "Login":
#     display_sign_in_page()

# else:
    # require_login()
if selected_menu == "두부 불량 탐지":
    display_main_page()
elif selected_menu == "Dashboard":
    display_dashboard_page()
elif selected_menu == "관리자":
    display_admin_page()