import streamlit as st
import json
import os
from datetime import date

# ---------- 파일 경로 ----------
USER_FILE = "data/users.json"
STUDENT_FILE = "data/students.json"
EXAM_FILE = "data/exam_dates.json"

# ---------- 권한별 메뉴 ----------
ROLE_MENUS = {
    "원장": ["학생관리", "시험입력", "시간표출력", "현황보고", "사용자관리"],
    "실장": ["학생관리", "시험입력", "시간표출력", "현황보고"],
    "팀장": ["학생관리", "시험입력", "시간표출력"],
    "강사": ["시험입력", "시간표출력"],
    "조교": ["학생관리", "시험입력", "시간표출력"]
}

# ---------- 기본 유틸 ----------
def load_json(file_path, default):
    if not os.path.exists(file_path):
        return default
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return data if isinstance(data, type(default)) else default
        except:
            return default

def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ---------- 로그인 ----------
def login():
    st.title("👨‍🏫 라온 시간표 생성 시스템")
    password = st.text_input("비밀번호를 입력하세요", type="password")
    if st.button("로그인"):
        users = load_json(USER_FILE, {})
        for user_id, info in users.items():
            if info["password"] == password:
                st.session_state["logged_in"] = True
                st.session_state["role"] = info["role"]
                st.session_state["user"] = user_id
                st.experimental_rerun()
        st.warning("비밀번호가 틀렸습니다.")

# ---------- 사이드바 ----------
def sidebar_menu():
    st.sidebar.title("📚 메뉴")
    menu = ROLE_MENUS.get(st.session_state["role"], [])
    return st.sidebar.radio("이동", menu)

# ---------- 학생관리 ----------
def student_management():
    st.header("👨‍🎓 학생관리")

    with st.expander("📝 학생 등록"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("이름")
            role = st.selectbox("구분", ["학생", "강사", "조교"])
        with col2:
            school = st.text_input("학교") if role == "학생" else ""
            grade = st.selectbox("학년", ["1학년", "2학년", "3학년"], index=0) if role == "학생" else ""

        col3, col4 = st.columns(2)
        with col3:
            classname = st.text_input("반명")
            homeroom = st.selectbox("담임", ["김담임", "이담임", "박담임"])
        with col4:
            time = st.text_input("수업시간")
            course = st.text_input("수업과정")

        if st.button("저장"):
            if name:
                students = load_json(STUDENT_FILE, [])
                students.append({
                    "이름": name, "구분": role, "학교": school, "학년": grade,
                    "반명": classname, "담임": homeroom,
                    "수업시간": time, "수업과정": course
                })
                save_json(STUDENT_FILE, students)
                st.success("학생 정보가 저장되었습니다.")
                st.experimental_rerun()
            else:
                st.warning("이름은 필수 항목입니다.")

    st.divider()
    st.subheader("📋 현재 등록된 학생")

    students = load_json(STUDENT_FILE, [])
    selected = st.multiselect("삭제할 학생 선택", [s["이름"] for s in students])
    if st.button("선택삭제"):
        students = [s for s in students if s["이름"] not in selected]
        save_json(STUDENT_FILE, students)
        st.success("선택한 학생을 삭제했습니다.")
        st.experimental_rerun()
    if st.button("전체삭제"):
        if st.confirm("정말 모든 학생을 삭제하시겠습니까?"):
            save_json(STUDENT_FILE, [])
            st.success("모든 학생을 삭제했습니다.")
            st.experimental_rerun()

    if students:
        df = [{k: s.get(k, "") for k in ["이름", "학교", "반명", "담임", "수업시간"]} for s in students]
        st.dataframe(df, use_container_width=True)

# ---------- 시험입력 메인 ----------
def exam_main():
    st.header("📝 시험입력")

    st.markdown("### 📋 시험입력표")
    example_rows = [
        {"학교": "경희고", "반명": "고1B", "담당": "이라온, 김서연", "기간": "05-01~05-05", "수학일": "05-06"},
        {"학교": "배봉초", "반명": "초6A", "담당": "이민호, 김민지", "기간": "", "수학일": ""}
    ]

    for idx, row in enumerate(example_rows):
        with st.container():
            cols = st.columns([2, 2, 2, 2, 1])
            cols[0].write(f"🏫 **{row['학교']}**")
            cols[1].write(f"🏷️ **{row['반명']}**")
            cols[2].write(f"👤 {row['담당']}")
            cols[3].write(f"🗓️ {row['기간'] or '미입력'} / 📐 {row['수학일'] or '미입력'}")
            if cols[4].button("✏️", key=f"edit_{idx}"):
                st.session_state["editing_exam"] = row
                st.session_state["editing_index"] = idx
                st.session_state["exam_mode"] = "edit"

    if st.session_state.get("exam_mode") == "edit":
        exam_edit_form()
def exam_edit_form():
    st.markdown("### 🧾 시험 정보 입력")

    exam = st.session_state.get("editing_exam", {})
    school = exam.get("학교", "")
    class_name = exam.get("반명", "")
    st.info(f"📌 대상: {school} - {class_name}")

    exam_title = st.selectbox("시험명칭", ["1학기 중간고사", "1학기 기말고사", "2학기 중간고사", "2학기 기말고사"])
    period = st.date_input("시험기간 선택 (시작 ~ 종료)", value=(date.today(), date.today()))
    math_date = st.date_input("수학시험일 선택")

    st.markdown("#### 📆 다른 과목 시험일 추가")
    other_subjects = st.session_state.get("other_subjects", [])
    new_subject = st.text_input("과목명 입력")
    new_date = st.date_input("시험일 선택", key="other_date")
    if st.button("과목 추가"):
        if new_subject:
            other_subjects.append((new_subject, str(new_date)))
            st.session_state["other_subjects"] = other_subjects

    for subj, d in other_subjects:
        st.write(f"✅ {subj}: {d}")

    st.markdown("#### 📚 시험 범위")
    scope = st.text_area("단원명 입력")

    st.markdown("#### 📝 시험재료")
    textbook = st.text_input("교과서(출판사명)")
    subbook = st.text_input("부교재명")
    schoolprint = st.file_uploader("학교프린트 스캔파일", type=["pdf", "png", "jpg"], key="print")

    st.markdown("#### 📎 기출문제 업로드")
    previous_exam = st.file_uploader("기출문제 업로드", type=["pdf", "png", "jpg"], key="prev_exam")
    if previous_exam:
        st.success(f"업로드됨: {previous_exam.name}")
        st.download_button("다운로드", previous_exam.getvalue(), file_name=previous_exam.name)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 저장"):
            exam_data = load_json(EXAM_FILE, {})
            key_prefix = f"{school}_{class_name}_{exam_title}".replace(" ", "")

            exam_data[f"{key_prefix}_시험기간"] = f"{period[0].strftime('%m-%d')}~{period[1].strftime('%m-%d')}"
            exam_data[f"{key_prefix}_수학시험일"] = math_date.strftime("%m-%d")
            exam_data[f"{key_prefix}_시험범위"] = scope
            exam_data[f"{key_prefix}_교과서"] = textbook
            exam_data[f"{key_prefix}_부교재"] = subbook

            if "other_subjects" in st.session_state:
                for subj, d in st.session_state["other_subjects"]:
                    exam_data[f"{key_prefix}_{subj}시험일"] = d

            save_json(EXAM_FILE, exam_data)
            st.success("시험 정보가 저장되었습니다.")
            st.session_state["exam_mode"] = None
            st.session_state["other_subjects"] = []
    with col2:
        if st.button("↩️ 되돌아가기"):
            st.session_state["exam_mode"] = None
            st.session_state["other_subjects"] = []

# ---------- 앱 실행 ----------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
else:
    page = sidebar_menu()
    if page == "학생관리":
        student_management()
    elif page == "시험입력":
        exam_main()
    elif page == "시간표출력":
        st.header("📅 시간표출력 (준비중)")
    elif page == "현황보고":
        st.header("📊 현황보고 (준비중)")
    elif page == "사용자관리":
        st.header("🧑‍💻 사용자관리 (준비중)")
