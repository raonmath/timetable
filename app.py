# app.py (UI 향상 + 권한 기반 메뉴 + 학생관리 리디자인)
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from io import BytesIO
from openpyxl import Workbook
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# 파일 경로 상수
STUDENTS_FILE = "data/students.json"
USERS_FILE = "data/users.json"
EXCEL_TEMPLATE_PATH = "data/student_template.xlsx"

# JSON 로드 & 저장

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 로그인 함수

def login():
    st.session_state.page = "login"
    st.title("🔒 로그인")
    password = st.text_input("비밀번호", type="password")
    users = load_json(USERS_FILE)
    if st.button("로그인"):
        for user, info in users.items():
            if info["password"] == password:
                st.session_state.username = user
                st.session_state.role = info["role"]
                st.session_state.page = "main"
                st.experimental_rerun()
        st.error("비밀번호가 틀렸습니다.")

# 메뉴 구성

def sidebar_menu():
    st.sidebar.markdown("### 📋 메뉴")
    pages = {
        "학생관리": ["원장", "실장", "팀장", "조교"],
        "시험입력": ["원장", "실장", "팀장", "강사", "조교"],
        "사용자관리": ["원장", "실장"]
    }
    for label, roles in pages.items():
        if st.session_state.role in roles:
            if st.sidebar.button(label):
                st.session_state.page = label
                st.experimental_rerun()
    st.sidebar.markdown("---")
    if st.sidebar.button("로그아웃"):
        st.session_state.clear()
        st.experimental_rerun()

# 학생관리

def student_management():
    st.title("👨🏻‍🎓 학생관리")
    levels = {"초등": ["배봉초", "전농초", "전동초", "휘봉초", "삼육초", "청량초"],
              "중등": ["휘경여중", "전동중", "전일중", "전농중", "동대문중", "장평중", "경희중", "경희여중"],
              "고등": ["휘경여고", "해성여고", "동대부고", "휘봉고", "경희고", "경희여고", "대광고", "한대부고", "혜원여고", "중화고", "석관고"]}

    grades = {"초등": ["초3", "초4", "초5", "초6"],
              "중등": ["중1", "중2", "중3"],
              "고등": ["고1", "고2", "고3"]}

    times = {"초등": ["월수금(3시~5시)", "화목(3시~6시)"],
             "중등": ["월수금(5시~7시30분)", "월수금(7시30분~10시)", "화목토(5시~7시30분)", "화목토(7시30분~10시)"],
             "고등": ["월수(5시~8시30분)", "월수(6시30분~10시)", "화목(5시~8시30분)", "화목(6시30분~10시)"]}

    subjects = {"초등": ["초3-1", "초3-2", "초4-1", "초4-2", "초5-1", "초5-2", "초6-1", "초6-2"],
                "중등": ["중1-1", "중1-2", "중2-1", "중2-2", "중3-1", "중3-2"],
                "고등": ["공통수학1", "공통수학2", "대수", "미적분1", "미적분2", "확률과 통계", "기하", "수학1", "수학2", "미적분"]}

    with st.form("학생추가"):
        col1, col2 = st.columns(2)
        name = col1.text_input("이름")
        level = col2.selectbox("구분", list(levels.keys()))
        col3, col4 = st.columns(2)
        school = col3.selectbox("학교", levels[level])
        grade = col4.selectbox("학년", grades[level])
        col5, col6 = st.columns(2)
        class_ = col5.text_input("반명")
        teacher = col6.text_input("담임")
        time = st.selectbox("수업시간", times[level])
        course = st.multiselect("수업과목", subjects[level])
        submitted = st.form_submit_button("저장")
        if submitted and name:
            student = {"이름": name, "구분": level, "학교": school, "학년": grade,
                       "반명": class_, "담임": teacher, "수업시간": time, "학습과정": ", ".join(course)}
            data = load_json(STUDENTS_FILE)
            if school not in data:
                data[school] = {}
            if grade not in data[school]:
                data[school][grade] = {}
            if class_ not in data[school][grade]:
                data[school][grade][class_] = []
            data[school][grade][class_].append(student)
            save_json(data, STUDENTS_FILE)
            st.success("저장되었습니다.")

    # 저장된 학생 표시 및 삭제
    all_students = []
    data = load_json(STUDENTS_FILE)
    for school in data:
        for grade in data[school]:
            for class_ in data[school][grade]:
                all_students.extend(data[school][grade][class_])

    st.markdown("---")
    st.markdown("### 현재 등록된 학생")
    df = pd.DataFrame(all_students)
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection("multiple", use_checkbox=True)
    grid = AgGrid(df, gridOptions=gb.build(), update_mode=GridUpdateMode.SELECTION_CHANGED)
    selected = grid["selected_rows"]

    col_del1, col_del2 = st.columns(2)
    if col_del1.button("선택삭제") and selected:
        for s in selected:
            delete_student_by_name(s["이름"])
        st.success("선택된 학생 삭제 완료")
        st.experimental_rerun()
    if col_del2.button("전체삭제"):
        save_json({}, STUDENTS_FILE)
        st.success("전체 삭제 완료")
        st.experimental_rerun()

    st.download_button(
        label="엑셀 양식 다운로드",
        data=create_excel_template(),
        file_name="학생등록양식.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    uploaded = st.file_uploader("엑셀 업로드", type="xlsx")
    if uploaded:
        df_new = pd.read_excel(uploaded)
        for _, row in df_new.iterrows():
            save_student(row.to_dict())
        st.success("엑셀에서 학생정보 등록 완료")
        st.experimental_rerun()

def delete_student_by_name(name):
    data = load_json(STUDENTS_FILE)
    for school in list(data.keys()):
        for grade in list(data[school].keys()):
            for class_ in list(data[school][grade].keys()):
                data[school][grade][class_] = [s for s in data[school][grade][class_] if s["이름"] != name]
    save_json(data, STUDENTS_FILE)

def save_student(student):
    school, grade, class_ = student["학교"], student["학년"], student["반명"]
    data = load_json(STUDENTS_FILE)
    if school not in data:
        data[school] = {}
    if grade not in data[school]:
        data[school][grade] = {}
    if class_ not in data[school][grade]:
        data[school][grade][class_] = []
    data[school][grade][class_].append(student)
    save_json(data, STUDENTS_FILE)

def create_excel_template():
    df = pd.DataFrame(columns=["이름", "구분", "학교", "학년", "반명", "담임", "수업시간", "학습과정"])
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# 메인 실행

def main():
    if "page" not in st.session_state:
        st.session_state.page = "login"
    if st.session_state.page == "login":
        login()
        return

    sidebar_menu()

    page = st.session_state.page
    if page == "main":
        st.title("📚 학생 관리 시스템")
        st.write(f"안녕하세요, {st.session_state.username}님 ({st.session_state.role})")
    elif page == "학생관리":
        student_management()

if __name__ == "__main__":
    main()
