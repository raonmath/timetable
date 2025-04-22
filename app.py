
import streamlit as st
from datetime import date

# ===== 사용자 정보 =====
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
    st.session_state.students = []
    st.session_state.class_info = {}
    st.session_state.class_list = {
        "초6-A반": "김서진선생님",
        "중1-B반": "김서진선생님",
        "중1-A반": "류승연선생님",
        "중2-C반": "조하현선생님"
    }

# ===== 스타일 =====
st.markdown("""
<style>
button {
    height: 3em;
    font-size: 16px !important;
    border-radius: 0.5em;
}
div.stButton > button {
    margin: 5px;
}
.menu-row {
    display: flex;
    gap: 1em;
    flex-wrap: wrap;
    margin-top: 2em;
}
.menu-row button {
    min-width: 200px;
    background-color: #f0f2f6;
    color: #333;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ===== 로그인 =====
if st.session_state.page == "login":
    st.title("🔐 로그인")
    with st.form("login_form", clear_on_submit=True):
        password = st.text_input("비밀번호", type="password")
        submitted = st.form_submit_button("확인")
        if submitted:
            user = PASSWORDS.get(password)
            if user:
                st.session_state.authenticated = True
                st.session_state.username = user["name"]
                st.session_state.role = user["role"]
                st.session_state.page = "home"
            else:
                st.error("❌ 비밀번호가 틀렸습니다.")

# ===== 홈 화면 =====
elif st.session_state.page == "home":
    st.markdown(f"## 👋 {st.session_state.username} 안녕하세요 ({st.session_state.role})")
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="menu-row">', unsafe_allow_html=True)

    def go(page_name):
        st.session_state.page = page_name

    role = st.session_state.role
    if role in ["원장", "실장", "조교"]:
        if st.button("📚 전체 반 목록 확인"):
            go("class_list")

    if role in ["강사"]:
        if st.button("📚 담당 반 목록 확인"):
            go("class_list")

    if role in ["원장", "실장"]:
        if st.button("👤 원생 정보 입력"):
            go("student_input")

    if st.button("📋 시험 정보 입력"):
        go("exam_info")

    if st.button("🧠 시간표 출력"):
        go("student_list")

    if role in ["원장", "실장"]:
        if st.button("📊 현황 보고"):
            go("status_report")

    st.markdown('</div>', unsafe_allow_html=True)

# ===== 페이지: 시험 정보 입력 =====
elif st.session_state.page == "exam_info":
    st.subheader("📋 시험 정보 입력")
    st.markdown("#### 🔙 이전 페이지로 돌아가기")
    if st.button("← 뒤로 가기"):
        st.session_state.page = "home"

    selected_class = st.selectbox("담당 반 선택", list(st.session_state.class_list.keys()))
    school = st.text_input("학교명")
    exam_start = st.date_input("시험 시작일")
    exam_end = st.date_input("시험 종료일")
    math_exam_date = st.date_input("수학 시험일")

    if st.button("시험 정보 저장"):
        st.session_state.class_info[selected_class] = {
            "학교명": school,
            "시험기간": f"{exam_start} ~ {exam_end}",
            "수학시험": math_exam_date
        }
        st.success(f"{selected_class} 반 시험 정보 저장됨")

# ===== 페이지: 학생 등록 (시간표 출력 메뉴) =====
elif st.session_state.page == "student_list":
    st.subheader("🧑‍🎓 학생 정보 등록")
    if st.button("← 뒤로 가기"):
        st.session_state.page = "home"

    school_levels = {
        "초등": ["배봉초", "전농초", "전동초", "휘봉초", "삼육초", "청량초"],
        "중등": ["휘경여중", "전동중", "전일중", "전농중", "동대문중", "장평중", "경희중", "경희여중"],
        "고등": ["휘경여고", "해성여고", "동대부고", "휘봉고", "경희고", "경희여고", "대광고", "한대부고", "혜원여고", "중화고", "석관고"]
    }

    level = st.selectbox("학교급", list(school_levels.keys()))
    school = st.selectbox("학교", school_levels[level])
    grade = st.selectbox("학년", ["초3", "초4", "초5", "초6", "중1", "중2", "중3", "고1", "고2", "고3"])
    class_name = st.text_input("반명")
    homeroom = st.text_input("담임")
    time = st.selectbox("수업시간", ["월수금(3시~5시)", "화목(3시~6시)", "월수금(5시~7시30분)", "화목토(7시30분~10시)"])
    subject = st.multiselect("수업과목", ["수학", "과학", "영어", "사회", "기타"])
    student_name = st.text_input("학생 이름")

    if st.button("등록"):
        st.session_state.students.append({
            "이름": student_name,
            "학교급": level,
            "학교": school,
            "학년": grade,
            "반": class_name,
            "담임": homeroom,
            "수업시간": time,
            "수업과목": subject
        })
        st.success(f"{student_name} 등록 완료")

    if st.session_state.students:
        st.write("등록된 학생 명단:")
        st.table(st.session_state.students)

# ===== 페이지: 반 목록 보기 =====
elif st.session_state.page == "class_list":
    st.subheader("📚 반 목록 보기")
    if st.button("← 뒤로 가기"):
        st.session_state.page = "home"

    role = st.session_state.role
    if role in ["강사"]:
        user_name = st.session_state.username
        filtered = {k: v for k, v in st.session_state.class_list.items() if v == user_name}
    else:
        filtered = st.session_state.class_list

    for classname, teacher in filtered.items():
        st.write(f"📘 {classname} ({teacher})")

# ===== 페이지: 원생정보 수기입력 =====
elif st.session_state.page == "student_input":
    st.subheader("👤 원생 정보 수기입력")
    if st.button("← 뒤로 가기"):
        st.session_state.page = "home"

    name = st.text_input("이름")
    school = st.text_input("학교")
    grade = st.text_input("학년")
    cls = st.text_input("반")
    time = st.text_input("수업 시간")
    subjects = st.text_input("수업 과목 (쉼표로 구분)")

    if st.button("정보 저장"):
        st.session_state.students.append({
            "이름": name,
            "학교": school,
            "학년": grade,
            "반": cls,
            "수업시간": time,
            "수업과목": subjects.split(",")
        })
        st.success(f"{name} 학생 정보가 저장되었습니다.")

# ===== 페이지: 현황 보고 =====
elif st.session_state.page == "status_report":
    st.subheader("📊 전체 현황")
    if st.button("← 뒤로 가기"):
        st.session_state.page = "home"

    st.write("시험 정보", st.session_state.class_info)
    st.write("학생 정보", st.session_state.students)
