import streamlit as st
import pandas as pd
import json
import os
from datetime import date
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# 파일 경로
DATA_PATH = "students.json"
EXAM_PATH = "exam_dates.json"

# 비밀번호 목록
PASSWORDS = {
    "rt5222": {"name": "이윤로", "role": "원장"},
    "rt1866": {"name": "이라온", "role": "실장"},
    "rt0368": {"name": "김서진", "role": "강사"},
    "rt0621": {"name": "류승연", "role": "강사"},
    "rt7705": {"name": "임인섭", "role": "강사"},
    "rt3137": {"name": "정주빈", "role": "강사"},
    "rt7735": {"name": "조하현", "role": "강사"},
    "rt0365": {"name": "유진서", "role": "조교"},
    "rt3080": {"name": "이예원", "role": "조교"},
}

# 파일 로드/저장 함수
def load_students():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_students(data):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_exam_dates():
    if os.path.exists(EXAM_PATH):
        with open(EXAM_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_exam_dates(data):
    with open(EXAM_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 세션 초기화
if "page" not in st.session_state:
    st.session_state.page = "login"
    st.session_state.user = ""
    st.session_state.role = ""
    st.session_state.students = load_students()
    st.session_state.exam_subjects = ["수학시험일"]
    st.session_state.exam_dates = load_exam_dates()
    st.session_state.exam_title = "1학기 중간고사 시험기간"

# 로그인 함수
def login():
    pw = st.session_state.get("password_input", "")
    user = PASSWORDS.get(pw)
    if user:
        st.session_state.user = user["name"]
        st.session_state.role = user["role"]
        st.session_state.page = "main"
        st.rerun()
    else:
        st.error("비밀번호가 올바르지 않습니다.")

# 로그인 화면
if st.session_state.page == "login":
    st.title("🔐 라온 시간표 시스템")
    st.text_input("비밀번호를 입력하세요", type="password", key="password_input")
    if st.button("확인"):
        login()

# 메인 메뉴
elif st.session_state.page == "main":
    st.markdown(f"## 👋 {st.session_state.user}님 환영합니다.")
    role = st.session_state.role

    if role in ["원장", "실장"]:
        cols = st.columns(4)
        if cols[0].button("📊 현황보고"): pass
        if cols[1].button("👤 원생입력"):
            st.session_state.page = "student_input"
            st.rerun()
        if cols[2].button("📝 시험입력"):
            st.session_state.page = "exam_input"
            st.rerun()
        if cols[3].button("📋 원생관리"):
            st.session_state.page = "student_manage"
            st.rerun()
    elif role == "조교":
        cols = st.columns(3)
        if cols[0].button("👤 원생입력"):
            st.session_state.page = "student_input"
            st.rerun()
        if cols[1].button("📝 시험입력"):
            st.session_state.page = "exam_input"
            st.rerun()
        if cols[2].button("📋 원생관리"):
            st.session_state.page = "student_manage"
            st.rerun()
    elif role == "강사":
        cols = st.columns(2)
        if cols[0].button("📝 시험입력"):
            st.session_state.page = "exam_input"
            st.rerun()
        if cols[1].button("📋 원생관리"):
            st.session_state.page = "student_manage"
            st.rerun()

# 원생 입력
elif st.session_state.page == "student_input":
    st.title("👤 원생정보 입력")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("이름")
        level = st.radio("구분", ["초등", "중등", "고등"], horizontal=True)

        school_map = {
            "초등": sorted(["배봉초", "전농초", "전동초", "휘봉초", "삼육초", "청량초"]),
            "중등": sorted(["휘경여중", "전동중", "전일중", "전농중", "동대문중", "장평중", "경희중", "경희여중"]),
            "고등": sorted(["휘경여고", "해성여고", "동대부고", "휘봉고", "경희고", "경희여고", "대광고", "한대부고", "혜원여고", "중화고", "석관고"]),
        }
        grade_map = {
            "초등": ["초3", "초4", "초5", "초6"],
            "중등": ["중1", "중2", "중3"],
            "고등": ["고1", "고2", "고3"],
        }
        time_map = {
            "초등": ["월수금(3시~5시)", "화목(3시~6시)"],
            "중등": ["월수금(5시~7시30분)", "월수금(7시30분~10시)", "화목토(5시~7시30분)", "화목토(7시30분~10시)"],
            "고등": ["월수(5시~8시30분)", "월수(6시30분~10시)", "화목(5시~8시30분)", "화목(6시30분~10시)"]
        }
        subject_map = {
            "초등": sorted(["초3-1", "초3-2", "초4-1", "초4-2", "초5-1", "초5-2", "초6-1", "초6-2"]),
            "중등": sorted(["중1-1", "중1-2", "중2-1", "중2-2", "중3-1", "중3-2"]),
            "고등": sorted(["공통수학1", "공통수학2", "대수", "미적분1", "미적분2", "확률과 통계", "기하", "수학1", "수학2", "미적분"]),
        }

        school = st.selectbox("학교", school_map[level])
        grade = st.selectbox("학년", grade_map[level])
        classname = st.text_input("반명")
        homeroom = st.selectbox("담임", sorted([info["name"] for info in PASSWORDS.values()]))
        time = st.selectbox("수업시간", time_map[level])
        subjects = st.multiselect("학습과정", subject_map[level])

        if st.button("💾 저장"):
            new_student = {
                "이름": name, "구분": level, "학교": school, "학년": grade,
                "반명": classname, "담임": homeroom, "수업시간": time,
                "학습과정": ", ".join(subjects)
            }
            st.session_state.students = [
                s for s in st.session_state.students
                if not (s["이름"] == name and s["반명"] == classname)
            ]
            st.session_state.students.append(new_student)
            save_students(st.session_state.students)
            st.success("저장되었습니다.")

    with col2:
        st.subheader("📥 엑셀 업로드")
        file = st.file_uploader("xlsx 업로드", type="xlsx")
        if file:
            df = pd.read_excel(file)
            for _, row in df.iterrows():
                new = row.to_dict()
                if not any(s["이름"] == new["이름"] and s["반명"] == new["반명"] for s in st.session_state.students):
                    st.session_state.students.append(new)
            save_students(st.session_state.students)
            st.success("업로드 완료!")

        if st.button("📤 엑셀 양식 다운로드"):
            import io
            import openpyxl
            buffer = io.BytesIO()
            pd.DataFrame([{
                "이름": "예시학생", "구분": "중등", "학교": "전농중", "학년": "중2",
                "반명": "중2A", "담임": "김서진", "수업시간": "월수금(5시~7시30분)",
                "학습과정": "중2-1, 중2-2"
            }]).to_excel(buffer, index=False, engine="openpyxl")
            st.download_button("양식 다운로드", buffer.getvalue(), "원생입력양식.xlsx")

    if st.button("⬅️ 이전단계로"):
        st.session_state.page = "main"
        st.rerun()

# 시험입력 화면
elif st.session_state.page == "exam_input":
    st.title("📝 시험정보 입력")

    students = st.session_state.students
    user = st.session_state.user
    role = st.session_state.role

    if role == "강사":
        students = [s for s in students if s["담임"] == user]

    # 시험기간 종류 선택
    exam_titles = [
        "1학기 중간고사 시험기간", "1학기 기말고사 시험기간",
        "2학기 중간고사 시험기간", "2학기 기말고사 시험기간"
    ]
    st.session_state.exam_title = st.selectbox("시험기간 제목 선택", exam_titles)

    # 과목 추가
    new_subject = st.text_input("추가할 과목 입력 (예: 국어)", key="add_subject")
    if st.button("과목시험일 추가"):
        key = f"{new_subject.strip()}시험일"
        if key not in st.session_state.exam_subjects:
            st.session_state.exam_subjects.append(key)

    # 반별 정보 정리
    school_class_map = {}
    for s in students:
        school = s["학교"]
        cls = s["반명"]
        name = s["이름"]
        school_class_map.setdefault(school, {}).setdefault(cls, []).append(name)

    # 표 데이터 생성
    grid_rows = []
    for school, class_data in school_class_map.items():
        row = {"학교명": school}
        for cls, names in class_data.items():
            label = f"{', '.join(names)} ({len(names)}명)"
            row[cls] = label

        # 시험기간 입력값 추가
        for cls in class_data:
            key = f"{school}_{cls}_{st.session_state.exam_title}"
            val = st.session_state.exam_dates.get(key, "")
            row[f"{cls}_{st.session_state.exam_title}"] = val

            for subj in st.session_state.exam_subjects:
                key2 = f"{school}_{cls}_{subj}"
                val2 = st.session_state.exam_dates.get(key2, "")
                row[f"{cls}_{subj}"] = val2

        grid_rows.append(row)

    # 표 컬럼 설정
    columns = ["학교명"]
    all_classes = {cls for data in school_class_map.values() for cls in data}
    columns += sorted(all_classes)

    for cls in sorted(all_classes):
        columns.append(f"{cls}_{st.session_state.exam_title}")
        for subj in st.session_state.exam_subjects:
            columns.append(f"{cls}_{subj}")

    df = pd.DataFrame(grid_rows, columns=columns)

    # AgGrid 옵션 구성
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=True, wrapText=True, autoHeight=True)
    gb.configure_grid_options(domLayout='normal')
    grid_options = gb.build()

    # 표 출력
    st.markdown("### 📋 시험정보표")
    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        allow_unsafe_jscode=True,
        height=350,
        fit_columns_on_grid_load=True
    )

    updated_df = grid_response["data"]

    if st.button("✅ 시험정보 저장"):
        new_data = {}
        for _, row in updated_df.iterrows():
            school = row["학교명"]
            for col in row.index:
                if col == "학교명": continue
                if isinstance(row[col], str) and row[col].strip():
                    key = f"{school}_{col}"
                    new_data[key] = row[col]
        st.session_state.exam_dates.update(new_data)
        save_exam_dates(st.session_state.exam_dates)
        st.success("시험 일정이 저장되었습니다.")

    if st.button("⬅️ 이전단계로"):
        st.session_state.page = "main"
        st.rerun()
