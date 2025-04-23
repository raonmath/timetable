import streamlit as st
import pandas as pd
from datetime import date
from collections import defaultdict

# 사용자 인증 정보
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

# 학생 데이터
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

# 초기 세션 상태
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.page = "login"
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.exam_subjects = ["수학"]
    st.session_state.exam_data = defaultdict(lambda: defaultdict(dict))

# 화면 이동
def go(page):
    st.session_state.page = page
    st.experimental_rerun()

# 한글 요일
def get_kor_day(d):
    return ["월", "화", "수", "목", "금", "토", "일"][d.weekday()]

# 🔐 로그인
if st.session_state.page == "login":
    st.title("🔐 비밀번호 입력")
    pw = st.text_input("비밀번호", type="password")
    if st.button("확인"):
        user = PASSWORDS.get(pw)
        if user:
            st.session_state.authenticated = True
            st.session_state.username = user["name"]
            st.session_state.role = user["role"]
            go("home")
        else:
            st.error("비밀번호가 올바르지 않습니다.")

# 🏠 메인화면
elif st.session_state.page == "home":
    st.markdown(f"## 👋 {st.session_state.username}님 환영합니다. ({st.session_state.role})")
    st.markdown("### 메뉴를 선택하세요")
    col1, col2 = st.columns(2)
    if col1.button("📝 시험정보입력"):
        go("exam")
    if col2.button("📄 시험지출력"):
        st.info("시험지출 출력 기능은 다음에 준비됩니다.")

# 📝 시험정보입력
elif st.session_state.page == "exam":
    st.title("📝 시험정보 입력")

    # 과목추가 기능
    new_subject = st.text_input("➕ 시험과목 추가 (예: 국어, 영어)")
    if st.button("과목추가") and new_subject.strip() and new_subject not in st.session_state.exam_subjects:
        st.session_state.exam_subjects.append(new_subject.strip())
        st.experimental_rerun()

    # 담당 반 기준 필터링
    my_classes = ["중3A반", "고2B반"]
    school_map = defaultdict(lambda: defaultdict(list))
    for stu in students:
        if stu["반"] in my_classes:
            school_map[stu["학교"]][stu["반"]].append(stu["이름"])

    rows = []
    for school, class_map in sorted(school_map.items()):
        row = {"학교명": school}
        for cls in my_classes:
            names = class_map.get(cls, [])
            row[cls] = ", ".join(names) + f" ({len(names)}명)" if names else ""

        for subject in st.session_state.exam_subjects:
            for cls in my_classes:
                key = f"{school}_{cls}_{subject}"
                d = st.date_input(f"{school} {cls} {subject} 시험일", key=key, value=date.today())
                st.session_state.exam_data[school][cls][subject] = d

            subject_label = f"{subject}시험일"
            exam_day = st.session_state.exam_data[school][my_classes[0]].get(subject, None)
            if isinstance(exam_day, date):
                row[subject_label] = f"{exam_day.strftime('%m-%d')}({get_kor_day(exam_day)})"

        rows.append(row)

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)

    st.write("")
    if st.button("← 메인으로"):
        go("home")
    if st.button("✅ 저장"):
        st.success("시험정보가 저장되었습니다.")
        st.json(st.session_state.exam_data)
