
import streamlit as st
from datetime import date
import pandas as pd
from collections import defaultdict

# ===== 가상 데이터: 학생 정보 =====
students = [
    {"이름": "김서연", "학교": "휘경여고", "반": "중2-C반"},
    {"이름": "박성민", "학교": "휘경여고", "반": "중2-C반"},
    {"이름": "이지우", "학교": "중화고", "반": "중2-C반"},
    {"이름": "이수빈", "학교": "중화고", "반": "고1-B반"},
    {"이름": "정예린", "학교": "휘경여고", "반": "고1-B반"},
    {"이름": "김민준", "학교": "경희여고", "반": "고1-B반"},
]

# 로그인된 사용자 기준 담당 반
my_classes = ["중2-C반", "고1-B반"]

# ===== 그룹핑: 학교별 → 반별 학생 목록 =====
school_table = defaultdict(lambda: defaultdict(list))

for stu in students:
    if stu["반"] in my_classes:
        school_table[stu["학교"]][stu["반"]].append(stu["이름"])

# ===== 시험일 저장공간 =====
if "exam_schedule" not in st.session_state:
    st.session_state.exam_schedule = {}

st.title("📋 시험정보 입력")

# ===== 테이블 생성 =====
data = []

for school, classes in school_table.items():
    row = {"학교명": school}
    for cls in my_classes:
        names = classes.get(cls, [])
        if names:
            row[cls] = f"{', '.join(names)} ({len(names)}명)"
        else:
            row[cls] = ""
    exam_start = st.date_input(f"[{school}] 시험 시작일", key=f"{school}_start")
    exam_end = st.date_input(f"[{school}] 시험 종료일", key=f"{school}_end")
    math_day = st.date_input(f"[{school}] 수학 시험일", key=f"{school}_math")
    row["시험기간"] = f"{exam_start} ~ {exam_end}"
    row["수학시험일"] = str(math_day)
    st.session_state.exam_schedule[school] = {
        "시험시작": exam_start,
        "시험종료": exam_end,
        "수학시험일": math_day
    }
    data.append(row)

# ===== 표 출력 =====
df = pd.DataFrame(data)
st.dataframe(df)

# ===== 저장 확인 =====
if st.button("✅ 저장 완료"):
    st.success("모든 시험 정보가 저장되었습니다.")
    st.json(st.session_state.exam_schedule)
