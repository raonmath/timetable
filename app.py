# app.py (전체코드)
import streamlit as st
import pandas as pd
import json
import os
from datetime import date
from openpyxl import Workbook
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# 파일 경로
STUDENTS_FILE = "data/students.json"
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

# 로그인
def login():
    st.title("로그인")
    password = st.text_input("비밀번호를 입력하세요", type="password")
    users = load_json(USERS_FILE)
    if st.button("로그인"):
        for username, info in users.items():
            if info["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = info["role"]
                st.success(f"{username}님 환영합니다!")
                st.experimental_rerun()
        else:
            st.error("비밀번호가 틀렸습니다.")

# 학생 저장
def save_student(new_student):
    data = load_json(STUDENTS_FILE)
    school = new_student["학교"]
    grade = new_student["학년"]
    class_ = new_student["반명"]

    if school not in data:
        data[school] = {}
    if grade not in data[school]:
        data[school][grade] = {}
    if class_ not in data[school][grade]:
        data[school][grade][class_] = []

    data[school][grade][class_].append(new_student)
    save_json(data, STUDENTS_FILE)

# 학생 삭제
def delete_students(selected_students):
    data = load_json(STUDENTS_FILE)
    for sel in selected_students:
        for school in data:
            for grade in data[school]:
                for class_ in data[school][grade]:
                    data[school][grade][class_] = [s for s in data[school][grade][class_] if s["이름"] != sel]
    save_json(data, STUDENTS_FILE)

# 메인
school_levels = {
    "초등": ["배봉초", "전농초", "전동초", "휘봉초", "삼육초", "청량초"],
    "중등": ["휘경여중", "전동중", "전일중", "전농중", "동대문중", "장평중", "경희중", "경희여중"],
    "고등": ["휘경여고", "해성여고", "동대부고", "휘봉고", "경희고", "경희여고", "대광고", "한대부고", "혜원여고", "중화고", "석관고"]
}

school_times = {
    "초등": ["월수금(3시~5시)", "화목(3시~6시)"],
    "중등": ["월수금(5시~7시30분)", "월수금(7시30분~10시)", "화목토(5시~7시30분)", "화목토(7시30분~10시)"],
    "고등": ["월수(5시~8시30분)", "월수(6시30분~10시)", "화목(5시~8시30분)", "화목(6시30분~10시)"]
}

school_subjects = {
    "초등": ["초3-1", "초3-2", "초4-1", "초4-2", "초5-1", "초5-2", "초6-1", "초6-2"],
    "중등": ["중1-1", "중1-2", "중2-1", "중2-2", "중3-1", "중3-2"],
    "고등": ["공통수학1", "공통수학2", "대수", "미적분1", "미적분2", "확률과 통계", "기하", "수학1", "수학2", "미적분"]
}

def main_page():
    with st.sidebar:
        st.header("메뉴")
        menu = st.radio("이동하기", ("학생관리", "로그아웃"))

    if menu == "학생관리":
        student_management()
    elif menu == "로그아웃":
        for key in st.session_state.keys():
            del st.session_state[key]
        st.experimental_rerun()

def student_management():
    st.title("학생 관리")

    with st.form("학생등록"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("이름")
            level = st.selectbox("구분", ["초등", "중등", "고등"])
            school = st.selectbox("학교", school_levels[level])
        with col2:
            grade = st.selectbox("학년", ["초3", "초4", "초5", "초6"] if level=="초등" else ["중1", "중2", "중3"] if level=="중등" else ["고1", "고2", "고3"])
            class_name = st.text_input("반명")
            teacher = st.text_input("담임")
        time = st.selectbox("수업시간", school_times[level])
        subjects = st.multiselect("수업과목", school_subjects[level])

        submitted = st.form_submit_button("저장")
        if submitted:
            new_student = {"이름": name, "구분": level, "학교": school, "학년": grade, "반명": class_name, "담임": teacher, "수업시간": time, "학습과정": ", ".join(subjects)}
            save_student(new_student)
            st.success("학생이 저장되었습니다!")

    # 등록된 학생 보기
    data = load_json(STUDENTS_FILE)
    student_list = []
    for school in data:
        for grade in data[school]:
            for class_ in data[school][grade]:
                for student in data[school][grade][class_]:
                    student_list.append(student)

    df = pd.DataFrame(student_list)
    st.dataframe(df)

    selected_students = st.multiselect("삭제할 학생 선택", df["이름"] if not df.empty else [])

    if st.button("선택삭제"):
        if selected_students:
            if st.confirm("정말 삭제하시겠습니까?"):
                delete_students(selected_students)
                st.success("삭제되었습니다.")
                st.experimental_rerun()

    if st.button("전체삭제"):
        if st.confirm("전체 학생을 정말 삭제하시겠습니까?"):
            save_json({}, STUDENTS_FILE)
            st.success("전체 삭제되었습니다.")
            st.experimental_rerun()

if "logged_in" not in st.session_state:
    login()
else:
    main_page()
