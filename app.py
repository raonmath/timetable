
import streamlit as st
from datetime import date
from collections import defaultdict
import pandas as pd

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

# ===== 초기화 =====
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.page = "login"
    st.session_state.exam_schedule = {}
    st.session_state.custom_subjects = ["시험기간", "수학"]

# ===== 예시 학생 데이터 =====
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

my_classes = ["중3A반", "고2B반"]

# ===== 로그인 화면 =====
if not st.session_state.authenticated:
    st.title("🔐 로그인")
    with st.form("login_form", clear_on_submit=True):
        password = st.text_input("비밀번호를 입력하세요", type="password")
        submitted = st.form_submit_button("확인")
        if submitted:
            user = PASSWORDS.get(password)
            if user:
                st.session_state.authenticated = True
                st.session_state.username = user["name"]
                st.session_state.role = user["role"]
                st.session_state.page = "home"
            else:
                st.error("비밀번호가 틀렸습니다.")

# ===== 메인 화면 =====
elif st.session_state.page == "home":
    st.markdown(f"## 👋 {st.session_state.username} 안녕하세요. ({st.session_state.role})")
    st.markdown("#### 원하는 메뉴를 선택하세요.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 시험정보입력"):
            st.session_state.page = "시험정보입력"
    with col2:
        if st.button("🧠 시험지출력"):
            st.session_state.page = "시험지출력"

# ===== 요일 포함 날짜 포맷 =====
def format_date(d):
    return d.strftime("%Y-%m-%d (%a)")

# ===== 시험정보입력 화면 =====
elif st.session_state.page == "시험정보입력":
    st.title("📋 시험정보 입력")

    available_subjects = ["국어", "영어", "사회", "과학"]
    new_subjects = st.multiselect("시험일 추가 과목 선택", available_subjects)

    for sub in new_subjects:
        if sub not in st.session_state.custom_subjects:
            st.session_state.custom_subjects.append(sub)

    # 그룹핑
    school_data = defaultdict(lambda: defaultdict(list))
    for stu in students:
        if stu["반"] in my_classes:
            school_data[stu["학교"]][stu["반"]].append(stu["이름"])

    # 테이블 생성
    for school, class_map in sorted(school_data.items()):
        st.markdown(f"### 🏫 {school}")
        columns = list(class_map.keys())
        data = []

        for subject in st.session_state.custom_subjects:
            row = {"시험항목": subject}
            for cls in columns:
                names = class_map[cls]
                student_text = f"<span class='small-text'>{', '.join(names)} ({len(names)}명)</span>"
                key = f"{school}_{cls}_{subject}"
                if subject == "시험기간":
                    col1, col2 = st.columns(2)
                    start = col1.date_input(f"{cls} 시작일", key=key+"_start", value=date.today())
                    end = col2.date_input(f"{cls} 종료일", key=key+"_end", value=date.today())
                    row[cls] = f"{format_date(start)} ~ {format_date(end)}"
                    st.session_state.exam_schedule[key] = (start, end)
                else:
                    d = st.date_input(f"{cls} {subject} 시험일", key=key, value=date.today())
                    row[cls] = format_date(d)
                    st.session_state.exam_schedule[key] = d
            data.append(row)

        df = pd.DataFrame(data)
        st.markdown("<style> .small-text { font-size: 12px; color: gray; } </style>", unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)

    if st.button("← 돌아가기"):
        st.session_state.page = "home"
    if st.button("✅ 저장 완료"):
        st.success("시험정보가 저장되었습니다.")
        st.json(st.session_state.exam_schedule)

# ===== 시험지출력 화면 (단순 안내용) =====
elif st.session_state.page == "시험지출력":
    st.title("🧠 시험지출력")
    st.info("이 화면은 다음 단계에서 구현됩니다. 각 반별 학생 목록 및 출력 필터가 포함될 예정입니다.")
    if st.button("← 돌아가기"):
        st.session_state.page = "home"
