import streamlit as st
import pandas as pd
import json
import os
from datetime import date

# 파일 경로
DATA_PATH = "students.json"
EXAM_PATH = "exam_dates.json"

# 사용자 비밀번호 목록
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

# 저장/불러오기 함수
def load_students():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_students(data):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_exam_dates():
    if os.path.exists(EXAM_PATH):
        with open(EXAM_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_exam_dates(data):
    with open(EXAM_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 초기 세션 설정
if "page" not in st.session_state:
    st.session_state.page = "login"
    st.session_state.user = ""
    st.session_state.role = ""
    st.session_state.students = load_students()
    st.session_state.exam_subjects = ["시험기간", "수학시험일"]
    st.session_state.exam_dates = load_exam_dates()
    st.session_state.confirm_delete = False
    st.session_state.delete_index = None

# 로그인 처리
def login():
    pw = st.session_state.get("password_input", "")
    user = PASSWORDS.get(pw)
    if user:
        st.session_state.user = user["name"]
        st.session_state.role = user["role"]
        st.session_state.page = "main"
        st.rerun()
    else:
        st.error("비밀번호가 올바르지 않습니다.")

# 화면: 로그인
if st.session_state.page == "login":
    st.title("🔐 라온 시간표 시스템")
    st.text_input("비밀번호를 입력하세요", type="password", key="password_input")
    if st.button("확인"):
        login()

# 화면: 메인
elif st.session_state.page == "main":
    st.markdown(f"## 👋 {st.session_state.user}님 환영합니다.")
    role = st.session_state.role

    if role in ["원장", "실장"]:
        cols = st.columns(4)
        if cols[0].button("📊 현황보고"): pass
        if cols[1].button("👤 원생입력"):
            st.session_state.page = "student_input"
            st.rerun()
        if cols[2].button("📝 시험입력"):
            st.session_state.page = "exam_input"
            st.rerun()
        if cols[3].button("📋 원생관리"):
            st.session_state.page = "student_manage"
            st.rerun()
    elif role == "조교":
        cols = st.columns(3)
        if cols[0].button("👤 원생입력"):
            st.session_state.page = "student_input"
            st.rerun()
        if cols[1].button("📝 시험입력"):
            st.session_state.page = "exam_input"
            st.rerun()
        if cols[2].button("📋 원생관리"):
            st.session_state.page = "student_manage"
            st.rerun()
    elif role == "강사":
        cols = st.columns(2)
        if cols[0].button("📝 시험입력"):
            st.session_state.page = "exam_input"
            st.rerun()
        if cols[1].button("📋 원생관리"):
            st.session_state.page = "student_manage"
            st.rerun()

# 화면: 원생입력
elif st.session_state.page == "student_input":
    st.title("👤 원생정보 입력")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("이름")
        level = st.radio("구분", ["초등", "중등", "고등"], horizontal=True)

        school_map = {
            "초등": sorted(["배봉초", "전농초", "전동초", "휘봉초", "삼육초", "청량초"]),
            "중등": sorted(["휘경여중", "전동중", "전일중", "전농중", "동대문중", "장평중", "경희중", "경희여중"]),
            "고등": sorted(["휘경여고", "해성여고", "동대부고", "휘봉고", "경희고", "경희여고", "대광고", "한대부고", "혜원여고", "중화고", "석관고"]),
        }
        grade_map = {
            "초등": ["초3", "초4", "초5", "초6"],
            "중등": ["중1", "중2", "중3"],
            "고등": ["고1", "고2", "고3"],
        }
        time_map = {
            "초등": ["월수금(3시~5시)", "화목(3시~6시)"],
            "중등": ["월수금(5시~7시30분)", "월수금(7시30분~10시)", "화목토(5시~7시30분)", "화목토(7시30분~10시)"],
            "고등": ["월수(5시~8시30분)", "월수(6시30분~10시)", "화목(5시~8시30분)", "화목(6시30분~10시)"]
        }
        subject_map = {
            "초등": sorted(["초3-1", "초3-2", "초4-1", "초4-2", "초5-1", "초5-2", "초6-1", "초6-2"]),
            "중등": sorted(["중1-1", "중1-2", "중2-1", "중2-2", "중3-1", "중3-2"]),
            "고등": sorted(["공통수학1", "공통수학2", "대수", "미적분1", "미적분2", "확률과 통계", "기하", "수학1", "수학2", "미적분"]),
        }

        school = st.selectbox("학교", school_map[level])
        grade = st.selectbox("학년", grade_map[level])
        classname = st.text_input("반명")
        homeroom = st.selectbox("담임", sorted([info["name"] for info in PASSWORDS.values()]))
        time = st.selectbox("수업시간", time_map[level])
        subjects = st.multiselect("학습과정", subject_map[level])

        if st.button("💾 저장"):
            new_student = {
                "이름": name, "구분": level, "학교": school, "학년": grade,
                "반명": classname, "담임": homeroom, "수업시간": time,
                "학습과정": ", ".join(subjects)
            }
            # 중복 방지
            st.session_state.students = [
                s for s in st.session_state.students
                if not (s["이름"] == name and s["반명"] == classname)
            ]
            st.session_state.students.append(new_student)
            save_students(st.session_state.students)
            st.success("저장되었습니다.")

    with col2:
        st.subheader("📥 엑셀 업로드")
        file = st.file_uploader("xlsx 업로드", type="xlsx")
        if file:
            df = pd.read_excel(file)
            for _, row in df.iterrows():
                new = row.to_dict()
                if not any(s["이름"] == new["이름"] and s["반명"] == new["반명"] for s in st.session_state.students):
                    st.session_state.students.append(new)
            save_students(st.session_state.students)
            st.success("업로드 완료!")

        if st.button("📤 엑셀 양식 다운로드"):
            import io
            import openpyxl
            buffer = io.BytesIO()
            pd.DataFrame([{
                "이름": "예시학생", "구분": "중등", "학교": "전농중", "학년": "중2",
                "반명": "중2A", "담임": "김서진", "수업시간": "월수금(5시~7시30분)",
                "학습과정": "중2-1, 중2-2"
            }]).to_excel(buffer, index=False, engine="openpyxl")
            st.download_button("양식 다운로드", buffer.getvalue(), "원생입력양식.xlsx")

    if st.button("📋 원생정보확인"):
        df = pd.DataFrame(st.session_state.students)
        if df.empty:
            st.info("저장된 학생 정보가 없습니다.")
        else:
            st.dataframe(df)
            if st.button("🗑 전체 삭제"):
                st.session_state.confirm_delete = True
            if st.session_state.confirm_delete:
                if st.button("❗ 삭제 확정"):
                    st.session_state.students.clear()
                    save_students([])
                    st.session_state.confirm_delete = False
                    st.warning("모든 원생정보가 삭제되었습니다.")
                if st.button("취소"):
                    st.session_state.confirm_delete = False

    if st.button("⬅️ 이전단계로"):
        st.session_state.page = "main"
        st.rerun()

# 화면: 시험정보입력
elif st.session_state.page == "exam_input":
    st.title("📝 시험정보 입력")

    students = st.session_state.students
    role = st.session_state.role
    user = st.session_state.user

    if role == "강사":
        students = [s for s in students if s["담임"] == user]

    # 반명 기준 정리
    class_list = sorted({s["반명"] for s in students})
    school_list = sorted({s["학교"] for s in students})

    school_class_map = {}
    for s in students:
        school = s["학교"]
        cls = s["반명"]
        name = s["이름"]
        school_class_map.setdefault(school, {}).setdefault(cls, []).append(name)

    # 과목 추가
    new_subject = st.text_input("과목 입력 후 추가 버튼을 눌러주세요")
    if st.button("과목시험일 추가") and new_subject:
        key = f"{new_subject.strip()}시험일"
        if key not in st.session_state.exam_subjects:
            st.session_state.exam_subjects.append(key)

    # 표 생성
    st.write("📋 시험정보 입력표")
    for school, classes in school_class_map.items():
        st.markdown(f"### 🏫 {school}")
        cols = st.columns(len(classes))
        for i, (cls, names) in enumerate(classes.items()):
            cols[i].write(f"**{cls}**")
            cols[i].write(", ".join(names) + f" ({len(names)}명)")

        for subj in st.session_state.exam_subjects:
            st.markdown(f"📌 **{subj} 입력**")
            cols = st.columns(len(classes))
            for i, (cls, _) in enumerate(classes.items()):
                key = f"{school}_{cls}_{subj}"
                if "시험기간" in subj:
                    start = st.date_input(f"{cls} 시작", key=f"{key}_start", value=date.today())
                    end = st.date_input(f"{cls} 종료", key=f"{key}_end", value=date.today())
                    w1 = "월화수목금토일"[start.weekday()]
                    w2 = "월화수목금토일"[end.weekday()]
                    st.session_state.exam_dates[key] = f"{start.strftime('%m-%d')}({w1})~{end.strftime('%m-%d')}({w2})"
                else:
                    dt = st.date_input(f"{cls}", key=key, value=date.today())
                    w = "월화수목금토일"[dt.weekday()]
                    st.session_state.exam_dates[key] = f"{dt.strftime('%m-%d')}({w})"

    if st.button("✅ 시험정보 저장"):
        save_exam_dates(st.session_state.exam_dates)
        st.success("시험 일정이 저장되었습니다.")
        st.json(st.session_state.exam_dates)

    if st.button("⬅️ 이전단계로"):
        st.session_state.page = "main"
        st.rerun()


# 화면: 원생정보 열람/수정
elif st.session_state.page == "student_manage":
    st.title("📋 원생 정보 관리")

    students = st.session_state.students
    role = st.session_state.role
    user = st.session_state.user

    if role == "강사":
        students = [s for s in students if s["담임"] == user]

    df = pd.DataFrame(students)
    if df.empty:
        st.info("아직 저장된 원생 정보가 없습니다.")
    else:
        levels = sorted(df["구분"].unique())
        selected_level = st.selectbox("구분 선택", levels)
        filtered = df[df["구분"] == selected_level]

        teachers = sorted(filtered["담임"].unique())
        selected_teacher = st.selectbox("담임 선택", teachers)
        filtered = filtered[filtered["담임"] == selected_teacher]

        classes = sorted(filtered["반명"].unique())
        selected_class = st.selectbox("반 선택", classes)
        filtered = filtered[filtered["반명"] == selected_class]

        names = filtered["이름"].tolist()
        selected_name = st.selectbox("학생 선택", names)

        student = next((s for s in st.session_state.students if s["이름"] == selected_name and s["반명"] == selected_class), None)

        if student:
            st.subheader(f"✏️ {selected_name} 정보 수정")
            student["학교"] = st.text_input("학교", student["학교"])
            student["학년"] = st.text_input("학년", student["학년"])
            student["반명"] = st.text_input("반명", student["반명"])
            student["담임"] = st.text_input("담임", student["담임"])
            student["수업시간"] = st.text_input("수업시간", student["수업시간"])
            student["학습과정"] = st.text_input("학습과정", student["학습과정"])

            if st.button("💾 수정저장"):
                save_students(st.session_state.students)
                st.success("수정 완료되었습니다.")
                st.rerun()

            if st.button("🗑 삭제"):
                st.session_state.confirm_delete = True
                st.session_state.delete_index = student

            if st.session_state.get("confirm_delete") and st.session_state.delete_index == student:
                if st.button("❗ 삭제 확정"):
                    st.session_state.students = [
                        s for s in st.session_state.students
                        if not (s["이름"] == selected_name and s["반명"] == selected_class)
                    ]
                    save_students(st.session_state.students)
                    st.session_state.confirm_delete = False
                    st.success("삭제 완료되었습니다.")
                    st.rerun()
                if st.button("취소"):
                    st.session_state.confirm_delete = False

    if st.button("⬅️ 이전단계로"):
        st.session_state.page = "main"
        st.rerun()
