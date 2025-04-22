
import streamlit as st

# ======== 비밀번호별 사용자 및 권한 정보 ========
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

# ======== 세션 상태 초기화 ========
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None

# ======== 로그인 단계 ========
if not st.session_state.authenticated:
    st.title("🔐 로그인")
    password_input = st.text_input("비밀번호를 입력하세요", type="password")
    if st.button("확인"):
        user_info = PASSWORDS.get(password_input)
        if user_info:
            st.session_state.authenticated = True
            st.session_state.username = user_info["name"]
            st.session_state.role = user_info["role"]
            st.success(f"✅ 로그인 성공! {st.session_state.username} ({st.session_state.role})")
        else:
            st.error("❌ 비밀번호가 틀렸습니다.")

# ======== 메인 메뉴 ========
else:
    st.title(f"👋 안녕하세요, {st.session_state.username}님 ({st.session_state.role})!")
    menu_choice = st.radio("무엇을 하시겠습니까?", ["시험 정보 입력", "학생 명단 입력"])

    # 시험 정보 입력
    if menu_choice == "시험 정보 입력":
        st.subheader("📋 시험 정보 입력")

        my_classes = {
            "김서진선생님": ["초6-A반", "중1-B반"],
            "류승연선생님": ["중1-A반"],
            "조하현선생님": ["중2-C반"],
            "이윤로원장님": ["전체 관리"],
            "이라온실장님": ["전체 관리"]
        }

        teacher_name = st.session_state.username
        classes = my_classes.get(teacher_name, ["담당 반 없음"])
        selected_class = st.selectbox("담당 반 선택", classes)

        school_name = st.text_input("🏫 학교명")
        exam_start = st.date_input("🗓️ 시험 시작일")
        exam_end = st.date_input("🗓️ 시험 종료일")
        math_exam_date = st.date_input("📘 수학 시험일")

        if st.button("시험 정보 저장"):
            if "class_info" not in st.session_state:
                st.session_state.class_info = {}
            st.session_state.class_info[selected_class] = {
                "학교명": school_name,
                "시험기간": f"{exam_start} ~ {exam_end}",
                "수학시험": math_exam_date
            }
            st.success(f"{selected_class}의 시험 정보를 저장했습니다.")

        if "class_info" in st.session_state and selected_class in st.session_state.class_info:
            st.write("📄 저장된 정보:")
            st.json(st.session_state.class_info[selected_class])

    # 학생 명단 입력
    elif menu_choice == "학생 명단 입력":
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

        school_level = st.selectbox("학교급 선택", ["초등", "중등", "고등"])
        school = st.selectbox("학교명", school_options[school_level])
        grade = st.selectbox("학년", grade_options[school_level])
        class_name = st.text_input("반명 (예: A반, 1반 등)")
        homeroom_teacher = st.text_input("담임 이름")
        class_time = st.selectbox("수업 시간", class_time_options[school_level])
        subjects = st.multiselect("수업 과목", subject_options[school_level])
        student_name = st.text_input("학생 이름")

        if st.button("학생 등록"):
            if "students" not in st.session_state:
                st.session_state.students = []
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
            st.success(f"{student_name} 학생 정보가 등록되었습니다.")

        if "students" in st.session_state and st.session_state.students:
            st.subheader("📋 등록된 학생 명단")
            for student in st.session_state.students:
                st.write(student)

        else:
            st.error("❌ 비밀번호가 틀렸습니다.")

# ======== 메인 화면 UI (인삿말 + 버튼) ========
elif not st.session_state.menu:
    st.markdown(f"## 👋 {st.session_state.username} 선생님 안녕하세요.")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📋 시험 정보 입력", use_container_width=True):
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
        if "class_info" not in st.session_state:
            st.session_state.class_info = {}
        st.session_state.class_info[selected_class] = {
            "학교명": school_name,
            "시험기간": f"{exam_start} ~ {exam_end}",
            "수학시험": math_exam_date
        }
        st.success(f"{selected_class}의 시험 정보를 저장했습니다.")

    if "class_info" in st.session_state and selected_class in st.session_state.class_info:
        st.write("📄 저장된 정보:")
        st.json(st.session_state.class_info[selected_class])

# ======== 시간표 출력 (임시 안내) ========
elif st.session_state.menu == "시간표 출력":
    st.subheader("🧠 시간표 출력 기능")
    st.info("자동 시간표 출력 기능이 여기에 구현될 예정입니다.")
