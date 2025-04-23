import streamlit as st
import pandas as pd

# 사용자 인증 정보
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

초등학교 = sorted(["배봉초", "전농초", "전동초", "휘봉초", "삼육초", "청량초"])
중학교 = sorted(["휘경여중", "전동중", "전일중", "전농중", "동대문중", "장평중", "경희중", "경희여중"])
고등학교 = sorted(["휘경여고", "해성여고", "동대부고", "휘봉고", "경희고", "경희여고", "대광고", "한대부고", "혜원여고", "중화고", "석관고"])

학년_초 = ["초3", "초4", "초5", "초6"]
학년_중 = ["중1", "중2", "중3"]
학년_고 = ["고1", "고2", "고3"]

시간_초 = ["월수금(3시~5시)", "화목(3시~6시)"]
시간_중 = ["월수금(5시~7시30분)", "월수금(7시30분~10시)", "화목토(5시~7시30분)", "화목토(7시30분~10시)"]
시간_고 = ["월수(5시~8시30분)", "월수(6시30분~10시)", "화목(5시~8시30분)", "화목(6시30분~10시)"]

과목_초 = sorted(["초3-1", "초3-2", "초4-1", "초4-2", "초5-1", "초5-2", "초6-1", "초6-2"])
과목_중 = sorted(["중1-1", "중1-2", "중2-1", "중2-2", "중3-1", "중3-2"])
과목_고 = sorted(["공통수학1", "공통수학2", "대수", "미적분1", "미적분2", "확률과 통계", "기하", "수학1", "수학2", "미적분"])

# 세션 초기화
if "page" not in st.session_state:
    st.session_state.page = "login"
    st.session_state.user = ""
    st.session_state.role = ""
    st.session_state.login_error = False
    st.session_state.students = []

def login():
    pw = st.session_state.password_input
    user = PASSWORDS.get(pw)
    if user:
        st.session_state.user = user["name"]
        st.session_state.role = user["role"]
        st.session_state.page = "main"
        st.session_state.login_error = False
    else:
        st.session_state.login_error = True

# 로그인
if st.session_state.page == "login":
    st.title("🔐 라온 시간표 시스템")
    st.text_input("비밀번호를 입력하세요", type="password", key="password_input")
    st.button("확인", on_click=login)
    if st.session_state.login_error:
        st.error("비밀번호가 올바르지 않습니다.")

# 메인
elif st.session_state.page == "main":
    st.markdown(f"## 👋 {st.session_state.user}님 환영합니다. ({st.session_state.role})")
    role = st.session_state.role
    if role in ["원장", "실장"]:
        cols = st.columns(4)
        if cols[0].button("📊 현황보고"): pass
        if cols[1].button("👤 원생입력"):
            st.session_state.page = "student_input"
        if cols[2].button("📝 시험입력"): pass
        if cols[3].button("📅 시간표출력"): pass
    elif role == "조교":
        cols = st.columns(3)
        if cols[0].button("👤 원생입력"):
            st.session_state.page = "student_input"
        if cols[1].button("📝 시험입력"): pass
        if cols[2].button("📅 시간표출력"): pass
    elif role == "강사":
        cols = st.columns(2)
        if cols[0].button("📝 시험입력"): pass
        if cols[1].button("📅 시간표출력"): pass
            
# 원생입력 화면
elif st.session_state.page == "student_input":
    # 권한 확인
    if st.session_state.role not in ["원장", "실장"]:
        st.warning("⚠️ 원생정보 입력은 원장님과 실장님만 가능합니다.")
        if st.button("⬅️ 메인으로"):
            st.session_state.page = "main"
    else:
        st.title("👤 원생정보 입력")

        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("이름")
            level = st.radio("구분", ["초등", "중등", "고등"], horizontal=True)

            if level == "초등":
                school = st.selectbox("학교", 초등학교)
                grade = st.selectbox("학년", 학년_초)
                time = st.selectbox("수업시간", 시간_초)
                subjects = st.multiselect("학습과정", 과목_초)
            elif level == "중등":
                school = st.selectbox("학교", 중학교)
                grade = st.selectbox("학년", 학년_중)
                time = st.selectbox("수업시간", 시간_중)
                subjects = st.multiselect("학습과정", 과목_중)
            else:
                school = st.selectbox("학교", 고등학교)
                grade = st.selectbox("학년", 학년_고)
                time = st.selectbox("수업시간", 시간_고)
                subjects = st.multiselect("학습과정", 과목_고)

            classname = st.text_input("반명")
            homeroom = st.selectbox("담임", sorted([info["name"] for info in PASSWORDS.values()]))

            if st.button("💾 저장"):
                st.session_state.students.append({
                    "이름": name,
                    "구분": level,
                    "학교": school,
                    "학년": grade,
                    "반명": classname,
                    "담임": homeroom,
                    "수업시간": time,
                    "학습과정": ", ".join(subjects)
                })
                st.success("✅ 원생정보가 저장되었습니다.")

        with col2:
            st.subheader("📥 엑셀 업로드")
            uploaded = st.file_uploader("xlsx 파일을 업로드하세요", type="xlsx")
            if uploaded:
                df = pd.read_excel(uploaded)
                st.dataframe(df)

        st.markdown("---")
        st.subheader("📋 현재 저장된 원생 목록")
        if st.session_state.students:
            df = pd.DataFrame(st.session_state.students)
            st.dataframe(df, use_container_width=True)

        colA, colB = st.columns(2)
        if colA.button("⬅️ 메인으로"):
            st.session_state.page = "main"
        if colB.button("🗑 전체삭제"):
            st.session_state.students.clear()
            st.warning("모든 원생 정보가 삭제되었습니다.")
