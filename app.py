import streamlit as st
import pandas as pd
import json
import os
import io
from datetime import date
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from openpyxl import Workbook

# 파일 경로
STUDENT_FILE = "students.json"
SCHEDULE_FILE = "exam_schedule.json"

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

# 파일 불러오기
def load_students():
    if os.path.exists(STUDENT_FILE):
        with open(STUDENT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_students(data):
    with open(STUDENT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_schedule():
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_schedule(data):
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 세션 초기화
if "page" not in st.session_state:
    st.session_state.page = "login"
    st.session_state.user = ""
    st.session_state.role = ""
    st.session_state.students = load_students()
    st.session_state.schedule = load_schedule()
    st.session_state.confirm_delete = False

# 로그인
def login():
    pw = st.session_state.get("password_input", "")
    if pw in PASSWORDS:
        st.session_state.user = PASSWORDS[pw]["name"]
        st.session_state.role = PASSWORDS[pw]["role"]
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

# 원생입력 화면
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
            buffer = io.BytesIO()
            pd.DataFrame([{
                "이름": "예시학생", "구분": "중등", "학교": "전농중", "학년": "중2",
                "반명": "중2A", "담임": "김서진", "수업시간": "월수금(5시~7시30분)",
                "학습과정": "중2-1, 중2-2"
            }]).to_excel(buffer, index=False, engine="openpyxl")
            st.download_button("양식 다운로드", buffer.getvalue(), "원생입력양식.xlsx")

    if st.button("📋 원생정보확인"):
        df = pd.DataFrame(st.session_state.students)
        if not df.empty:
            st.dataframe(df)
            if not st.session_state.confirm_delete:
                if st.button("⚠️ 전체삭제"):
                    st.session_state.confirm_delete = True
            else:
                st.warning("정말 삭제하시겠습니까?")
                if st.button("Yes"):
                    st.session_state.students = []
                    save_students([])
                    st.session_state.confirm_delete = False
                    st.success("전체 삭제 완료되었습니다.")
                if st.button("No"):
                    st.session_state.confirm_delete = False
        else:
            st.info("저장된 원생이 없습니다.")

    if st.button("⬅️ 이전단계로"):
        st.session_state.page = "main"
        st.rerun()

# 시험입력 메인 화면
elif st.session_state.page == "exam_input":
    st.title("📝 시험입력")
    students = st.session_state.students
    schedule = st.session_state.schedule
    user = st.session_state.user
    role = st.session_state.role

    # 강사는 본인 담당 반만 필터링
    if role == "강사":
        students = [s for s in students if s["담임"] == user]

    df = pd.DataFrame(students)
    if df.empty:
        st.warning("입력된 학생 정보가 없습니다.")
    else:
        school_list = df["학교"].unique()
        display_data = []

        for school in school_list:
            sub_df = df[df["학교"] == school]
            row = {"학교명": school}
            for cls in sub_df["반명"].unique():
                names = sub_df[sub_df["반명"] == cls]["이름"].tolist()
                row[cls] = ", ".join(names) + f" ({len(names)}명)"
            row["시험기간"] = schedule.get(school, {}).get("시험기간", "")
            row["입력"] = "✅ 저장됨" if school in schedule else "시험입력"
            display_data.append(row)

        table_df = pd.DataFrame(display_data)
        gb = GridOptionsBuilder.from_dataframe(table_df)
        gb.configure_column("입력", editable=False, cellRenderer='AgGridCustomRenderer')
        grid = AgGrid(table_df, gridOptions=gb.build(), update_mode=GridUpdateMode.SELECTION_CHANGED)

        if grid and grid['selected_rows']:
            selected_school = grid['selected_rows'][0]['학교명']
            st.session_state.popup_school = selected_school
            st.session_state.page = "exam_popup"
            st.rerun()

    if st.button("⬅️ 이전단계로"):
        st.session_state.page = "main"
        st.rerun()

# 시험입력 팝업 입력 화면
elif st.session_state.page == "exam_popup":
    school = st.session_state.popup_school
    st.title(f"🏫 {school} - 시험정보입력")

    start_date = st.date_input("시험 시작일", value=date.today())
    end_date = st.date_input("시험 종료일", value=date.today())

    start_week = "월화수목금토일"[start_date.weekday()]
    end_week = "월화수목금토일"[end_date.weekday()]
    period_str = f"{start_date.strftime('%m-%d')}({start_week}) ~ {end_date.strftime('%m-%d')}({end_week})"

    st.subheader("🗓️ 날짜별 시험과목 입력")
    date_range = pd.date_range(start_date, end_date)
    level = next((s["구분"] for s in st.session_state.students if s["학교"] == school), "고등")
    subject_map = {
        "초등": ["초3-1", "초3-2", "초4-1", "초5-1", "초6-1"],
        "중등": ["중1-1", "중2-1", "중3-1"],
        "고등": ["수학1", "수학2", "미적분", "확률과 통계", "기하"]
    }
    subjects = subject_map.get(level, [])

    exam_schedule = {}
    for dt in date_range:
        week = "월화수목금토일"[dt.weekday()]
        st.markdown(f"**{dt.strftime('%m-%d')}({week})**")
        selected = st.multiselect(f"{dt}", subjects, key=f"{school}_{dt}")
        if selected:
            exam_schedule[dt.strftime('%m-%d') + f"({week})"] = selected

    if st.button("✅ 저장"):
        st.session_state.schedule[school] = {
            "시험기간": period_str,
            "일정": exam_schedule
        }
        save_schedule(st.session_state.schedule)
        st.success("저장되었습니다.")
        st.session_state.page = "exam_input"
        st.rerun()

    if st.button("⬅️ 이전으로"):
        st.session_state.page = "exam_input"
        st.rerun()

# 원생관리
elif st.session_state.page == "student_manage":
    st.title("📋 원생관리")

    df = pd.DataFrame(st.session_state.students)
    role = st.session_state.role
    user = st.session_state.user

    if df.empty:
        st.warning("등록된 학생이 없습니다.")
    else:
        if role == "강사":
            df = df[df["담임"] == user]

        level = st.selectbox("구분 선택", sorted(df["구분"].unique()))
        df = df[df["구분"] == level]

        teacher = st.selectbox("담임 선택", sorted(df["담임"].unique()))
        df = df[df["담임"] == teacher]

        classname = st.selectbox("반명 선택", sorted(df["반명"].unique()))
        df = df[df["반명"] == classname]

        student = st.selectbox("학생 선택", sorted(df["이름"].unique()))
        target = df[df["이름"] == student]

        if not target.empty:
            st.markdown("#### 저장된 정보:")
            st.write(target.iloc[0].to_dict())

            if st.button("❌ 삭제"):
                if "confirm_indiv" not in st.session_state:
                    st.session_state.confirm_indiv = True
                elif st.session_state.confirm_indiv:
                    st.session_state.students = [
                        s for s in st.session_state.students
                        if not (s["이름"] == student and s["반명"] == classname)
                    ]
                    save_students(st.session_state.students)
                    st.success("삭제 완료되었습니다.")
                    st.session_state.confirm_indiv = False
                    st.rerun()

            if st.session_state.get("confirm_indiv"):
                st.warning("정말 삭제하시겠습니까?")
                col_yes, col_no = st.columns(2)
                if col_yes.button("Yes"):
                    st.session_state.confirm_indiv = True
                if col_no.button("No"):
                    st.session_state.confirm_indiv = False

    if st.button("⬅️ 이전단계로"):
        st.session_state.page = "main"
        st.rerun()
