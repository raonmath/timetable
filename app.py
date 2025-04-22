
import streamlit as st
import pandas as pd
from datetime import date
from collections import defaultdict

# ===== 사용자 설정 =====
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

# ===== 초기화 =====
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.page = "login"
    st.session_state.exam_subjects = ["시험기간", "수학"]
    st.session_state.exam_data = defaultdict(lambda: defaultdict(dict))

# ===== 페이지 제어 =====
def go(page):
    st.session_state.page = page
    st.experimental_rerun()

# ===== 로그인 =====
if st.session_state.page == "login":
    st.title("🔐 로그인")
    pw = st.text_input("비밀번호를 입력하세요", type="password", key="pw")
    if st.button("확인"):
        user = PASSWORDS.get(pw)
        if user:
            st.session_state.authenticated = True
            st.session_state.username = user["name"]
            st.session_state.role = user["role"]
            go("home")
        else:
            st.error("비밀번호가 올바르지 않습니다.")

# ===== 홈 =====
elif st.session_state.page == "home":
    st.markdown(f"## 👋 {st.session_state.username} 안녕하세요. ({st.session_state.role})")
    col1, col2 = st.columns(2)
    if col1.button("📋 시험정보입력"):
        go("exam_input")
    if col2.button("🧠 시험지출력"):
        st.info("시험지출력은 다음 단계에서 제공됩니다.")

# ===== 시험정보입력 =====
elif st.session_state.page == "exam_input":
    st.title("📋 시험정보 입력")

    new_subject = st.text_input("➕ 시험과목 추가 (예: 국어, 영어)", key="new_subject")
    if st.button("과목추가"):
        s = new_subject.strip()
        if s and s not in st.session_state.exam_subjects:
            st.session_state.exam_subjects.append(s)
            st.experimental_rerun()

    my_classes = ["중3A반", "고2B반"]
    school_map = defaultdict(lambda: defaultdict(list))
    for s in students:
        if s["반"] in my_classes:
            school_map[s["학교"]][s["반"]].append(s["이름"])

    for school, class_map in sorted(school_map.items()):
        st.markdown(f"### 🏫 {school}")
        table = {"시험항목": []}
        for cls in class_map:
            table[cls] = []
        for subject in st.session_state.exam_subjects:
            table["시험항목"].append(subject)
            for cls in class_map:
                names = class_map[cls]
                key = f"{school}_{cls}_{subject}"
                if subject == "시험기간":
                    col1, col2 = st.columns(2)
                    start = col1.date_input(f"{cls} 시작일", key=key+"_start", value=date.today())
                    end = col2.date_input(f"{cls} 종료일", key=key+"_end", value=date.today())
                    st.session_state.exam_data[school][cls][subject] = (start, end)
                    cell = f"{start.strftime('%Y-%m-%d (%a)')} ~ {end.strftime('%Y-%m-%d (%a)')}"
                else:
                    d = st.date_input(f"{cls} {subject} 시험일", key=key, value=date.today())
                    st.session_state.exam_data[school][cls][subject] = d
                    cell = d.strftime("%Y-%m-%d (%a)")
                table[cls].append(cell)

        df = pd.DataFrame(table)
        st.dataframe(df, use_container_width=True)

    if st.button("← 돌아가기"):
        go("home")
    if st.button("✅ 저장"):
        st.success("시험정보가 저장되었습니다.")
        st.json(st.session_state.exam_data)
