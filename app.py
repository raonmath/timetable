import streamlit as st

def go(page_name):
    st.session_state.page = page_name

def main():
    st.set_page_config(page_title="학생 관리 시스템", layout="wide")

    if "page" not in st.session_state:
        st.session_state.page = "login"

    if st.session_state.page == "login":
        st.title("🔐 로그인")
        username = st.text_input("아이디")
        role = st.selectbox("역할", ["원장", "실장", "조교", "강사", "학생"])
        if st.button("로그인"):
            st.session_state["username"] = username
            st.session_state["role"] = role
            go("main")

    elif st.session_state.page == "main":
        st.title("📚 학생 관리 시스템")
        st.button("현황보고", on_click=lambda: go("dashboard"))
        st.button("학생 관리", on_click=lambda: go("student_manage"))
        st.button("시험 입력", on_click=lambda: go("exam_input"))
        st.button("시간표 출력", on_click=lambda: go("timetable"))
        st.button("원생정보", on_click=lambda: go("student_detail"))

    elif st.session_state.page == "student_manage":
        st.subheader("👨‍🎓 학생관리")
        st.write("여기에 학생 목록 테이블 및 추가/삭제 기능이 들어갑니다.")
        st.button("이전 단계로", on_click=lambda: go("main"))

    elif st.session_state.page == "exam_input":
        st.subheader("📘 시험 입력")
        st.write("여기에 시험 입력 기능이 들어갑니다.")
        st.button("이전 단계로", on_click=lambda: go("main"))

    elif st.session_state.page == "dashboard":
        st.subheader("📊 현황보고")
        st.write("여기에 통계나 주요 요약 정보가 표시됩니다.")
        st.button("이전 단계로", on_click=lambda: go("main"))

    elif st.session_state.page == "timetable":
        st.subheader("🗓️ 시간표 출력")
        st.write("시간표 테이블 또는 이미지 출력이 여기에 들어갑니다.")
        st.button("이전 단계로", on_click=lambda: go("main"))

    elif st.session_state.page == "student_detail":
        st.subheader("📋 원생정보")
        st.write("선택된 학생의 상세 정보 수정 화면이 여기에 들어갑니다.")
        st.button("이전 단계로", on_click=lambda: go("main"))

if __name__ == "__main__":
    main()
