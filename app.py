
import streamlit as st

# ======== 사용자 비밀번호 및 역할 ========
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
    st.session_state.menu = None

# ======== 로그인 화면 ========
if not st.session_state.authenticated:
    st.title("🔐 로그인")
    password = st.text_input("비밀번호를 입력하세요", type="password")
    if st.button("확인"):
        user = PASSWORDS.get(password)
        if user:
            st.session_state.authenticated = True
            st.session_state.username = user["name"]
            st.session_state.role = user["role"]
            st.success(f"✅ 로그인 성공! {user['name']} ({user['role']})")
        else:
            st.error("❌ 비밀번호가 틀렸습니다.")

# ======== 메인 화면 (로그인 후 첫 화면) ========
elif st.session_state.authenticated and st.session_state.menu is None:
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

# ======== 메뉴에 따른 화면 분기 ========
elif st.session_state.menu == "시험 정보 입력":
    st.subheader("📋 시험 정보 입력")
    st.info("이곳에서 반별 시험 일정 정보를 입력합니다.")

elif st.session_state.menu == "시간표 출력":
    st.subheader("🧠 시간표 출력")
    st.info("자동 생성된 시간표 출력 기능입니다.")

elif st.session_state.menu == "현황 보고":
    st.subheader("📊 현황 보고")
    st.info("전체 수업 및 시험 정보 현황을 확인할 수 있습니다.")
