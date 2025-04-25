import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# 파일 경로
STUDENTS_FILE = "data/students.json"
EXAM_FILE = "data/exam_dates.json"
USERS_FILE = "data/users.json"

# 파일 디렉토리 확인 및 생성
def ensure_directory(file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

# JSON 파일 로드
def load_json(file_path):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# JSON 파일 저장
def save_json(data, file_path):
    ensure_directory(file_path)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 로그인 함수
def login(password):
    users = load_json("data/users.json")

    if username in users and users[username]["password"] == password:
        # 로그인 성공
        st.session_state["username"] = username
        st.session_state["role"] = users[username]["role"]
        go("main")  # 메인 페이지로 이동
    else:
        st.error("아이디 또는 비밀번호가 틀렸습니다.")

# 사용자 관리 (관리자 전용)
def manage_users():
    st.header("👤 사용자 관리 (관리자 전용)")
    users = load_json(USERS_FILE)

    if st.button("사용자 추가"):
        with st.form("add_user"):
            name = st.text_input("이름")
            password = st.text_input("비밀번호")
            role = st.selectbox("역할", ["원장", "실장", "팀장", "조교", "강사"])
            submitted = st.form_submit_button("저장")
            if submitted and name and password and role:
                users[password] = {"name": name, "role": role}
                save_json(users, USERS_FILE)
                st.success("사용자 추가 완료!")

    st.subheader("📋 기존 사용자")
    for pwd, info in users.items():
        with st.expander(f"{info['name']} ({info['role']})"):
            new_name = st.text_input(f"이름 수정 - {pwd}", value=info['name'], key=f"name_{pwd}")
            new_role = st.selectbox(f"역할 수정 - {pwd}", ["원장", "실장", "팀장", "조교", "강사"], index=["원장", "실장", "팀장", "조교", "강사"].index(info['role']), key=f"role_{pwd}")
            if st.button(f"수정하기 - {pwd}"):
                users[pwd] = {"name": new_name, "role": new_role}
                save_json(users, USERS_FILE)
                st.success("수정 완료!")
            if st.button(f"삭제하기 - {pwd}"):
                users.pop(pwd)
                save_json(users, USERS_FILE)
                st.success("삭제 완료!")
                st.experimental_rerun()

# 메인 함수
def main():
    st.set_page_config(page_title="학원 관리 시스템", page_icon="📚", layout="wide")

    if 'user' not in st.session_state:
        st.title("📚 학원 관리 시스템 로그인")
        password = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            if login(password):
                st.success("로그인 성공!")
                st.experimental_rerun()
            else:
                st.error("비밀번호가 틀렸습니다.")
        return

    user = st.session_state['user']
    role = user['role']

    st.sidebar.title(f"환영합니다, {user['name']}님 ({role})")
    menu_options = []
    if role in ["원장", "실장"]:
        menu_options = ["현황보고", "직원관리", "학생관리", "학생정보", "시험입력", "학생시간표출력", "강사시간표출력"]
    elif role == "팀장":
        menu_options = ["학생관리", "학생정보", "시험입력", "학생시간표출력", "강사시간표출력"]
    elif role == "조교":
        menu_options = ["학생관리", "시험입력", "학생시간표출력"]
    elif role == "강사":
        menu_options = ["시험입력", "학생시간표출력"]

    choice = st.sidebar.radio("메뉴", menu_options)

    if choice == "직원관리" and role in ["원장", "실장"]:
        manage_users()

    elif choice == "학생관리":
        st.header("📖 학생 관리")
        st.info("(구체적인 기능은 다음 단계에서 추가)")

    elif choice == "학생정보":
        st.header("🧾 학생 정보")
        st.info("(구체적인 기능은 다음 단계에서 추가)")

    elif choice == "시험입력":
        st.header("📝 시험 입력")
        st.info("(구체적인 기능은 다음 단계에서 추가)")

    elif choice == "학생시간표출력":
        st.header("📅 학생 시간표 출력")
        st.info("(구체적인 기능은 다음 단계에서 추가)")

    elif choice == "강사시간표출력":
        st.header("👨‍🏫 강사 시간표 출력")
        st.info("(구체적인 기능은 다음 단계에서 추가)")

    elif choice == "현황보고":
        st.header("📊 전체 현황 보고")
        st.info("(구체적인 기능은 다음 단계에서 추가)")

if __name__ == "__main__":
    main()
