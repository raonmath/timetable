
import streamlit as st
import pandas as pd
from datetime import date
from collections import defaultdict

# ===== 로그인 설정 =====
PASSWORDS = {
    "rt5222": {"name": "이윤로원장님", "role": "원장"},
    "rt1866": {"name": "이라온실장님", "role": "실장"},
    "rt0368": {"name": "김서진선생님", "role": "강사"},
    "rt0621": {"name": "류승연선생님", "role": "강사"},
    "rt7705": {"name": "임인섭선생님", "role": "강사"},
    "rt3137": {"name": "정주빈선생님", "role": "강사"},
    "rt7735": {"name": "조하현선생님", "role": "강사"},
    "rt0365": {"name": "유진서조교", "role": "조교"},
    "rt3080": {"name": "이예원조교", "role": "조교"},
}

students = [
    {"이름": "이라온", "학교": "경희고", "반": "중3A반"},
    {"이름": "김서연", "학교": "경희고", "반": "중3A반"},
    {"이름": "이준호", "학교": "경희고", "반": "고2B반"},
    {"이름": "박성민", "학교": "동대부고", "반": "중3A반"},
    {"이름": "이민호", "학교": "배봉초", "반": "중3A반"},
    {"이름": "김민지", "학교": "배봉초", "반": "중3A반"},
    {"이름": "홍길동", "학교": "배봉초", "반": "중3A반"},
    {"이름": "유진서", "학교": "배봉초", "반": "고2B반"},
    {"이름": "한민관", "학교": "배봉초", "반": "고2B반"},
]

# ===== 세션 초기화 =====
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.page = "login"
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.exam_subjects = ["시험기간", "수학"]
    st.session_state.exam_data = defaultdict(lambda: defaultdict(dict))

# ===== 로그인 =====
if st.session_state.page == "login":
    st.title("🔐 로그인")
    pw = st.text_input("비밀번호를 입력하세요", type="password")
    if st.button("확인") or st.session_state.get("login_submitted", False):
        st.session_state["login_submitted"] = True
        user = PASSWORDS.get(pw)
        if user:
            st.session_state.authenticated = True
            st.session_state.username = user["name"]
            st.session_state.role = user["role"]
            st.session_state.page = "home"
        else:
            st.error("비밀번호가 올바르지 않습니다.")

# ===== 홈 =====
if st.session_state.page == "home" and st.session_state.authenticated:
    st.markdown(f"## 👋 {st.session_state.username} 안녕하세요. ({st.session_state.role})")
    st.markdown("### 아래 메뉴를 선택하세요")
    col1, col2 = st.columns(2)
    if col1.button("📋 시험정보입력"):
        st.session_state.page = "exam_input"
    if col2.button("🧠 시험지출력"):
        st.info("시험지출력은 다음 버전에서 지원됩니다.")

# ===== 시험정보입력 페이지 =====
if st.session_state.page == "exam_input":
    st.title("📋 시험정보 입력")

    # 과목 추가
    new_subject = st.text_input("➕ 시험과목 추가 (예: 국어, 영어)", "")
    if st.button("과목추가") and new_subject.strip() != "":
        if new_subject not in st.session_state.exam_subjects:
            st.session_state.exam_subjects.append(new_subject)

    # 학생 데이터 그룹핑
    my_classes = ["중3A반", "고2B반"]  # 예시: 로그인된 사용자의 반
    school_map = defaultdict(lambda: defaultdict(list))
    for s in students:
        if s["반"] in my_classes:
            school_map[s["학교"]][s["반"]].append(s["이름"])

    for school, class_map in sorted(school_map.items()):
        st.markdown(f"### 🏫 {school}")
        table_data = {"시험항목": []}
        for class_name in class_map:
            student_list = class_map[class_name]
            display = ", ".join(student_list) + f" ({len(student_list)}명)"
            table_data[class_name] = [display] * len(st.session_state.exam_subjects)

        table_data["시험항목"] = st.session_state.exam_subjects
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True)

        # 시험일 입력
        for subject in st.session_state.exam_subjects:
            for cls in class_map:
                key = f"{school}_{cls}_{subject}"
                if subject == "시험기간":
                    col1, col2 = st.columns(2)
                    start = col1.date_input(f"{cls} 시작일", key=key+"_start", value=date.today())
                    end = col2.date_input(f"{cls} 종료일", key=key+"_end", value=date.today())
                    st.session_state.exam_data[school][cls][subject] = (start, end)
                else:
                    dt = st.date_input(f"{cls} {subject} 시험일", key=key, value=date.today())
                    st.session_state.exam_data[school][cls][subject] = dt

    if st.button("← 돌아가기"):
        st.session_state.page = "home"
    if st.button("✅ 저장"):
        st.success("시험정보가 저장되었습니다.")
        st.json(st.session_state.exam_data)
