
import streamlit as st
from datetime import date

# ======== 비밀번호 및 사용자 정보 ========
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

# ======== 세션 초기화 ========
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.menu = None
    st.session_state.students = []
    st.session_state.class_info = {}

# ======== 로그인 ========
if not st.session_state.authenticated:
    st.title("🔐 로그인")
    password = st.text_input("비밀번호를 입력하세요", type="password")
    if st.button("확인"):
        user = PASSWORDS.get(password)
        if user:
            st.session_state.authenticated = True
            st.session_state.username = user["name"]
            st.session_state.role = user["role"]
            st.session_state.menu = "home"
            st.success(f"✅ 로그인 성공! {user['name']} ({user['role']})")
            st.experimental_rerun()
        else:
            st.error("❌ 비밀번호가 틀렸습니다.")

# ======== 메인 화면 (권한별 버튼 제공) ========
elif st.session_state.menu == "home":
    st.markdown(f"## 👋 {st.session_state.username} 안녕하세요.")
    role = st.session_state.role
    col1, col2, col3 = st.columns(3)

    if role in ["원장", "실장"]:
        with col1:
            if st.button("📊 현황 보고", use_container_width=True):
                st.session_state.menu = "현황 보고"
        with col2:
            if st.button("📋 정보 입력", use_container_width=True):
                st.session_state.menu = "시험 정보 입력"
        with col3:
            st.markdown("""
            <style>
            div.stButton > button:nth-child(1) {
                background-color: #ff4b4b;
                color: white;
                height: 3em;
                font-size: 18px;
            }
            </style>
            """, unsafe_allow_html=True)
            if st.button("🧠 시간표 출력", use_container_width=True):
                st.session_state.menu = "시간표 출력"

    elif role in ["강사", "조교"]:
        with col1:
            if st.button("📋 정보 입력", use_container_width=True):
                st.session_state.menu = "시험 정보 입력"
        with col2:
            st.markdown("""
            <style>
            div.stButton > button:nth-child(1) {
                background-color: #ff4b4b;
                color: white;
                height: 3em;
                font-size: 18px;
            }
            </style>
            """, unsafe_allow_html=True)
            if st.button("🧠 시간표 출력", use_container_width=True):
                st.session_state.menu = "시간표 출력"

# ======== 시험 정보 입력 ========
elif st.session_state.menu == "시험 정보 입력":
    st.subheader("📋 시험 정보 입력")

    teacher_classes = {
        "김서진선생님": ["초6-A반", "중1-B반"],
        "류승연선생님": ["중1-A반"],
        "조하현선생님": ["중2-C반"],
        "이윤로원장님": ["전체 관리"],
        "이라온실장님": ["전체 관리"]
    }

    teacher_name = st.session_state.username
    classes = teacher_classes.get(teacher_name, ["담당 반 없음"])
    selected_class = st.selectbox("담당 반 선택", classes)
    school_name = st.text_input("🏫 학교명")
    exam_start = st.date_input("🗓️ 시험 시작일")
    exam_end = st.date_input("🗓️ 시험 종료일")
    math_exam_date = st.date_input("📘 수학 시험일")

    if st.button("시험 정보 저장"):
        st.session_state.class_info[selected_class] = {
            "학교명": school_name,
            "시험기간": f"{exam_start} ~ {exam_end}",
            "수학시험": math_exam_date
        }
        st.success(f"{selected_class}의 시험 정보를 저장했습니다.")

    if selected_class in st.session_state.class_info:
        st.write("📄 저장된 정보:")
        st.json(st.session_state.class_info[selected_class])

# ======== 학생 정보 등록 ========
elif st.session_state.menu == "시간표 출력":
    st.subheader("🧑‍🎓 학생 정보 등록")

    school_options = {
        "초등": ["배봉초", "전농초", "전동초", "휘봉초", "삼육초", "청량초"],
        "중등": ["휘경여중", "전동중", "전일중", "전농중", "동대문중", "장평중", "경희중", "경희여중"],
        "고등": ["휘경여고", "해성여고", "동대부고", "휘봉고", "경희고", "경희여고", "대광고", "한대부고", "혜원여고", "중화고", "석관고"]
    }

    grade_options = {
        "초등": ["초3", "초4", "초5", "초6"],
        "중등": ["중1", "중2", "중3"],
        "고등": ["고1", "고2", "고3"]
    }

    class_time_options = {
        "초등": ["월수금(3시~5시)", "화목(3시~6시)"],
        "중등": ["월수금(5시~7시30분)", "월수금(7시30분~10시)", "화목토(5시~7시30분)", "화목토(7시30분~10시)"],
        "고등": ["월수(5시~8시30분)", "월수(6시30분~10시)", "화목(5시~8시30분)", "화목(6시30분~10시)"]
    }

    subject_options = {
        "초등": ["초3-1","초3-2","초4-1","초4-2","초5-1","초5-2","초6-1","초6-2"],
        "중등": ["중1-1","중1-2","중2-1","중2-2","중3-1","중3-2"],
        "고등": ["공통수학1","공통수학2","대수","미적분1","미적분2","확률과 통계","기하","수학1","수학2","미적분"]
    }

    school_level = st.selectbox("학교급", ["초등", "중등", "고등"])
    school = st.selectbox("학교", school_options[school_level])
    grade = st.selectbox("학년", grade_options[school_level])
    class_name = st.text_input("반명 (예: A반)")
    homeroom_teacher = st.text_input("담임 선생님")
    class_time = st.selectbox("수업 시간", class_time_options[school_level])
    subjects = st.multiselect("수업 과목", subject_options[school_level])
    student_name = st.text_input("학생 이름")

    if st.button("학생 등록"):
        st.session_state.students.append({
            "이름": student_name,
            "학교급": school_level,
            "학교": school,
            "학년": grade,
            "반명": class_name,
            "담임": homeroom_teacher,
            "수업시간": class_time,
            "수업과목": subjects
        })
        st.success(f"{student_name} 학생 등록 완료!")

    if st.session_state.students:
        st.subheader("📋 등록된 학생 명단")
        st.table(st.session_state.students)

# ======== 현황 보고 ========
elif st.session_state.menu == "현황 보고":
    st.subheader("📊 전체 현황")
    st.write("시험 정보:", st.session_state.class_info)
    st.write("학생 명단:", st.session_state.students)
