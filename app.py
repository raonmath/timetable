
import streamlit as st
import pandas as pd
from datetime import date
from collections import defaultdict

# ===== 테스트용 학생 데이터 =====
students = [
    {"이름": "김서연", "학교": "휘경여고", "반": "중2-C반"},
    {"이름": "박성민", "학교": "휘경여고", "반": "중2-C반"},
    {"이름": "이지우", "학교": "중화고", "반": "중2-C반"},
    {"이름": "이수빈", "학교": "중화고", "반": "고1-B반"},
    {"이름": "정예린", "학교": "휘경여고", "반": "고1-B반"},
    {"이름": "김민준", "학교": "경희여고", "반": "고1-B반"},
]

my_classes = ["중2-C반", "고1-B반"]

# ===== 그룹핑 =====
school_table = defaultdict(lambda: defaultdict(list))
for stu in students:
    if stu["반"] in my_classes:
        school_table[stu["학교"]][stu["반"]].append(stu["이름"])

# ===== 시험일 항목 정의 =====
EXAM_SUBJECTS = ["국어", "수학", "영어"]

# ===== 시험 스케줄 초기화 =====
if "exam_schedule" not in st.session_state:
    st.session_state.exam_schedule = {}

st.title("📋 시험정보 입력")

# ===== 표 구성 =====
table_rows = []
for school, class_map in sorted(school_table.items()):
    row = {"학교명": school}
    for cls in my_classes:
        names = class_map.get(cls, [])
        row[cls] = f"{', '.join(names)} ({len(names)}명)" if names else ""

    start = st.date_input(f"{school} 시험 시작일", key=f"{school}_start")
    end = st.date_input(f"{school} 시험 종료일", key=f"{school}_end")

    row["시험기간"] = f"{start} ~ {end}"

    for subject in EXAM_SUBJECTS:
        exam_day = st.date_input(f"{school} {subject} 시험일", key=f"{school}_{subject}")
        row[f"{subject}시험일"] = exam_day.strftime("%Y-%m-%d")

    st.session_state.exam_schedule[school] = {
        "시험기간": (start, end),
        **{f"{subject}": st.session_state[f"{school}_{subject}"] for subject in EXAM_SUBJECTS}
    }
    table_rows.append(row)

# ===== 데이터프레임 출력 =====
df = pd.DataFrame(table_rows)
st.dataframe(df)

# ===== 저장 확인 =====
if st.button("✅ 저장 완료"):
    st.success("입력한 모든 시험 일정이 저장되었습니다.")
    st.json(st.session_state.exam_schedule)
