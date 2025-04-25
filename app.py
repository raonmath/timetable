import streamlit as st
import pandas as pd
import json
import os
from datetime import date
from openpyxl import Workbook
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from io import BytesIO

# 파일 경로
STUDENTS_FILE = "data/students.json"
EXAM_DATES_FILE = "data/exam_dates.json"
USERS_FILE = "data/users.json"

# 디렉토리 생성
os.makedirs("data", exist_ok=True)

# JSON 파일 함수
def load_json(file_path):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 로그인 처리
def login():
    st.title("🛡️ 로그인")
    password = st.text_input("비밀번호 입력", type="password")
    if st.button("로그인"):
        users = load_json(USERS_FILE)
        for username, info in users.items():
            if info["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = info["role"]
                st.success(f"{username}님 환영합니다!")
                st.experimental_rerun()
        else:
            st.error("비밀번호가 올바르지 않습니다.")

# 학생 데이터 테이블 생성
def student_table():
    students = load_json(STUDENTS_FILE)
    rows = []
    for school, grades in students.items():
        for grade, classes in grades.items():
            for class_, student_list in classes.items():
                for student in student_list:
                    rows.append({
                        "이름": student["이름"],
                        "구분": student["구분"],
                        "학교": school,
                        "학년": grade,
                        "반명": class_,
                        "담임": student["담임"],
                        "수업시간": student["수업시간"],
                        "수업과정": student["학습과정"]
                    })
    return pd.DataFrame(rows)

# 엑셀 다운로드용 파일 생성
def create_excel_template():
    df = pd.DataFrame({
        "이름": [],
        "구분": [],
        "학교": [],
        "학년": [],
        "반명": [],
        "담임": [],
        "수업시간": [],
        "수업과정": []
    })
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# 메인 페이지
def main_page():
    st.sidebar.title("📋 메뉴")
    role = st.session_state.role

    menu_options = []
    if role in ["원장", "실장"]:
        menu_options = ["현황보고", "직원관리", "학생관리", "학생정보", "시험입력", "학생시간표출력", "강사시간표출력"]
    elif role == "팀장":
        menu_options = ["학생관리", "학생정보", "시험입력", "학생시간표출력", "강사시간표출력"]
    elif role == "조교":
        menu_options = ["학생관리", "시험입력", "학생시간표출력"]
    elif role == "강사":
        menu_options = ["시험입력", "학생시간표출력"]

    choice = st.sidebar.radio("선택하세요", menu_options)

    if choice == "학생관리":
        manage_students()
    elif choice == "시험입력":
        manage_exams()

# 학생 관리 페이지
def manage_students():
    st.title("👩‍🎓 학생 관리")
    
    with st.expander("학생 등록"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("이름")
            level = st.selectbox("구분", ["초등", "중등", "고등"])
            school = st.text_input("학교")
            grade = st.text_input("학년")
        with col2:
            class_name = st.text_input("반명")
            teacher = st.text_input("담임")
        time = st.text_input("수업시간")
        subjects = st.multiselect("수업과정", ["초3-1", "초3-2", "초4-1", "초4-2", "초5-1", "초5-2", "초6-1", "초6-2",
                                             "중1-1", "중1-2", "중2-1", "중2-2", "중3-1", "중3-2",
                                             "수학1", "수학2", "공통수학1", "공통수학2", "미적분1", "미적분2", "확률과 통계", "기하"])

        if st.button("저장"):
            if name and school and grade and class_name:
                students = load_json(STUDENTS_FILE)
                students.setdefault(school, {}).setdefault(grade, {}).setdefault(class_name, []).append({
                    "이름": name,
                    "구분": level,
                    "학교": school,
                    "학년": grade,
                    "반명": class_name,
                    "담임": teacher,
                    "수업시간": time,
                    "학습과정": ", ".join(subjects)
                })
                save_json(students, STUDENTS_FILE)
                st.success("학생이 저장되었습니다.")
                st.experimental_rerun()
            else:
                st.warning("필수 항목을 모두 입력하세요.")

    st.divider()
    st.subheader("현재 등록된 학생")
    df = student_table()
    grid = AgGrid(df, update_mode=GridUpdateMode.SELECTION_CHANGED)

    selected = grid['selected_rows']
    if selected:
        if st.button("선택 삭제"):
            students = load_json(STUDENTS_FILE)
            for sel in selected:
                for grade in students.get(sel['학교'], {}):
                    for class_ in students[sel['학교']][grade]:
                        students[sel['학교']][grade][class_] = [s for s in students[sel['학교']][grade][class_] if s['이름'] != sel['이름']]
            save_json(students, STUDENTS_FILE)
            st.success("삭제되었습니다.")
            st.experimental_rerun()

    if st.button("전체 삭제"):
        if st.confirm("정말 전체 삭제하시겠습니까?"):
            save_json({}, STUDENTS_FILE)
            st.success("전체 삭제 완료")
            st.experimental_rerun()

    st.download_button(
        label="엑셀 양식 다운로드",
        data=create_excel_template(),
        file_name="학생등록양식.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# 시험 관리 페이지
def manage_exams():
    st.title("📝 시험 입력")
    st.write("준비 중... (추가 예정)")

# 메인 실행
def main():
    if "logged_in" not in st.session_state:
        login()
    elif st.session_state.logged_in:
        main_page()

if __name__ == "__main__":
    main()
