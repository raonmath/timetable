# 전체 app.py (수정본)

import streamlit as st
import pandas as pd
import json
import os
from datetime import date
from openpyxl import Workbook
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

STUDENTS_FILE = "data/students.json"
EXAM_FILE = "data/exam_dates.json"

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

def main():
    st.set_page_config(layout="wide")
    page = st.session_state.get("page", "main")

    if page == "main":
        st.title("📋 시간표 관리 시스템")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👩‍🎓 학생 관리"):
                go("student")
        with col2:
            if st.button("📘 시험 입력"):
                go("exam_input")

    elif page == "student":
        st.subheader("👩‍🎓 학생 등록 및 조회")
        with st.form("학생 등록"):
            name = st.text_input("이름")
            level = st.selectbox("구분", ["중등", "고등"])
            school = st.text_input("학교")
            grade = st.text_input("학년")
            class_name = st.text_input("반명")
            teacher = st.text_input("담임")
            study_time = st.text_input("수업시간")
            course = st.text_input("학습과정")
            submitted = st.form_submit_button("학생 추가")
            if submitted:
                if name:
                    student = {
                        "이름": name,
                        "구분": level,
                        "학교": school,
                        "학년": grade,
                        "반명": class_name,
                        "담임": teacher,
                        "수업시간": study_time,
                        "학습과정": course
                    }
                    data = load_json(STUDENTS_FILE)
                    if school not in data:
                        data[school] = {}
                    if grade not in data[school]:
                        data[school][grade] = {}
                    if class_name not in data[school][grade]:
                        data[school][grade][class_name] = []
                    data[school][grade][class_name].append(student)
                    save_json(data, STUDENTS_FILE)
                    st.success("학생이 추가되었습니다.")

        data = load_json(STUDENTS_FILE)
        if data:
            for school in data:
                st.markdown(f"### 🏫 {school}")
                for grade in data[school]:
                    for class_name in data[school][grade]:
                        st.markdown(f"#### {grade} - {class_name}")
                        df = pd.DataFrame(data[school][grade][class_name])
                        grid = AgGrid(df)
                        names = [s["이름"] for s in data[school][grade][class_name]]
                        name_to_delete = st.selectbox(f"삭제할 학생 선택 ({grade}-{class_name})", [""] + names, key=f"{school}_{grade}_{class_name}")
                        if name_to_delete:
                            if st.button("삭제 확인", key=f"delete_{name_to_delete}_{school}"):
                                data[school][grade][class_name] = [s for s in data[school][grade][class_name] if s["이름"] != name_to_delete]
                                save_json(data, STUDENTS_FILE)
                                st.success(f"{name_to_delete} 학생이 삭제되었습니다.")
                                go("student")

        if st.button("전체 삭제"):
            if st.button("진짜 전체 삭제", key="really_delete"):
                save_json({}, STUDENTS_FILE)
                st.success("전체 학생 데이터가 삭제되었습니다.")

        if st.button("이전으로"):
            go("main")

    elif page == "exam_input":
        st.subheader("📘 시험입력")
        exam_data = load_json(EXAM_FILE)
        df_all = []
        data = load_json(STUDENTS_FILE)
        for school in data:
            for grade in data[school]:
                for class_name in data[school][grade]:
                    students = data[school][grade][class_name]
                    for s in students:
                        df_all.append({"학교": school, "반": class_name, "이름": s["이름"], "담임": s["담임"]})
        df = pd.DataFrame(df_all)
        df["학생수"] = 1
        df_summary = df.groupby(["학교", "반"]).agg({"이름": lambda x: ", ".join(x), "학생수": "sum"}).reset_index()
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
            "2학기 중간고사 시험기간", "2학기 기말고사 시험기간"])

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
                exam_data = load_json(EXAM_FILE)
                exam_data[school] = new_entry
                save_json(exam_data, EXAM_FILE)
                st.success("저장되었습니다.")
                go("exam_input")

        if st.button("이전단계로"):
            go("main")

if __name__ == "__main__":
    main()
