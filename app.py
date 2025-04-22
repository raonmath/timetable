
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
            st.experimental_rerun()
        else:
            st.error("❌ 비밀번호가 틀렸습니다.")

# ======== 메인 메뉴 ========
else:
    st.title(f"👋 안녕하세요, {st.session_state.username}님 ({st.session_state.role})!")
    menu_choice = st.radio("무엇을 하시겠습니까?", ["정보 입력", "시간표 출력"])

    if menu_choice == "정보 입력":
        st.subheader("📋 정보 입력 화면")

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
        exam_period = st.date_input("🗓️ 시험 기간 시작", key="exam_start")
        exam_end = st.date_input("🗓️ 시험 기간 종료", key="exam_end")
        math_exam_date = st.date_input("📘 수학 시험일")

        if st.button("저장하기"):
            if "class_info" not in st.session_state:
                st.session_state.class_info = {}

            st.session_state.class_info[selected_class] = {
                "학교명": school_name,
                "시험기간": f"{exam_period} ~ {exam_end}",
                "수학시험": math_exam_date
            }
            st.success(f"{selected_class}의 시험 정보를 저장했습니다.")

        if "class_info" in st.session_state and selected_class in st.session_state.class_info:
            st.write("📄 저장된 정보:")
            st.json(st.session_state.class_info[selected_class])

    elif menu_choice == "시간표 출력":
        st.subheader("🧠 시간표 출력 화면")
        st.info("자동으로 생성된 시간표를 여기에 표시할 예정입니다.")
