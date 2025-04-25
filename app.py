import streamlit as st
import pandas as pd
import json
import os
from datetime import date
from openpyxl import Workbook
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

STUDENTS_FILE = "data/students.json"
EXAM_FILE = "data/exam_dates.json"

# 디렉토리 확인
def ensure_directory(file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

def load_json(file_path):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(data, file_path):
    ensure_directory(file_path)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def go(page):
    st.session_state["page"] = page
    st.experimental_rerun()

def save_student(student):
    data = load_json(STUDENTS_FILE)
    school = student["학교"]
    grade = student["학년"]
    class_ = student["반명"]
    if school not in data:
        data[school] = {}
    if grade not in data[school]:
        data[school][grade] = {}
    if class_ not in data[school][grade]:
        data[school][grade][class_] = []
    data[school][grade][class_].append(student)
    save_json(data, STUDENTS_FILE)

def delete_student(student_name):
    data = load_json(STUDENTS_FILE)
    for school in data:
        for grade in data[school]:
            for class_ in data[school][grade]:
                new_list = [s for s in data[school][grade][class_] if s["이름"] != student_name]
                if len(new_list) < len(data[school][grade][class_]):
                    data[school][grade][class_] = new_list
    save_json(data, STUDENTS_FILE)

def delete_all_students():
    save_json({}, STUDENTS_FILE)

def main():
    st.set_page_config(page_title="학생 시험 관리", layout="wide")
    if "page" not in st.session_state:
        st.session_state["page"] = "main"

    page = st.session_state["page"]

    if page == "main":
        st.title("📘 학생 시험 관리 시스템")
        st.button("학생 관리", on_click=lambda: go("students"))
        st.button("시험 입력", on_click=lambda: go("exam_input"))

    elif page == "students":
        st.subheader("👨‍🎓 학생 관리")
        data = load_json(STUDENTS_FILE)
        flat_data = []
        for school in data:
            for grade in data[school]:
                for class_ in data[school][grade]:
                    for student in data[school][grade][class_]:
                        flat_data.append(student)
        df = pd.DataFrame(flat_data)
        if not df.empty:
            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_selection("single")
            grid = AgGrid(df, gridOptions=gb.build(), update_mode=GridUpdateMode.SELECTION_CHANGED)
            if grid and grid['selected_rows']:
                selected_name = grid['selected_rows'][0]['이름']
                if st.button("선택 학생 삭제"):
                    delete_student(selected_name)
                    st.success(f"{selected_name} 학생 삭제됨")
                    go("students")
            if st.button("전체 삭제"):
                if st.confirm("정말 모든 학생 정보를 삭제하시겠습니까?"):
                    delete_all_students()
                    st.success("전체 학생 삭제 완료")
                    go("students")
        else:
            st.info("등록된 학생이 없습니다.")

        if st.button("이전 단계로"):
            go("main")

    elif page == "exam_input":
        st.subheader("📘 시험 입력")
        student_data = load_json(STUDENTS_FILE)
        exam_data = load_json(EXAM_FILE)
        schools = list(student_data.keys())
        for school in schools:
            for grade in student_data[school]:
                for class_ in student_data[school][grade]:
                    students = student_data[school][grade][class_]
                    student_names = ", ".join([s["이름"] for s in students])
                    saved = "🟢" if exam_data.get(school) else "🔴"
                    table_df = pd.DataFrame([{
                        "학교명": school,
                        "학년": grade,
                        "반명": class_,
                        "학생명단": student_names,
                        "저장됨": saved,
                        "입력": "시험정보입력"
                    }])
                    gb = GridOptionsBuilder.from_dataframe(table_df)
                    gb.configure_column("입력", editable=False, cellRenderer='AgGridClickableCellRenderer')
                    grid = AgGrid(table_df, gridOptions=gb.build(), update_mode=GridUpdateMode.SELECTION_CHANGED)
                    if grid and grid['selected_rows']:
                        st.session_state["selected_school"] = school
                        go("exam_detail")

        if st.button("이전 단계로"):
            go("main")

    elif page == "exam_detail":
        st.subheader("📘 시험 정보 입력")
        school = st.session_state.get("selected_school")
        if not school:
            st.error("학교가 선택되지 않았습니다.")
            go("exam_input")
            return

        st.markdown(f"#### {school} 시험 정보 입력")
        start_date = st.date_input("시험 시작일")
        end_date = st.date_input("시험 종료일")
        exam_title = st.selectbox("시험 구분", ["1학기 중간고사", "1학기 기말고사", "2학기 중간고사", "2학기 기말고사"])

        if start_date and end_date:
            weekdays = ["월", "화", "수", "목", "금", "토", "일"]
            start_week = weekdays[start_date.weekday()]
            end_week = weekdays[end_date.weekday()]
            period_text = f"{start_date.strftime('%m-%d')}({start_week}) ~ {end_date.strftime('%m-%d')}({end_week})"
            st.info(f"시험기간: {period_text}")

            subjects = {
                "중학교": ["국어", "수학", "영어", "과학", "사회"],
                "고등학교": ["국어", "수학", "영어", "물리", "화학", "생명과학", "지구과학", "한국사"]
            }
            school_level = "고등학교" if "고" in school else "중학교"
            selected_subjects = {}
            for d in pd.date_range(start=start_date, end=end_date):
                weekday = weekdays[d.weekday()]
                date_str = f"{d.strftime('%m-%d')}({weekday})"
                selected = st.multiselect(f"{date_str} 시험과목 선택", subjects[school_level], key=date_str)
                if selected:
                    selected_subjects[date_str] = selected

            if st.button("시험정보 저장"):
                new_entry = {
                    "시험기간": period_text,
                    "시험구분": exam_title,
                    "과목시험일정": selected_subjects
                }
                exam_data = load_json(EXAM_FILE)
                exam_data[school] = new_entry
                save_json(exam_data, EXAM_FILE)
                st.success("시험 정보가 저장되었습니다.")
                go("exam_input")

        if st.button("이전 단계로"):
            go("exam_input")

if __name__ == "__main__":
    main()
