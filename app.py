import streamlit as st
import pandas as pd
import json
import os
from datetime import date
from openpyxl import Workbook
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# 파일 경로
STUDENTS_FILE = "data/students.json"
EXAM_DATES_FILE = "data/exam_dates.json"
USERS_FILE = "data/users.json"

# 디렉토리 생성 함수
def ensure_directory(file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

# JSON 파일 로드/저장 함수
def load_json(file_path):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(data, file_path):
    ensure_directory(file_path)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 페이지 이동 함수
def go(page):
    st.session_state["page"] = page
    st.experimental_rerun()

# 날짜 형식 변환
def format_date_with_day(d):
    return d.strftime("%m-%d(%a)")

# 학생 저장
def save_student(student):
    data = load_json(STUDENTS_FILE)
    school, grade, class_ = student["학교"], student["학년"], student["반명"]
    data.setdefault(school, {}).setdefault(grade, {}).setdefault(class_, []).append(student)
    save_json(data, STUDENTS_FILE)

# 삭제 함수
def delete_student(student_name):
    data = load_json(STUDENTS_FILE)
    for school in data:
        for grade in data[school]:
            for class_ in data[school][grade]:
                data[school][grade][class_] = [s for s in data[school][grade][class_] if s["이름"] != student_name]
    save_json(data, STUDENTS_FILE)

def delete_all_students():
    save_json({}, STUDENTS_FILE)

def main():
    st.set_page_config(page_title="학생 관리 시스템")

    if "page" not in st.session_state:
        st.session_state["page"] = "login"

    if st.session_state["page"] == "login":
        st.title("🔐 로그인")
        password = st.text_input("비밀번호 입력", type="password")
        if st.button("로그인"):
            users = load_json(USERS_FILE)
            if password in users:
                st.session_state["username"] = users[password]["이름"]
                st.session_state["role"] = users[password]["role"]
                go("main")
            else:
                st.error("비밀번호가 일치하지 않습니다.")

    elif st.session_state["page"] == "main":
        st.title("📚 학생 관리 시스템")
        role = st.session_state.get("role")
        if role:
            if role in ["원장", "실장", "조교", "강사"]:
                if st.button("학생 관리"):
                    go("student_manage")
                if st.button("시험 입력"):
                    go("exam_input")

    elif st.session_state["page"] == "student_manage":
        st.subheader("🧑‍🎓 학생 관리")
        data = load_json(STUDENTS_FILE)
        flat_data = []
        for school in data:
            for grade in data[school]:
                for class_ in data[school][grade]:
                    for student in data[school][grade][class_]:
                        flat_data.append(student)

        df = pd.DataFrame(flat_data)
        AgGrid(df)

        if st.button("전체 삭제"):
            if st.confirm("정말 삭제하시겠습니까?"):
                delete_all_students()
                st.success("전체 삭제 완료")
                st.experimental_rerun()

        if st.button("이전 단계로"):
            go("main")

    elif st.session_state["page"] == "exam_input":
        st.subheader("📘 시험입력")
        exam_data = load_json(EXAM_DATES_FILE)
        data = load_json(STUDENTS_FILE)

        df = []
        for school in data:
            for grade in data[school]:
                for class_ in data[school][grade]:
                    names = [s["이름"] for s in data[school][grade][class_]]
                    df.append({
                        "학교명": school, "학년": grade, "반명": class_, "학생명단": ", ".join(names)
                    })

        df = pd.DataFrame(df)
        AgGrid(df)

        if st.button("이전 단계로"):
            go("main")

if __name__ == "__main__":
    main()
