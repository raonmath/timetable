import streamlit as st
import pandas as pd
import json
import os
from datetime import date
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# 파일 경로
DATA_DIR = "data"
STUDENTS_FILE = os.path.join(DATA_DIR, "students.json")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

# 디렉토리 확인 및 생성
def ensure_directory(file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

# JSON 파일 로드/저장
def load_json(file_path):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(data, file_path):
    ensure_directory(file_path)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 로그인 함수
def login():
    users = load_json(USERS_FILE)
    st.title("🔐 로그인")
    password = st.text_input("비밀번호 입력", type="password")
    if st.button("로그인"):
        for username, info in users.items():
            if password == info.get("password"):
                st.session_state["username"] = username
                st.session_state["role"] = info.get("role")
                st.success(f"{username}님 환영합니다!")
                st.session_state["page"] = "main"
                st.experimental_rerun()
        st.error("비밀번호가 일치하지 않습니다.")

# 메인 페이지
def main_page():
    role = st.session_state.get("role")
    st.sidebar.title("📋 메뉴")

    menus = []
    if role in ["원장", "실장"]:
        menus = ["학생관리", "시험입력"]
    elif role == "팀장":
        menus = ["학생관리", "시험입력"]
    elif role == "강사":
        menus = ["시험입력"]
    elif role == "조교":
        menus = ["학생관리", "시험입력"]

    choice = st.sidebar.radio("메뉴를 선택하세요", menus)

    if choice == "학생관리":
        manage_students()
    elif choice == "시험입력":
        input_exam()

# 학생관리 함수
def manage_students():
    st.header("👩‍🎓 학생 관리")

    students = load_json(STUDENTS_FILE)

    with st.form("학생 등록"):        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("이름")
            level = st.selectbox("구분", ["초등", "중등", "고등"])
        with col2:
            school = st.selectbox("학교", get_schools(level))
            grade = st.selectbox("학년", get_grades(level))

        col3, col4 = st.columns(2)
        with col3:
            class_name = st.text_input("반명")
        with col4:
            teacher = st.text_input("담임")

        lesson_time = st.selectbox("수업시간", get_lesson_times(level))
        subjects = st.multiselect("수업과정", get_subjects(level))

        if st.form_submit_button("학생 저장"):
            new_student = {
                "이름": name,
                "구분": level,
                "학교": school,
                "학년": grade,
                "반명": class_name,
                "담임": teacher,
                "수업시간": lesson_time,
                "학습과정": ", ".join(subjects)
            }
            if school not in students:
                students[school] = {}
            if grade not in students[school]:
                students[school][grade] = {}
            if class_name not in students[school][grade]:
                students[school][grade][class_name] = []
            students[school][grade][class_name].append(new_student)
            save_json(students, STUDENTS_FILE)
            st.success("학생 정보가 저장되었습니다!")

    st.divider()
    st.subheader("현재 등록된 학생")

    if students:
        student_rows = []
        for school, grades in students.items():
            for grade, classes in grades.items():
                for class_name, student_list in classes.items():
                    for s in student_list:
                        student_rows.append({
                            "이름": s.get("이름"),
                            "학교": school,
                            "반명": class_name,
                            "담임": s.get("담임"),
                            "수업시간": s.get("수업시간")
                        })
        df = pd.DataFrame(student_rows)

        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_selection(selection_mode="multiple", use_checkbox=True)
        grid = AgGrid(df, gridOptions=gb.build(), update_mode=GridUpdateMode.SELECTION_CHANGED, height=300)

        col_del1, col_del2 = st.columns(2)
        with col_del1:
            if st.button("선택 삭제"):
                selected = grid["selected_rows"]
                if selected:
                    if st.confirm("선택한 학생을 삭제하시겠습니까?"):
                        for row in selected:
                            delete_student(row["이름"])
                        st.success("선택한 학생이 삭제되었습니다.")
                        st.experimental_rerun()
        with col_del2:
            if st.button("전체 삭제"):
                if st.confirm("정말 전체 삭제하시겠습니까?"):
                    save_json({}, STUDENTS_FILE)
                    st.success("전체 학생 삭제 완료!")
                    st.experimental_rerun()
    else:
        st.info("등록된 학생이 없습니다.")

# 학생 삭제 함수
def delete_student(name):
    students = load_json(STUDENTS_FILE)
    for school in list(students.keys()):
        for grade in list(students[school].keys()):
            for class_name in list(students[school][grade].keys()):
                students[school][grade][class_name] = [s for s in students[school][grade][class_name] if s.get("이름") != name]
    save_json(students, STUDENTS_FILE)

# 시험입력 함수 (간단화)
def input_exam():
    st.header("📝 시험 입력 (준비중)")
    st.info("시험 입력 페이지는 곧 완성됩니다!")

# 학교/학년/수업시간/수업과정 가져오기 함수
def get_schools(level):
    data = {
        "초등": ["배봉초", "전농초", "전동초", "휘봉초", "삼육초", "청량초"],
        "중등": ["휘경여중", "전동중", "전일중", "전농중", "동대문중", "장평중", "경희중", "경희여중"],
        "고등": ["휘경여고", "해성여고", "동대부고", "휘봉고", "경희고", "경희여고", "대광고", "한대부고", "혜원여고", "중화고", "석관고"]
    }
    return data.get(level, [])

def get_grades(level):
    data = {
        "초등": ["초3", "초4", "초5", "초6"],
        "중등": ["중1", "중2", "중3"],
        "고등": ["고1", "고2", "고3"]
    }
    return data.get(level, [])

def get_lesson_times(level):
    data = {
        "초등": ["월수금(3시~5시)", "화목(3시~6시)"],
        "중등": ["월수금(5시~7시30분)", "월수금(7시30분~10시)", "화목토(5시~7시30분)", "화목토(7시30분~10시)"],
        "고등": ["월수(5시~8시30분)", "월수(6시30분~10시)", "화목(5시~8시30분)", "화목(6시30분~10시)"]
    }
    return data.get(level, [])

def get_subjects(level):
    data = {
        "초등": ["초3-1", "초3-2", "초4-1", "초4-2", "초5-1", "초5-2", "초6-1", "초6-2"],
        "중등": ["중1-1", "중1-2", "중2-1", "중2-2", "중3-1", "중3-2"],
        "고등": ["공통수학1", "공통수학2", "대수", "미적분1", "미적분2", "확률과 통계", "기하", "수학1", "수학2", "미적분"]
    }
    return data.get(level, [])

# 메인 함수
def main():
    if "username" not in st.session_state:
        login()
    else:
        main_page()

if __name__ == "__main__":
    main()
