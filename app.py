import streamlit as st
import pandas as pd
import json
import os
from datetime import date
from openpyxl import Workbook
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# 파일 경로 설정
STUDENTS_FILE = "data/students.json"
EXAM_DATES_FILE = "data/exam_dates.json"
USERS_FILE = "data/users.json"

# 파일 디렉토리 확인 및 생성
def ensure_directory(file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

# JSON 파일 로드 및 저장
def load_json(file_path):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(data, file_path):
    ensure_directory(file_path)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 페이지 이동
def go(page_name):
    st.session_state["page"] = page_name

# 메인 함수
def main():
    st.set_page_config(page_title="학원 관리 시스템", layout="wide")
    page = st.session_state.get("page", "login")

    if page == "login":
        st.title("로그인")
        password = st.text_input("비밀번호를 입력하세요", type="password")
        if st.button("로그인"):
            users = load_json(USERS_FILE)
            found = False
            for username, info in users.items():
                if info["password"] == password:
                    st.session_state["username"] = username
                    st.session_state["role"] = info["role"]
                    found = True
                    go("main")
                    break
            if not found:
                st.error("비밀번호가 틀렸습니다.")

    elif page == "main":
        st.title(f"{st.session_state['username']}님 환영합니다 ✨")
        role = st.session_state.get("role")

        menu = []
        if role in ["원장", "실장"]:
            menu = ["현황보고", "사용자관리", "학생관리", "학생정보", "시험입력", "학생시간표출력", "강사시간표출력"]
        elif role == "팀장":
            menu = ["학생관리", "학생정보", "시험입력", "학생시간표출력", "강사시간표출력"]
        elif role == "조교":
            menu = ["학생관리", "시험입력", "학생시간표출력"]
        elif role == "강사":
            menu = ["시험입력", "학생시간표출력"]

        choice = st.sidebar.selectbox("메뉴", menu)

        if choice == "학생관리":
            student_management()

# 학생 관리 페이지
def student_management():
    st.subheader("📚 학생 관리")
    data = load_json(STUDENTS_FILE)

    level = st.selectbox("학교급 선택", ["초등", "중등", "고등"])

    school_options = {
        "초등": ["배봉초", "전농초", "전동초", "휘봉초", "삼육초", "청량초"],
        "중등": ["휘경여중", "전동중", "전일중", "전농중", "동대문중", "장평중", "경희중", "경희여중"],
        "고등": ["휘경여고", "해성여고", "동대부고", "휘봉고", "경희고", "경희여고", "대광고", "한대부고", "혜원여고", "중화고", "석관고"]
    }

    grade_options = {
        "초등": ["초3", "초4", "초5", "초6"],
        "중등": ["중1", "중2", "중3"],
        "고등": ["고1", "고2", "고3"]
    }

    time_options = {
        "초등": ["월수금(3시~5시)", "화목(3시~6시)"],
        "중등": ["월수금(5시~7시30분)", "월수금(7시30분~10시)", "화목토(5시~7시30분)", "화목토(7시30분~10시)"],
        "고등": ["월수(5시~8시30분)", "월수(6시30분~10시)", "화목(5시~8시30분)", "화목(6시30분~10시)"]
    }

    subject_options = {
        "초등": ["초3-1", "초3-2", "초4-1", "초4-2", "초5-1", "초5-2", "초6-1", "초6-2"],
        "중등": ["중1-1", "중1-2", "중2-1", "중2-2", "중3-1", "중3-2"],
        "고등": ["공통수학1", "공통수학2", "대수", "미적분1", "미적분2", "확률과 통계", "기하", "수학1", "수학2", "미적분"]
    }

    with st.form("학생 추가"):
        name = st.text_input("이름")
        school = st.selectbox("학교 선택", school_options[level])
        grade = st.selectbox("학년 선택", grade_options[level])
        class_name = st.text_input("반명")
        homeroom_teacher = st.text_input("담임")
        class_time = st.selectbox("수업시간 선택", time_options[level])
        study_courses = st.multiselect("수업 과목 선택", subject_options[level])
        submitted = st.form_submit_button("학생 추가")

        if submitted and name and class_name and homeroom_teacher and class_time and study_courses:
            student = {
                "이름": name,
                "구분": level,
                "학교": school,
                "학년": grade,
                "반명": class_name,
                "담임": homeroom_teacher,
                "수업시간": class_time,
                "학습과정": ", ".join(study_courses)
            }

            # 저장 로직
            if school not in data:
                data[school] = {}
            if grade not in data[school]:
                data[school][grade] = {}
            if class_name not in data[school][grade]:
                data[school][grade][class_name] = []

            data[school][grade][class_name].append(student)
            save_json(data, STUDENTS_FILE)
            st.success("학생이 추가되었습니다!")

    if data:
        st.write("## 현재 등록된 학생")
        st.json(data)

if __name__ == "__main__":
    main()
