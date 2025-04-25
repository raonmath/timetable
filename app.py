import streamlit as st
import pandas as pd
import json
import os
from datetime import date
from openpyxl import Workbook
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# 파일 경로
STUDENTS_FILE = "data/students.json"
EXAM_FILE = "data/exam_dates.json"

# 디렉토리 확인 및 생성
def ensure_directory(file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

# JSON 로드 및 저장 함수
def load_json(file_path):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(data, file_path):
    ensure_directory(file_path)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 날짜 포맷
def format_date_with_day(d):
    return d.strftime("%m-%d(%a)")

# 저장 및 삭제 관련 함수들
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

# Streamlit 페이지 이동 기능
def go(page):
    st.session_state["page"] = page
    st.experimental_rerun()

# 메인 앱 함수
def main():
    if "page" not in st.session_state:
        st.session_state.page = "main"

    page = st.session_state.page

    if page == "main":
        st.title("📚 학생 관리 시스템")
        st.button("학생 관리", on_click=lambda: go("student_manage"))
        st.button("시험 입력", on_click=lambda: go("exam_input"))

    elif page == "student_manage":
        st.subheader("👨\u200d🎓 학생 관리")
        data = load_json(STUDENTS_FILE)
        student_list = []
        for school in data:
            for grade in data[school]:
                for class_ in data[school][grade]:
                    student_list.extend(data[school][grade][class_])

        df = pd.DataFrame(student_list)
        if not df.empty:
            grid = AgGrid(df, update_mode=GridUpdateMode.SELECTION_CHANGED)
            selected = grid["selected_rows"]
            if selected:
                name_to_delete = selected[0]["이름"]
                if st.button("선택 삭제"):
                    delete_student(name_to_delete)
                    st.success(f"{name_to_delete} 학생이 삭제되었습니다.")
                    st.experimental_rerun()
        else:
            st.info("등록된 학생이 없습니다.")

        if st.button("전체 삭제"):
            if st.confirm("정말 모든 학생을 삭제하시겠습니까?"):
                delete_all_students()
                st.success("전체 삭제 완료")
                st.experimental_rerun()

        st.button("이전 단계로", on_click=lambda: go("main"))

    elif page == "exam_input":
        st.subheader("📘 시험입력")
        data = load_json(STUDENTS_FILE)
        exam_data = load_json(EXAM_FILE)

        table_rows = []
        for school in data:
            for grade in data[school]:
                for class_ in data[school][grade]:
                    students = data[school][grade][class_]
                    names = [s["이름"] for s in students]
                    row = {
                        "학교명": school,
                        "학년": grade,
                        "반명": class_,
                        "학생명단": ", ".join(names),
                        "입력": "시험정보입력",
                        "저장됨": "🟢" if exam_data.get(school) else "🔴"
                    }
                    table_rows.append(row)

        df = pd.DataFrame(table_rows)
        grid = AgGrid(df, update_mode=GridUpdateMode.SELECTION_CHANGED)
        selected = grid["selected_rows"]

        if selected:
            selected_school = selected[0]["학교명"]
            st.session_state["selected_school"] = selected_school
            go("exam_detail")

        st.button("이전 단계로", on_click=lambda: go("main"))

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
        exam_title = st.selectbox("시험 구분", [
            "1학기 중간고사 시험기간", "1학기 기말고사 시험기간",
            "2학기 중간고사 시험기간", "2학기 기말고사 시험기간"])

        if start_date and end_date:
            weekdays = ["월", "화", "수", "목", "금", "토", "일"]
            period_text = f"{start_date.strftime('%m-%d')}({weekdays[start_date.weekday()]}) ~ {end_date.strftime('%m-%d')}({weekdays[end_date.weekday()]})"
            st.info(f"시험기간: {period_text}")

            subjects = {
                "중학교": ["국어", "수학", "영어", "과학", "사회"],
                "고등학교": ["국어", "수학", "영어", "물리", "화학", "생명과학", "지구과학", "한국사"]
            }
            level = "고등학교" if "고" in school else "중학교"
            dates_range = pd.date_range(start=start_date, end=end_date)
            selected_subjects = {}
            for d in dates_range:
                weekday = weekdays[d.weekday()]
                date_str = f"{d.strftime('%m-%d')}({weekday})"
                selected = st.multiselect(f"{date_str} 시험과목 선택", subjects[level], key=date_str)
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
                st.success("저장되었습니다.")
                go("exam_input")

        st.button("이전 단계로", on_click=lambda: go("exam_input"))

if __name__ == "__main__":
    main()
