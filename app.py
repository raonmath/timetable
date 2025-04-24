# app.py (1/2)
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

# 날짜 요일 텍스트 변환 함수
def format_date_with_day(d):
    return d.strftime("%m-%d(%a)")

# 학생 저장 함수
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

# 삭제 함수
def delete_student(student_name):
    data = load_json(STUDENTS_FILE)
    for school in data:
        for grade in data[school]:
            for class_ in data[school][grade]:
                new_list = [s for s in data[school][grade][class_] if s["이름"] != student_name]
                if len(new_list) < len(data[school][grade][class_]):
                    data[school][grade][class_] = new_list
    save_json(data, STUDENTS_FILE)

# 전체 삭제
def delete_all_students():
    save_json({}, STUDENTS_FILE)

        if page == "exam_input":
            st.subheader("📘 시험입력")
            if "username" not in st.session_state or st.session_state["role"] not in ["원장", "실장", "조교", "강사"]:
                st.warning("접근 권한이 없습니다.")
                go("main")
                st.stop()

            exam_data = load_json_data(EXAM_FILE)
            teacher_name = st.session_state["username"]
            role = st.session_state["role"]

            # 담당 학교 및 반 확인
            df = pd.read_json(STUDENT_FILE)
            if role == "강사":
                df = df[df["담임"] == teacher_name]
            df["학생수"] = 1
            df_summary = df.groupby(["학교", "반"]).agg({"이름": lambda x: ", ".join(x), "학생수": "sum"}).reset_index()

            # 학교, 반별 테이블 구성
            schools = df_summary["학교"].unique()
            for school in schools:
                school_df = df_summary[df_summary["학교"] == school]
                table_data = []
                for _, row in school_df.iterrows():
                    반 = row["반"]
                    학생들 = row["이름"]
                    인원 = row["학생수"]
                    저장여부 = "🟢" if exam_data.get(school) else "🔴"
                    table_data.append({
                        "학교명": school,
                        "반명": 반,
                        "학생명단": f"{학생들} ({인원})",
                        "입력": "시험정보입력",
                        "저장됨": 저장여부
                    })
                table_df = pd.DataFrame(table_data)
                gb = GridOptionsBuilder.from_dataframe(table_df)
                gb.configure_column("입력", editable=False, cellRenderer='AgGridClickableCellRenderer')
                grid = AgGrid(table_df, gridOptions=gb.build(), update_mode=GridUpdateMode.SELECTION_CHANGED)
                if grid and grid['selected_rows']:
                    selected_school = grid['selected_rows'][0]['학교명']
                    selected_class = grid['selected_rows'][0]['반명']
                    st.session_state["selected_school"] = selected_school
                    st.session_state["selected_class"] = selected_class
                    go("exam_detail")

        elif page == "exam_detail":
            st.subheader("📘 시험 정보 입력")
            school = st.session_state.get("selected_school")
            if not school:
                st.error("학교가 선택되지 않았습니다.")
                go("exam_input")
                st.stop()

            st.markdown(f"#### {school} 시험 정보 입력")
            start_date = st.date_input("시험 시작일")
            end_date = st.date_input("시험 종료일")

            exam_title = st.selectbox("시험 구분", [
                "1학기 중간고사 시험기간", "1학기 기말고사 시험기간",
                "2학기 중간고사 시험기간", "2학기 기말고사 시험기간"
            ])

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
                dates_range = pd.date_range(start=start_date, end=end_date)
                selected_subjects = {}
                for d in dates_range:
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
                    exam_data = load_json_data(EXAM_FILE)
                    exam_data[school] = new_entry
                    save_json_data(EXAM_FILE, exam_data)
                    st.success("저장되었습니다.")
                    go("exam_input")

        if st.button("이전단계로"):
            go("main")


if __name__ == "__main__":
    main()
