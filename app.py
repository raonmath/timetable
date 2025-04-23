import streamlit as st

# 비밀번호 기반 사용자 정보
PASSWORDS = {
    "rt5222": {"name": "이윤로", "role": "원장"},
    "rt1866": {"name": "이라온", "role": "실장"},
    "rt0368": {"name": "김서진", "role": "강사"},
    "rt0621": {"name": "류승연", "role": "강사"},
    "rt7705": {"name": "임인섭", "role": "강사"},
    "rt3137": {"name": "정주빈", "role": "강사"},
    "rt7735": {"name": "조하현", "role": "강사"},
    "rt0365": {"name": "유진서", "role": "조교"},
    "rt3080": {"name": "이예원", "role": "조교"},
}

# 초기 세션값
if "page" not in st.session_state:
    st.session_state.page = "login"
    st.session_state.user = ""
    st.session_state.role = ""

# 페이지 전환 함수
def go(page):
    st.session_state.page = page
    st.experimental_rerun()

# 1. 로그인 화면
if st.session_state.page == "login":
    st.title("🔐 라온 시간표 시스템")
    pw = st.text_input("비밀번호를 입력하세요", type="password")
    if st.button("확인") or st.session_state.get("pw_entered", False):
        user = PASSWORDS.get(pw)
        if user:
            st.session_state.user = user["name"]
            st.session_state.role = user["role"]
            go("main")
        else:
            st.error("비밀번호가 올바르지 않습니다.")

# 2. 메인 화면 (권한별 메뉴 구성)
elif st.session_state.page == "main":
    st.markdown(f"## 👋 {st.session_state.user}님 환영합니다. ({st.session_state.role})")
    st.write("")

    role = st.session_state.role
    if role in ["원장", "실장"]:
        cols = st.columns(4)
        if cols[0].button("📊 현황보고"):
            st.info("현황보고 화면으로 이동합니다.")
        if cols[1].button("👤 원생입력"):
            st.info("원생입력 화면으로 이동합니다.")
        if cols[2].button("📝 시험입력"):
            st.info("시험입력 화면으로 이동합니다.")
        if cols[3].button("📅 시간표출력"):
            st.info("시간표출력 화면으로 이동합니다.")
    elif role == "조교":
        cols = st.columns(3)
        if cols[0].button("👤 원생입력"):
            st.info("원생입력 화면으로 이동합니다.")
        if cols[1].button("📝 시험입력"):
            st.info("시험입력 화면으로 이동합니다.")
        if cols[2].button("📅 시간표출력"):
            st.info("시간표출력 화면으로 이동합니다.")
    elif role == "강사":
        cols = st.columns(2)
        if cols[0].button("📝 시험입력"):
            st.info("시험입력 화면으로 이동합니다.")
        if cols[1].button("📅 시간표출력"):
            st.info("시간표출력 화면으로 이동합니다.")
