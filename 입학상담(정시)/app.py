import math
import re
import os
from html import escape
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

# ==================================================
# 1. 기본 설정 및 상수 데이터
# ==================================================
st.set_page_config(
    page_title="2027학년도 대진대학교 정시 입학상담",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()

GRADE_MAP = {1: 90, 2: 85, 3: 80, 4: 68, 5: 55, 6: 40, 7: 30, 8: 20, 9: 0}

ENG_DEPTS = {
    "의생명과학과", "식품영양학과", "간호학과", "보건경영학과", "공학자율학부",
    "전기공학과", "건축공학과", "AI건설융합공학과", "스마트시티·환경공학과",
    "데이터경영산업공학과", "반도체융합공학과", "IT기계공학과", "화학공학과",
    "컴퓨터공학과", "스마트융합보안학과", "AI빅데이터공학과", "스마트모빌리티공학과",
}

DEPT_ORDER = [
    "영어영문학과", "문예콘텐츠창작학과", "역사·문화콘텐츠학과", "경영학과",
    "글로벌경제학과", "국제통상학과", "공공인재법학과", "국제지역학과",
    "중국학과", "아동학과", "사회복지학과", "미디어커뮤니케이션학과",
    "행정정보학과", "문헌정보학과", "의생명과학과", "식품영양학과",
    "간호학과", "보건경영학과", "스포츠건강과학과", "공학자율학부",
    "전기공학과", "건축공학과", "AI건설융합공학과", "스마트시티·환경공학과",
    "데이터경영산업공학과", "반도체융합공학과", "IT기계공학과", "화학공학과",
    "컴퓨터공학과", "스마트융합보안학과", "AI빅데이터공학과",
    "스마트모빌리티공학과", "자율전공학부",
]

INQUIRY_SUBJECTS = [
    "선택안함", "사회·문화", "생활과 윤리", "한국지리", "정치와 법",
    "윤리와 사상", "세계지리", "경제", "동아시아사", "세계사",
    "물리학Ⅰ", "물리학Ⅱ", "화학Ⅰ", "화학Ⅱ", "생명과학Ⅰ", "생명과학Ⅱ",
    "지구과학Ⅰ", "지구과학Ⅱ", "직업탐구",
]

DEFAULTS = {
    "kor": 0.0,
    "math": 0.0,
    "math_subj": "확률과 통계",
    "eng_grade": "미선택",
    "hist_grade": "미선택",
    "inq1_subj": "선택안함",
    "inq2_subj": "선택안함",
    "inq1": 0.0,
    "inq2": 0.0,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

if "result" not in st.session_state:
    st.session_state.result = None

# ==================================================
# 2. 디자인
# ==================================================
st.markdown(
    """
<style>
    :root {
        --navy: #082070; --navy-deep: #051550; --primary: #1D3FA0; --tint: #E9EDF8;
        --silver: #D8E0E8; --text: #1B2440; --muted: #55607A; --line: #DDE3F0; --bg: #F3F5FB;
    }
    #MainMenu, footer, header { visibility: hidden; }
    .stApp {
        background: var(--bg); color: var(--text);
        font-family: "Pretendard", "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
    }
    .stApp::before {
        content: ""; position: fixed; top: 0; left: 0; right: 0; height: 4px; z-index: 999999;
        background: linear-gradient(90deg, var(--navy-deep), var(--navy) 50%, var(--primary));
    }
    .block-container {
        max-width: 1480px; padding-top: 2.6rem; padding-bottom: 2.4rem;
        padding-left: clamp(1rem, 2.5vw, 2.2rem); padding-right: clamp(1rem, 2.5vw, 2.2rem);
    }
    h1, h2, h3, h4 { color: var(--navy) !important; letter-spacing: -0.5px; }

    div[data-testid="column"] > div { height: 100%; }
    div[data-testid="stVerticalBlockBorderWrapper"] { height: 100%; }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #FFFFFF; border: 1px solid var(--line) !important; border-radius: 14px !important;
        box-shadow: 0 2px 8px rgba(8, 32, 112, 0.055);
    }
    [data-testid="stImage"] img {
        background: #FFFFFF; padding: 6px; border-radius: 14px;
        border: 1px solid var(--line); box-shadow: 0 4px 12px -4px rgba(8, 32, 112, 0.15);
    }

    [data-testid="stWidgetLabel"] p {
        color: var(--navy) !important; font-size: 14px !important;
        font-weight: 700 !important; line-height: 1.45 !important;
    }
    [data-testid="stWidgetLabel"] { min-height: 1.25rem; }

    [data-testid="stNumberInput"] input {
        background: var(--tint) !important; border: 1px solid transparent !important;
        color: var(--navy) !important; font-size: 18px !important; font-weight: 800 !important;
        min-height: 44px; border-radius: 10px;
    }
    [data-testid="stNumberInput"] input:focus {
        border-color: var(--primary) !important; box-shadow: 0 0 0 3px rgba(29, 63, 160, 0.15) !important;
    }
    [data-baseweb="select"] > div {
        background: var(--tint) !important; border-color: transparent !important;
        border-radius: 10px !important; color: var(--navy) !important;
        min-height: 44px; font-weight: 600;
    }
    [data-baseweb="select"] > div:focus-within {
        border-color: var(--primary) !important; box-shadow: 0 0 0 3px rgba(29, 63, 160, 0.15) !important;
    }

    [data-testid="stButton"] button {
        border-radius: 10px !important; min-height: 48px; font-weight: 750 !important;
        letter-spacing: -0.3px; transition: all .15s ease;
    }
    [data-testid="stButton"] button[kind="primary"] {
        background: linear-gradient(135deg, var(--navy), var(--primary)) !important;
        border: none !important; color: #FFFFFF !important;
        box-shadow: 0 6px 16px rgba(8, 32, 112, 0.28);
    }
    [data-testid="stButton"] button[kind="primary"]:hover {
        background: linear-gradient(135deg, var(--navy-deep), var(--navy)) !important;
        transform: translateY(-1px);
    }
    [data-testid="stButton"] button[kind="secondary"] {
        border: 1px solid var(--line) !important; color: var(--navy) !important; background: #FFFFFF !important;
    }
    [data-testid="stButton"] button[kind="secondary"]:hover {
        border-color: var(--navy) !important; background: var(--tint) !important;
    }

    [data-testid="stMetricLabel"] p {
        color: var(--muted) !important; font-size: 13px !important;
        font-weight: 600 !important; line-height: 1.4 !important;
    }
    [data-testid="stMetricValue"] {
        color: var(--navy) !important; font-size: clamp(21px, 2vw, 28px) !important;
        font-weight: 850 !important; font-variant-numeric: tabular-nums;
    }

    .eyebrow { color: var(--primary); font-size: 11px; font-weight: 850; letter-spacing: 1.8px; margin-bottom: 5px; }
    .page-title {
        color: #000000; font-size: clamp(26px, 3vw, 38px); font-weight: 900;
        letter-spacing: -1.2px; line-height: 1.3; margin-top: -6px;
    }
    .section-title {
        display: flex; align-items: center; gap: 10px; color: var(--navy);
        font-size: 20px; font-weight: 850; margin: 2px 0 14px;
    }
    .step {
        display: inline-flex; align-items: center; justify-content: center;
        width: 32px; height: 32px; border-radius: 9px;
        background: linear-gradient(135deg, var(--navy), var(--primary));
        color: #FFFFFF; font-size: 15px; font-weight: 900; flex-shrink: 0;
    }
    .subject-title {
        font-size: 15px; color: var(--navy); font-weight: 850;
        border-left: 4px solid var(--primary); padding-left: 10px;
        margin: 3px 0 10px; min-height: 23px; line-height: 1.5; box-sizing: border-box;
    }

    .rule-strip { display: flex; gap: 12px; flex-wrap: wrap; margin: 18px 0 22px; }
    .rule-item {
        flex: 1; min-width: 190px; padding: 16px 18px; border-radius: 12px;
        font-size: 15px; color: var(--muted); line-height: 1.6;
        background: #FFFFFF; border: 1px solid var(--line); border-top: 3px solid var(--primary);
    }
    .rule-item strong { font-size: 17px; color: var(--navy); margin-bottom: 6px; display: block; font-weight: 800; }

    .score-hero {
        position: relative; overflow: hidden;
        background: linear-gradient(135deg, var(--navy-deep) 0%, var(--navy) 55%, var(--primary) 100%);
        border-radius: 20px; padding: 30px; color: #FFFFFF; margin-bottom: 20px;
        box-shadow: 0 12px 24px rgba(8, 32, 112, 0.22);
    }
    .score-hero::after {
        content: ""; position: absolute; right: -60px; top: -60px; width: 220px; height: 220px;
        border-radius: 50%; background: radial-gradient(circle, rgba(255,255,255,0.14), rgba(255,255,255,0) 70%);
    }
    .score-label { font-size: 15px; font-weight: 700; color: #C3CEEA; }
    .score-number {
        font-size: clamp(42px, 4.5vw, 68px); font-weight: 900; letter-spacing: -2px;
        line-height: 1.2; margin: 10px 0; font-variant-numeric: tabular-nums;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .score-number small { font-size: 20px; font-weight: 600; color: #C3CEEA; letter-spacing: 0; }
    .score-footer {
        border-top: 1px solid rgba(255,255,255,0.18); padding-top: 16px;
        color: #C3CEEA; font-size: 14px; line-height: 1.7;
    }

    .status { border-radius: 14px; padding: 16px 20px; margin: 8px 0 16px; font-size: 16px; font-weight: 800; line-height: 1.6; }
    .empty-state {
        text-align: center; padding: 50px 20px; background: #FFFFFF;
        border: 2px dashed #B7C3E3; border-radius: 20px; color: var(--muted); line-height: 1.9;
    }
    .empty-state strong { display: block; color: var(--navy); font-size: 20px; font-weight: 800; margin-bottom: 8px; }

    [data-testid="stDataFrame"] {
        border: 1px solid var(--line); border-radius: 12px; overflow: hidden;
        background: #FFFFFF; width: 100% !important;
    }
    [data-testid="stAlert"] { border-radius: 10px; }

    @media (max-width: 900px) {
        .block-container { padding-top: 1.5rem; }
        .rule-item { min-width: 100%; }
        .score-hero { padding: 20px; }
        .section-title { font-size: 18px; }
    }
</style>
""",
    unsafe_allow_html=True,
)

# ==================================================
# 3. 공통 함수
# ==================================================
def invalidate_result():
    st.session_state.result = None


def reset_inputs():
    for key, value in DEFAULTS.items():
        st.session_state[key] = value
    invalidate_result()


def normalize_dept(value):
    return re.sub(r"\s+", "", str(value)).replace("ㆍ", "·").replace("･", "·")


def section_title(number, title):
    st.markdown(
        f'<div class="section-title"><span class="step">{escape(str(number))}</span>'
        f'{escape(title)}</div>',
        unsafe_allow_html=True,
    )


def subject_title(title):
    st.markdown(f'<div class="subject-title">{escape(title)}</div>', unsafe_allow_html=True)


def number_input(label, key):
    return st.number_input(
        label,
        min_value=0.0,
        max_value=100.0,
        step=1.0,
        format="%.0f",
        key=key,
        on_change=invalidate_result,
    )


def show_logo(path):
    try:
        st.image(path, use_container_width=True)
    except TypeError:
        st.image(path, use_column_width=True)


def to_number(value):
    if value is None:
        return None
    try:
        number = float(str(value).replace(",", "").strip())
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


def display_number(value):
    number = to_number(value)
    return "—" if number is None else f"{number:,.2f}"


def display_text(value):
    if value is None or pd.isna(value):
        return "—"
    text = str(value).strip()
    return text if text and text != "-" else "—"


def display_ratio(value):
    text = display_text(value)
    return text if text == "—" or ":" in text else f"{display_number(value)}:1"


def display_count(value):
    number = to_number(value)
    if number is None:
        return display_text(value)
    return f"{int(number):,}" if number.is_integer() else f"{number:,.1f}"


# ==================================================
# 4. 데이터 로딩
# ==================================================
@st.cache_data(show_spinner=False)
def load_data(file_path, header_row):
    path = Path(file_path)
    if path.suffix.lower() == ".csv":
        try:
            df = pd.read_csv(path, encoding="utf-8-sig", header=header_row)
        except UnicodeDecodeError:
            df = pd.read_csv(path, encoding="cp949", header=header_row)
    else:
        df = pd.read_excel(path, header=header_row)

    df.columns = [re.sub(r"\s+", "", str(column)) for column in df.columns]

    if "모집단위명" not in df.columns:
        raise ValueError("'모집단위명' 열을 찾을 수 없습니다.")
    if df.columns.duplicated().any():
        raise ValueError("정리 후 중복되는 열 이름이 있습니다.")

    df = df.dropna(subset=["모집단위명"]).copy()
    df["모집단위명"] = df["모집단위명"].map(normalize_dept)
    return df[df["모집단위명"] != ""].reset_index(drop=True)


target_files = [
    f for f in os.listdir(BASE_DIR)
    if "정시" in f
    and (f.endswith(".xls") or f.endswith(".xlsx") or f.endswith(".csv"))
    and not f.startswith("~")
]
ONLINE_TARGET_FILE = target_files[0] if target_files else None

db = pd.DataFrame()
header_line = 1

if ONLINE_TARGET_FILE:
    try:
        db = load_data(str(BASE_DIR / ONLINE_TARGET_FILE), header_line)
    except Exception as exc:
        st.error(f"데이터 로딩 오류: {exc}")
else:
    st.error("GitHub 서버 저장소에 '정시'가 포함된 엑셀 파일이 업로드되지 않았습니다.")


def detect_scale(df):
    values = []
    for col in df.columns:
        if any(str(y) in col for y in (2024, 2025, 2026)) and any(
            label in col for label in ("최고", "평균", "최저")
        ):
            values += [v for v in map(to_number, df[col]) if v is not None and v > 0]

    if not values:
        return None

    has_100_scale = any(v <= 105 for v in values)
    has_1000_scale = any(v >= 200 for v in values)
    if has_100_scale and has_1000_scale:
        return None

    median = float(pd.Series(values).median())
    if median <= 105:
        return 100
    if median >= 200:
        return 1000
    return None


data_scale = detect_scale(db) if not db.empty else 100

# ==================================================
# 5. 계산 함수
# ==================================================
def calculate_score(dept, kor, math_subj, math_val, eng_g, hist_g,
                    inq1_subj, inq1, inq2_subj, inq2):
    engineering = dept in ENG_DEPTS
    math_adj = math_val * (1.1 if engineering and math_subj in ("미적분", "기하") else 1)

    def inquiry(subj, value):
        if subj == "선택안함":
            return 0.0
        sci = any(name in subj for name in ("물리학", "화학", "생명과학", "지구과학"))
        return value * (1.07 if engineering and sci else 1)

    inquiry_scores = [inquiry(inq1_subj, inq1), inquiry(inq2_subj, inq2)]
    best_inquiry = max(range(2), key=lambda index: inquiry_scores[index])

    primary = [("국어", kor), ("수학", math_adj), ("영어", GRADE_MAP.get(eng_g, 0))]
    first_index = max(range(3), key=lambda index: primary[index][1])
    first = primary[first_index]

    remaining = [item for index, item in enumerate(primary) if index != first_index]
    remaining += [
        (f"탐구 {best_inquiry + 1}", inquiry_scores[best_inquiry]),
        ("한국사", GRADE_MAP.get(hist_g, 0)),
    ]
    second = max(remaining, key=lambda item: item[1])

    raw_score = first[1] * 0.6 + second[1] * 0.4

    return {
        "score": round(raw_score, 2),
        "score1000": round(raw_score * 10, 2),
        "first": first,
        "second": second,
        "engineering": engineering,
    }


def get_record_value(record, keywords):
    matches = [c for c in record.index if all(kw in str(c) for kw in keywords)]
    if len(matches) == 1 and pd.notna(record[matches[0]]):
        return record[matches[0]]
    return None


def build_history(record):
    rows, divisor = [], data_scale / 100
    for year in (2024, 2025, 2026):
        row = {"연도": str(year)}
        for label in ("최고", "평균", "최저"):
            value = to_number(get_record_value(record, [str(year), label]))
            row[label] = round(value / divisor, 2) if value is not None else None
        row["경쟁률"] = get_record_value(record, [str(year), "경쟁률"])
        row["추가합격"] = get_record_value(record, [str(year), "추가"])
        rows.append(row)
    return pd.DataFrame(rows)


# ==================================================
# 6. 헤더 및 입력 영역
# ==================================================
head_c1, head_c2 = st.columns([0.8, 9.2])

with head_c1:
    logo_png = BASE_DIR / "logo.png"
    logo_jpg = BASE_DIR / "logo.jpg"
    if logo_png.exists():
        show_logo(str(logo_png))
    elif logo_jpg.exists():
        show_logo(str(logo_jpg))

with head_c2:
    st.markdown(
        """
        <div class="eyebrow">ADMISSIONS COUNSELING · 2027</div>
        <div class="page-title">2027학년도 대진대학교 정시 입학상담 솔루션</div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="rule-strip">
        <div class="rule-item"><strong>01 &nbsp; 우수 영역 60%</strong>국어 · 수학 · 영어 중 가장 높은 영역</div>
        <div class="rule-item"><strong>02 &nbsp; 차 순위 영역 40%</strong>60%에 반영하지 않은 국·수·영, 탐구 상위 1과목, 한국사 중 최고</div>
        <div class="rule-item"><strong>03 &nbsp; 이공계열 가산점</strong>미적분·기하 10% / 과학탐구 7%</div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.container(border=True):
    section_title("01", "상담 모집단위")

    departments = (
        sorted(
            db["모집단위명"].unique().tolist(),
            key=lambda n: (DEPT_ORDER.index(n) if n in DEPT_ORDER else 999, n),
        )
        if not db.empty
        else DEPT_ORDER
    )

    dept_col, info_col = st.columns([2, 1])
    with dept_col:
        selected_dept = st.selectbox(
            "모집단위", departments, key="selected_dept", on_change=invalidate_result
        )
    with info_col:
        is_eng = selected_dept in ENG_DEPTS
        info_bg = "rgba(29, 63, 160, 0.08)" if is_eng else "rgba(5, 150, 105, 0.08)"
        info_border = "1px solid rgba(29, 63, 160, 0.2)" if is_eng else "1px solid rgba(5, 150, 105, 0.2)"
        info_color = "#1D3FA0" if is_eng else "#059669"
        info_text = "이공계열 · 수학 및 과학탐구 가산점 대상" if is_eng else "인문사회계열 · 별도 가산점 없음"
        st.markdown(
            f"""
            <div style="background-color: {info_bg}; border: {info_border}; border-radius: 10px; padding: 12px 16px; color: {info_color}; font-weight: 700; font-size: 14px; display: flex; align-items: center; height: 100%;">
                {info_text}
            </div>
            """,
            unsafe_allow_html=True
        )

    record = None
    if not db.empty:
        matching = db[db["모집단위명"] == selected_dept]
        if len(matching) == 1:
            record = matching.iloc[0]
        elif len(matching) > 1:
            record = matching.iloc[0]

with st.container(border=True):
    title_col, reset_col = st.columns([5, 1])
    with title_col:
        section_title("02", "수능 성적 입력")
    with reset_col:
        st.button("입력 초기화", on_click=reset_inputs, use_container_width=True)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        subject_title("국어")
        kor_score = number_input("국어 백분위", "kor")

    with c2:
        subject_title("수학")
        math_score = number_input("수학 백분위", "math")
        math_subj = st.selectbox(
            "수학 선택과목",
            ["확률과 통계", "미적분", "기하"],
            key="math_subj",
            on_change=invalidate_result,
        )

    with c3:
        subject_title("영어")
        eng_grade = st.selectbox(
            "영어 등급",
            ["미선택"] + list(range(1, 10)),
            key="eng_grade",
            on_change=invalidate_result,
        )

    with c4:
        subject_title("한국사")
        hist_grade = st.selectbox(
            "한국사 등급",
            ["미선택"] + list(range(1, 10)),
            key="hist_grade",
            on_change=invalidate_result,
        )

    st.divider()

    iq1, iq2 = st.columns(2)
    with iq1:
        subject_title("탐구 01")
        sc1, sc2 = st.columns([1.4, 1])
        with sc1:
            inq1_subj = st.selectbox(
                "탐구 1 과목", INQUIRY_SUBJECTS, key="inq1_subj", on_change=invalidate_result
            )
        with sc2:
            inq1_score = number_input("탐구 1 백분위", "inq1")

    with iq2:
        subject_title("탐구 02")
        sc3, sc4 = st.columns([1.4, 1])
        with sc3:
            inq2_subj = st.selectbox(
                "탐구 2 과목", INQUIRY_SUBJECTS, key="inq2_subj", on_change=invalidate_result
            )
        with sc4:
            inq2_score = number_input("탐구 2 백분위", "inq2")

    if st.button("환산 점수 산출 및 입시 결과 비교", type="primary", use_container_width=True):
        errors = []
        if eng_grade == "미선택":
            errors.append("영어 등급을 선택하세요.")
        if hist_grade == "미선택":
            errors.append("한국사 등급을 선택하세요.")
        if inq1_subj == "선택안함" and inq1_score > 0:
            errors.append("탐구 1 과목을 선택하세요.")
        if inq2_subj == "선택안함" and inq2_score > 0:
            errors.append("탐구 2 과목을 선택하세요.")
        if inq1_subj == inq2_subj and inq1_subj not in ("선택안함", "직업탐구"):
            errors.append("탐구 1과 탐구 2에 같은 과목이 선택되어 있습니다. 실제 응시 과목을 확인하세요.")

        if errors:
            invalidate_result()
            for error in errors:
                st.error(error)
        else:
            st.session_state.result = calculate_score(
                selected_dept, kor_score, math_subj, math_score,
                eng_grade, hist_grade,
                inq1_subj, inq1_score, inq2_subj, inq2_score,
            )

# ==================================================
# 7. 결과 출력 (50:50 균등 비율 적용)
# ==================================================
result = st.session_state.result

if result is None:
    st.markdown(
        """
        <div class="empty-state">
            <strong>입력한 성적을 바탕으로 상담 결과를 확인하세요</strong>
            모집단위와 성적을 입력한 후 산출 버튼을 누르면<br>
            환산 점수 · 반영 영역 · 최근 3개년 비교 결과가 표시됩니다.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

history = build_history(record) if record is not None and data_scale else pd.DataFrame()

# 03, 04번 영역 비율 50:50 균등 정렬
result_col, comparison_col = st.columns([1, 1], gap="large")

with result_col:
    with st.container(border=True):
        section_title("03", "환산 점수")

        st.markdown(
            f"""
            <div class="score-hero">
                <div class="score-label">{escape(selected_dept)}</div>
                <div class="score-number">{result["score"]:.2f} <small>점</small></div>
                <div class="score-footer">
                    100점 기준 환산값<br>
                    1,000점 기준 <b>{result["score1000"]:,.2f}점</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        first_name, first_score = result["first"]
        second_name, second_score = result["second"]

        f_col, s_col = st.columns(2)
        with f_col:
            st.metric(f"60% 반영 · {first_name}", f"{first_score * 0.6:.2f}")
            st.caption(f"{first_score:.2f} × 60%")
        with s_col:
            st.metric(f"40% 반영 · {second_name}", f"{second_score * 0.4:.2f}")
            st.caption(f"{second_score:.2f} × 40%")

        with st.expander("산출 근거 자세히 보기"):
            detail = pd.DataFrame({
                "반영 영역": [first_name, second_name],
                "가산·등급 환산 후 점수": [f"{first_score:.2f}", f"{second_score:.2f}"],
                "반영 비율": ["60%", "40%"],
                "반영 점수": [f"{first_score * 0.6:.2f}", f"{second_score * 0.4:.2f}"],
            })
            st.dataframe(detail, hide_index=True, use_container_width=True)

with comparison_col:
    with st.container(border=True):
        section_title("04", "전년도 입시 결과 비교")

        if record is not None and not data_scale and not db.empty:
            st.warning("점수 단위를 판별하지 못해 비교를 표시하지 않습니다.")
        elif history.empty:
            st.info("비교할 입시 결과 데이터가 없습니다.")
        else:
            recent = history[history["연도"] == "2026"].iloc[0]
            max_score = to_number(recent["최고"])
            avg_score = to_number(recent["평균"])
            cut_score = to_number(recent["최저"])

            m_cols = st.columns(3)
            for col, lbl, val in zip(
                m_cols,
                ["2026 최고점", "2026 평균점", "2026 최저점"],
                [max_score, avg_score, cut_score],
            ):
                with col:
                    st.metric(lbl, display_number(val))

            valid_history = all(
                v is not None and 0 <= v <= 1000
                for v in (max_score, avg_score, cut_score)
            )
            ordered_history = valid_history and max_score >= avg_score >= cut_score

            if ordered_history:
                score = result["score"]

                if score >= max_score:
                    msg, bg, c = "전년도 최고점 이상", "#E8F4F0", "#0B5A40"
                elif score >= avg_score:
                    msg, bg, c = "전년도 평균점 이상", "#E9EDF8", "#082070"
                elif score >= cut_score:
                    msg, bg, c = "전년도 최저점 이상 · 평균점 미만", "#FEF4E6", "#96520B"
                else:
                    msg, bg, c = "전년도 최저점 미만", "#FDEEEF", "#9F1A2C"

                st.markdown(
                    f"""
                    <div class="status" style="background:{bg}; color:{c};">
                        {msg}<br>
                        <span style="font-size:14px; font-weight:700;">
                            전년도 평균 대비 {score - avg_score:+.2f}점
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                def gap_text(target):
                    diff = score - target
                    if abs(diff) < 0.005:
                        return "동일"
                    return f"{abs(diff):,.2f}점 {'초과' if diff > 0 else '부족'}"

                gap_table = pd.DataFrame({
                    "비교 기준": ["2026 최고점", "2026 평균점", "2026 최저점"],
                    "전년도 점수(100점)": [f"{v:,.2f}" for v in (max_score, avg_score, cut_score)],
                    "내 점수와의 차이": [gap_text(v) for v in (max_score, avg_score, cut_score)],
                })

                def color_gap(val):
                    val_str = str(val)
                    if "부족" in val_str:
                        return "color: #E11D48; font-weight: 800;"
                    if "초과" in val_str:
                        return "color: #1D3FA0; font-weight: 800;"
                    return ""

                styled_gap = gap_table.style
                if hasattr(styled_gap, "map"):
                    styled_gap = styled_gap.map(color_gap, subset=["내 점수와의 차이"])
                else:
                    styled_gap = styled_gap.applymap(color_gap, subset=["내 점수와의 차이"])

                st.dataframe(styled_gap, hide_index=True, use_container_width=True)

            elif all(v is not None for v in (max_score, avg_score, cut_score)):
                st.warning(
                    "2026년 최고·평균·최저 점수의 값 또는 순서가 올바르지 않아 "
                    "판정 문구를 표시하지 않습니다. 원본 입시 결과 자료를 확인해 주세요."
                )
            else:
                st.info("2026년 최고·평균·최저 점수 중 일부가 없어 비교 판정을 표시하지 않습니다.")

# ==================================================
# 8. 결과 출력 (05, 06번 영역 비율 50:50 균등 정렬)
# ==================================================
if not history.empty:
    chart_col, table_col = st.columns([1, 1], gap="large")

    with chart_col:
        with st.container(border=True):
            section_title("05", "최근 3개년 점수 분포")

            c_data = history[["연도", "최고", "평균", "최저"]].copy()

            if c_data[["최고", "평균", "최저"]].notna().any().any():
                chart_values = [
                    value
                    for value in c_data[["최고", "평균", "최저"]].to_numpy().ravel().tolist()
                    if pd.notna(value)
                ]
                chart_values.append(float(result["score"]))

                x_min, x_max = min(chart_values), max(chart_values)
                pad = max((x_max - x_min) * 0.12, 1.0)
                domain_min = max(0, x_min - pad)
                domain_max = min(100, x_max + pad)
                if domain_max - domain_min < 2:
                    domain_min = max(0, domain_min - 1)
                    domain_max = min(100, domain_max + 1)

                chart_data = c_data.copy()
                chart_data["연도"] = chart_data["연도"].astype(str)

                y_encoding = alt.Y(
                    "연도:N",
                    title=None,
                    sort=["2026", "2025", "2024"],
                    axis=alt.Axis(
                        labelAngle=0,
                        labelFontSize=13,
                        labelFontWeight=700,
                        labelColor="#34415E",
                        ticks=False,
                        domain=False,
                        grid=True,
                        gridColor="#EEF1F7",
                        gridWidth=1,
                    ),
                )

                base = alt.Chart(chart_data).encode(y=y_encoding)

                x_scale = alt.Scale(domain=[domain_min, domain_max], zero=False, nice=False)

                range_rule = base.mark_rule(
                    color="#CBD5E5", strokeWidth=5, strokeCap="round"
                ).encode(
                    x=alt.X(
                        "최저:Q",
                        title="환산점수 · 100점 기준",
                        scale=x_scale,
                        axis=alt.Axis(
                            titleFontSize=12,
                            titleFontWeight=600,
                            titleColor="#64708A",
                            titlePadding=14,
                            labelFontSize=11,
                            labelColor="#64708A",
                            tickCount=6,
                            grid=True,
                            gridColor="#E9EDF5",
                            gridDash=[2, 3],
                            domain=False,
                            tickSize=0,
                            format=".1f",
                        ),
                    ),
                    x2="최고:Q",
                    tooltip=[
                        alt.Tooltip("연도:N", title="학년도"),
                        alt.Tooltip("최고:Q", format=".2f", title="최고점"),
                        alt.Tooltip("평균:Q", format=".2f", title="평균점"),
                        alt.Tooltip("최저:Q", format=".2f", title="최저점"),
                    ],
                )

                min_point = base.mark_point(
                    filled=True, color="#0F9D91", size=90, stroke="#FFFFFF", strokeWidth=1.5
                ).encode(
                    x=alt.X("최저:Q", scale=x_scale, axis=None),
                    tooltip=[
                        alt.Tooltip("연도:N", title="학년도"),
                        alt.Tooltip("최저:Q", format=".2f", title="최저점"),
                    ],
                )

                max_point = base.mark_point(
                    filled=True, color="#3157C8", size=90, stroke="#FFFFFF", strokeWidth=1.5
                ).encode(
                    x=alt.X("최고:Q", scale=x_scale, axis=None),
                    tooltip=[
                        alt.Tooltip("연도:N", title="학년도"),
                        alt.Tooltip("최고:Q", format=".2f", title="최고점"),
                    ],
                )

                avg_point = base.mark_point(
                    filled=True, color="#14264D", shape="diamond", size=145,
                    stroke="#FFFFFF", strokeWidth=1,
                ).encode(
                    x=alt.X("평균:Q", scale=x_scale, axis=None),
                    tooltip=[
                        alt.Tooltip("연도:N", title="학년도"),
                        alt.Tooltip("평균:Q", format=".2f", title="평균점"),
                    ],
                )

                max_txt = base.mark_text(
                    align="left", dx=8, dy=-10, fontSize=11, color="#2447A8", fontWeight=700
                ).encode(
                    x=alt.X("최고:Q", scale=x_scale, axis=None),
                    text=alt.Text("최고:Q", format=".2f"),
                )

                min_txt = base.mark_text(
                    align="right", dx=-8, dy=10, fontSize=11, color="#087F75", fontWeight=700
                ).encode(
                    x=alt.X("최저:Q", scale=x_scale, axis=None),
                    text=alt.Text("최저:Q", format=".2f"),
                )

                my_score_df = pd.DataFrame({"내 점수": [float(result["score"])]})
                my_line = alt.Chart(my_score_df).mark_rule(
                    color="#E5485D", strokeWidth=2, strokeDash=[5, 4], opacity=0.95
                ).encode(
                    x=alt.X("내 점수:Q", scale=x_scale, axis=None),
                    tooltip=[alt.Tooltip("내 점수:Q", title="내 환산점수", format=".2f")],
                )

                chart = (
                    alt.layer(range_rule, min_point, max_point, avg_point, min_txt, max_txt, my_line)
                    .properties(
                        height=330,
                        padding={"left": 8, "right": 24, "top": 14, "bottom": 4},
                    )
                    .configure_view(stroke=None, fill="#FFFFFF")
                    .configure_axis(
                        labelFont="Malgun Gothic, sans-serif",
                        titleFont="Malgun Gothic, sans-serif",
                    )
                )

                st.altair_chart(chart, use_container_width=True)

                st.markdown(
                    "<div style='width:100%;text-align:center;margin-top:2px;font-size:12px;line-height:1.6;'>"
                    "<span style='color:#3157C8;font-weight:700;'>● 최고점</span> "
                    "<span style='color:#087F75;font-weight:700;'>● 최저점</span> "
                    "<span style='color:#14264D;font-weight:700;'>◆ 평균점</span> "
                    "<span style='color:#E5485D;font-weight:700;'>┆ 내 점수</span>"
                    "</div>",
                    unsafe_allow_html=True,
                )

    with table_col:
        with st.container(border=True):
            section_title("06", "3개년 입시 결과")

            table = history.sort_values("연도", ascending=False).copy()
            table["학년도"] = table["연도"] + "학년도"
            table["경쟁률"] = table["경쟁률"].map(display_ratio)
            table["추가합격"] = table["추가합격"].map(display_count)
            for c in ("최고", "평균", "최저"):
                table[c] = table[c].map(display_number)

            st.dataframe(
                table[["학년도", "최고", "평균", "최저", "경쟁률", "추가합격"]],
                hide_index=True,
                use_container_width=True,
            )

# ==================================================
# 9. 모집단위 추천 및 모집단위 비교
# ==================================================
if not db.empty and data_scale and result is not None:
    st.divider()
    st.markdown(
        '<div class="section-title"><span class="step">07</span>모집단위 추천 및 비교</div>',
        unsafe_allow_html=True,
    )

    def make_dept_analysis(dept_name):
        matches = db[db["모집단위명"] == dept_name]
        if matches.empty:
            return None

        dept_record = matches.iloc[0]
        dept_score = calculate_score(
            dept_name, kor_score, math_subj, math_score,
            eng_grade, hist_grade,
            inq1_subj, inq1_score, inq2_subj, inq2_score,
        )

        dept_history = build_history(dept_record)
        hist_by_year = {}

        for _, hist_row in dept_history.iterrows():
            year_str = str(hist_row["연도"])
            mx = to_number(hist_row.get("최고"))
            av = to_number(hist_row.get("평균"))
            mn = to_number(hist_row.get("최저"))

            status = "자료 없음"
            if av is not None and mn is not None and mx is not None:
                if dept_score["score"] >= av:
                    status = "안정"
                elif dept_score["score"] >= mn:
                    status = "적정·경계"
                else:
                    status = "상향"

            hist_by_year[year_str] = {"최고": mx, "평균": av, "최저": mn, "판정": status}

        recent = hist_by_year.get("2026", {})
        recent_avg = recent.get("평균")
        recent_min = recent.get("최저")
        recent_max = recent.get("최고")

        if recent_avg is None or recent_min is None or recent_max is None:
            recommendation = "자료 확인 필요"
            rationale = "2026학년도 최고·평균·최저 점수 중 일부가 없습니다."
            gap_to_avg = None
            gap_to_min = None
        else:
            gap_to_avg = round(dept_score["score"] - recent_avg, 2)
            gap_to_min = round(dept_score["score"] - recent_min, 2)
            recommendation = recent.get("판정", "자료 확인 필요")

            if recommendation == "안정":
                rationale = f"현재 환산점수가 2026 평균보다 {gap_to_avg:+.2f}점입니다."
            elif recommendation == "적정·경계":
                rationale = f"2026 최저점 이상, 평균점 미만입니다(평균 대비 {gap_to_avg:+.2f}점)."
            else:
                rationale = f"현재 환산점수가 2026 최저점보다 {abs(gap_to_min):.2f}점 낮습니다."

        return {
            "모집단위": dept_name,
            "현재 환산점수": dept_score["score"],
            "분류": recommendation,
            "2026 최고": recent_max,
            "2026 평균": recent_avg,
            "2026 최저": recent_min,
            "평균 대비": gap_to_avg,
            "최저 대비": gap_to_min,
            "안내": rationale,
            "연도별": hist_by_year,
        }

    analysis_by_dept = {}
    for dept_name in departments:
        analysis = make_dept_analysis(dept_name)
        if analysis is not None:
            analysis_by_dept[dept_name] = analysis

    recommendation_tab, comparison_tab = st.tabs(["① 모집단위 추천", "② 모집단위 비교"])

    with recommendation_tab:
        st.markdown("#### 현재 점수 기준 추천 목록")
        st.caption(
            "분류 기준: 현재 점수 ≥ 2026 평균 이상 → 안정 / "
            "2026 최저 이상~평균 미만 → 적정·경계 / 2026 최저 미만 → 상향"
        )

        recommendation_rows = []
        for item in analysis_by_dept.values():
            if item["분류"] == "자료 확인 필요":
                continue
            recommendation_rows.append({
                "분류": item["분류"],
                "모집단위": item["모집단위"],
                "내 환산점수": item["현재 환산점수"],
                "2026 평균": item["2026 평균"],
                "평균 대비": item["평균 대비"],
                "2026 최저": item["2026 최저"],
                "최저 대비": item["최저 대비"],
                "분류 근거": item["안내"],
            })

        if recommendation_rows:
            rec_df = pd.DataFrame(recommendation_rows)
            rec_order = {"안정": 0, "적정·경계": 1, "상향": 2}
            rec_df["_order"] = rec_df["분류"].map(rec_order)
            rec_df = (
                rec_df.sort_values(["_order", "평균 대비"], ascending=[True, False])
                .drop(columns="_order")
            )

            def style_recommendation_cell(value):
                value_text = str(value)
                if value_text == "안정":
                    return "color: #059669; font-weight: 800;"
                if value_text == "적정·경계":
                    return "color: #DC2626; font-weight: 800;"
                if value_text == "상향":
                    return "color: #1D4ED8; font-weight: 800;"
                return ""

            styled_rec = rec_df.style.format(
                {
                    "내 환산점수": "{:.2f}",
                    "2026 평균": "{:.2f}",
                    "평균 대비": "{:+.2f}",
                    "2026 최저": "{:.2f}",
                    "최저 대비": "{:+.2f}",
                },
                na_rep="—",
            )
            if hasattr(styled_rec, "map"):
                styled_rec = styled_rec.map(style_recommendation_cell, subset=["분류"])
            else:
                styled_rec = styled_rec.applymap(style_recommendation_cell, subset=["분류"])

            st.dataframe(styled_rec, hide_index=True, use_container_width=True, height=420)
        else:
            st.info("추천 분류에 필요한 2026학년도 입시 결과가 충분하지 않습니다.")

    with comparison_tab:
        st.markdown("#### 모집단위별 점수·입결 비교")

        compare_options = list(analysis_by_dept.keys())
        default_compare = [selected_dept] if selected_dept in compare_options else compare_options[:1]

        compare_depts = st.multiselect(
            "비교할 모집단위 선택 (최대 4개)",
            options=compare_options,
            default=default_compare,
            max_selections=4,
            key="compare_departments",
        )

        if compare_depts:
            metrics = [
                ("현재 환산점수", None, "current"),
                ("2026학년도", "2026", "year"),
                (" 최고", ("2026", "최고"), "metric"),
                (" 평균", ("2026", "평균"), "metric"),
                (" 최저", ("2026", "최저"), "metric"),
                ("2025학년도", "2025", "year"),
                (" 최고", ("2025", "최고"), "metric"),
                (" 평균", ("2025", "평균"), "metric"),
                (" 최저", ("2025", "최저"), "metric"),
                ("2024학년도", "2024", "year"),
                (" 최고", ("2024", "최고"), "metric"),
                (" 평균", ("2024", "평균"), "metric"),
                (" 최저", ("2024", "최저"), "metric"),
            ]

            row_types = []
            compare_rows = []

            for metric_label, metric_key, row_type in metrics:
                row = {"비교 항목": metric_label}
                row_types.append(row_type)

                for dept_name in compare_depts:
                    item = analysis_by_dept[dept_name]

                    if row_type == "current":
                        value = f"{item['현재 환산점수']:.2f}"
                    elif row_type == "year":
                        yr_status = item["연도별"].get(metric_key, {}).get("판정", "")
                        value = f"[{yr_status}]" if yr_status and yr_status != "자료 없음" else ""
                    else:
                        year, label = metric_key
                        raw = item["연도별"].get(year, {}).get(label)
                        value = f"{raw:.2f}" if raw is not None else "—"

                    row[dept_name] = value

                compare_rows.append(row)

            compare_df = pd.DataFrame(compare_rows)

            def style_comparison_rows(row):
                row_type = row_types[row.name]
                styles = []
                for val in row:
                    val_str = str(val)
                    if row_type == "year":
                        base_style = (
                            "background-color: #E8EEF8; font-weight: bold; "
                            "border-top: 2px solid #9DB2D1;"
                        )
                        if "[상향]" in val_str:
                            styles.append(base_style + " color: #1D4ED8;")
                        elif "[안정]" in val_str:
                            styles.append(base_style + " color: #059669;")
                        elif "[적정·경계]" in val_str:
                            styles.append(base_style + " color: #DC2626;")
                        else:
                            styles.append(base_style + " color: #17365D;")
                    elif row_type == "current":
                        styles.append("background-color: #F4F7FB; font-weight: bold; color: #082070;")
                    else:
                        styles.append("")
                return styles

            styled_compare_df = compare_df.style.apply(style_comparison_rows, axis=1)
            st.dataframe(styled_compare_df, hide_index=True, use_container_width=True)
        else:
            st.info("비교할 모집단위를 하나 이상 선택해 주세요.")
