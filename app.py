import streamlit as st
import json
import os

# 데이터 경로
STUDENT_FILE = "data/students.json"
USER_FILE = "data/users.json"

# 권한별 메뉴 구성
ROLE_MENUS = {
    "원장": ["학생관리", "시험입력", "시간표출력", "현황보고", "사용자관리"],
    "실장": ["학생관리", "시험입력", "시간표출력", "현황보고"],
    "팀장": ["학생관리", "시험입력", "시간표출력"],
    "강사": ["시험입력", "시간표출력"],
    "조교": ["학생관리", "시험입력", "시간표출력"]
}

def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_students():
    if not os.path.exists(STUDENT_FILE):
        return []
    with open(STUDENT_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                return []
        except:
            return []

def save_students(data):
    with open(STUDENT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def login():
    st.title("👨‍🏫 라온 시간표 생성 시스템")
    password = st.text_input("비밀번호를 입력하세요", type="password")
    if st.button("로그인"):
        users = load_users()
        for user_id, info in users.items():
            if info["password"] == password:
                st.session_state["logged_in"] = True
                st.session_state["role"] = info["role"]
                st.experimental_rerun()
        st.warning("비밀번호가 틀렸습니다.")

def student_management():
    st.header("👨‍🎓 학생관리")

    with st.expander("📝 학생 등록"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("이름")
            role = st.selectbox("구분", ["학생", "강사", "조교"])
        with col2:
            school = st.text_input("학교") if role == "학생" else ""
            grade = st.selectbox("학년", ["1학년", "2학년", "3학년"], index=0) if role == "학생" else ""

        col3, col4 = st.columns(2)
        with col3:
            classname = st.text_input("반명")
            homeroom = st.selectbox("담임", ["김담임", "이담임", "박담임"])
        with col4:
            time = st.text_input("수업시간")
            course = st.text_input("수업과정")

        if st.button("저장"):
            if name:
                students = load_students()
                students.append({
                    "이름": name, "구분": role, "학교": school, "학년": grade,
                    "반명": classname, "담임": homeroom,
                    "수업시간": time, "수업과정": course
                })
                save_students(students)
                st.success("학생 정보가 저장되었습니다.")
                st.experimental_rerun()
            else:
                st.warning("이름은 필수 항목입니다.")

    st.divider()
    st.subheader("📋 현재 등록된 학생")

    students = load_students()
    selected = st.multiselect("삭제할 학생 선택", [s["이름"] for s in students])
    if st.button("선택삭제"):
        students = [s for s in students if s["이름"] not in selected]
        save_students(students)
        st.success("선택한 학생을 삭제했습니다.")
        st.experimental_rerun()
    if st.button("전체삭제"):
        if st.confirm("정말 모든 학생을 삭제하시겠습니까?"):
            save_students([])
            st.success("모든 학생을 삭제했습니다.")
            st.experimental_rerun()

    if students:
        df = [{k: s.get(k, "") for k in ["이름", "학교", "반명", "담임", "수업시간"]} for s in students]
        st.dataframe(df, use_container_width=True)

def sidebar_menu():
    st.sidebar.title("📚 메뉴")
    menu = ROLE_MENUS.get(st.session_state["role"], [])
    return st.sidebar.radio("이동", menu)

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
else:
    page = sidebar_menu()
    if page == "학생관리":
        student_management()
    elif page == "시험입력":
        st.header("📝 시험입력 (준비중)")
    elif page == "시간표출력":
        st.header("📅 시간표출력 (준비중)")
    elif page == "현황보고":
        st.header("📊 현황보고 (준비중)")
    elif page == "사용자관리":
        st.header("🧑‍💻 사용자관리 (준비중)")
