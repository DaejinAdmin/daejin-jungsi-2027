import math
import os
import re
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
# 2. 디자인 (AI 클리셰 제거 · 대학 공식 엔터프라이즈 플랫 UI)
# ==================================================
st.markdown(
    """
<style>
    :root {
        --navy: #0F2557; --navy-deep: #091738; --primary: #1E40AF; --tint: #F1F5F9;
        --silver: #E2E8F0; --text: #0F172A; --muted: #475569; --line: #CBD5E1; --bg: #F8FAFC;
    }
    #MainMenu, footer, header { visibility: hidden; }
    .stApp {
        background: var(--bg); color: var(--text);
        font-family: "Pretendard", "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
    }
    .stApp::before {
        content: ""; position: fixed; top: 0; left: 0; right: 0; height: 3px; z-index: 999999;
        background: var(--navy);
    }
    .block-container {
        max-width: 1480px; padding-top: 2.2rem; padding-bottom: 2.4rem;
        padding-left: clamp(1rem, 2.5vw, 2.2rem); padding-right: clamp(1rem, 2.5vw, 2.2rem);
    }
    h1, h2, h3, h4 { color: var(--text) !important; letter-spacing: -0.4px; }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #FFFFFF;
        border: 1px solid var(--line) !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
    }
    [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stVerticalBlockBorderWrapper"] * {
        scrollbar-width: none !important;
        -ms-overflow-style: none !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"]::-webkit-scrollbar,
    [data-testid="stVerticalBlockBorderWrapper"] *::-webkit-scrollbar {
        display: none !important;
        width: 0 !important;
        height: 0 !important;
    }

    /* 03, 04번 마스터 카드 (높이 565px 고정 대칭 · 엔터프라이즈 상단 보더) */
    .master-card {
        background-color: #FFFFFF;
        border: 1px solid var(--line);
        border-top: 3px solid var(--navy);
        border-radius: 8px;
        padding: 20px 22px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        height: 565px;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        margin-bottom: 16px;
    }

    /* 05, 06번 마스터 카드 (높이 440px 고정 대칭) */
    .master-card-056 {
        background-color: #FFFFFF;
        border: 1px solid var(--line);
        border-top: 3px solid var(--navy);
        border-radius: 8px;
        padding: 20px 22px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        height: 440px;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        margin-bottom: 16px;
        overflow: hidden;
    }

    /* 04번 상단 3열 최고/평균/최저 메트릭 (구분선 그리드 적용) */
    .top3-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0px;
        margin: 4px 0 14px;
        background: #F8FAFC;
        border: 1px solid var(--line);
        border-radius: 6px;
        padding: 12px 0;
        flex-shrink: 0;
    }
    .top3-grid > div {
        padding: 0 16px;
        border-right: 1px solid var(--silver);
    }
    .top3-grid > div:last-child {
        border-right: none;
    }
    .top3-lbl {
        color: var(--muted);
        font-size: 12.5px;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .top3-val {
        font-size: clamp(22px, 2vw, 26px);
        font-weight: 800;
        font-variant-numeric: tabular-nums;
        line-height: 1.15;
    }
    .top3-max { color: #1E40AF; }
    .top3-avg { color: #0F172A; }
    .top3-min { color: #047857; }

    [data-testid="stImage"] img {
        background: #FFFFFF; padding: 4px; border-radius: 8px;
        border: 1px solid var(--line);
    }

    [data-testid="stWidgetLabel"] p {
        color: var(--text) !important; font-size: 13.5px !important;
        font-weight: 700 !important; line-height: 1.45 !important;
    }
    [data-testid="stWidgetLabel"] { min-height: 1.25rem; }

    [data-testid="stNumberInput"] input {
        background: #FFFFFF !important; border: 1px solid var(--line) !important;
        color: var(--text) !important; font-size: 17px !important; font-weight: 750 !important;
        min-height: 42px; border-radius: 6px;
    }
    [data-testid="stNumberInput"] input:focus {
        border-color: var(--navy) !important; box-shadow: 0 0 0 2px rgba(15, 37, 87, 0.12) !important;
    }
    [data-baseweb="select"] > div {
        background: #FFFFFF !important; border: 1px solid var(--line) !important;
        border-radius: 6px !important; color: var(--text) !important;
        min-height: 42px; font-weight: 600;
    }
    [data-baseweb="select"] > div:focus-within {
        border-color: var(--navy) !important; box-shadow: 0 0 0 2px rgba(15, 37, 87, 0.12) !important;
    }

    [data-testid="stButton"] button {
        border-radius: 6px !important; min-height: 46px; font-weight: 700 !important;
        letter-spacing: -0.2px; transition: background .12s ease;
    }
    [data-testid="stButton"] button[kind="primary"] {
        background: var(--navy) !important;
        border: 1px solid var(--navy) !important; color: #FFFFFF !important;
        box-shadow: none !important;
    }
    [data-testid="stButton"] button[kind="primary"]:hover {
        background: var(--navy-deep) !important;
    }
    [data-testid="stButton"] button[kind="secondary"] {
        border: 1px solid var(--line) !important; color: var(--text) !important; background: #FFFFFF !important;
    }
    [data-testid="stButton"] button[kind="secondary"]:hover {
        border-color: var(--navy) !important; background: var(--tint) !important;
    }

    .eyebrow {
        display: inline-block; background: var(--tint); color: var(--navy);
        border: 1px solid var(--line); border-radius: 4px; padding: 2px 8px;
        font-size: 11.5px; font-weight: 700; letter-spacing: 0px; margin-bottom: 6px;
    }
    .page-title {
        color: #0F172A; font-size: clamp(24px, 2.8vw, 34px); font-weight: 850;
        letter-spacing: -0.8px; line-height: 1.25; margin: 0;
        text-align: center;
    }
    .section-title {
        display: flex; align-items: center; gap: 8px; color: #0F172A;
        font-size: 17.5px; font-weight: 800; margin: 0px 0 12px;
        padding-bottom: 8px; border-bottom: 1px solid var(--silver); flex-shrink: 0;
    }
    .step {
        display: inline-flex; align-items: center; justify-content: center;
        padding: 2px 7px; border-radius: 4px;
        background: var(--navy); color: #FFFFFF; font-size: 12px; font-weight: 800; flex-shrink: 0;
    }
    .subject-title {
        font-size: 14.5px; color: var(--text); font-weight: 800;
        border-left: 3px solid var(--navy); padding-left: 8px;
        margin: 3px 0 10px; min-height: 22px; line-height: 1.5; box-sizing: border-box;
    }

    .rule-strip {
        display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 14px 0 18px;
    }
    .rule-item {
        padding: 13px 16px; border-radius: 6px;
        font-size: 13.5px; color: var(--muted); line-height: 1.55;
        background: #FFFFFF; border: 1px solid var(--line); border-left: 3px solid var(--navy);
    }
    .rule-item strong { font-size: 14.5px; color: var(--text); margin-bottom: 3px; display: block; font-weight: 800; }

    /* 03번 상단 학과 산출성적 (AI 빛무리 제거 · 솔리드 네이비 패널) */
    .score-hero {
        background: var(--navy);
        border: 1px solid var(--navy-deep);
        border-radius: 6px; padding: 16px 20px; color: #FFFFFF; margin-bottom: 12px;
        flex-shrink: 0;
    }
    .score-label { font-size: 13px; font-weight: 600; color: #CBD5E1; }
    .score-number {
        font-size: clamp(32px, 3vw, 42px); font-weight: 850; letter-spacing: -1px;
        line-height: 1.15; margin: 4px 0 6px; font-variant-numeric: tabular-nums;
    }
    .score-number small { font-size: 16px; font-weight: 600; color: #CBD5E1; letter-spacing: 0; }
    .score-footer {
        border-top: 1px solid rgba(255,255,255,0.14); padding-top: 7px;
        color: #E2E8F0; font-size: 12.5px; line-height: 1.4;
    }

    /* 03번 중단 60%, 40% 인라인 요약 박스 */
    .sub-metric-grid {
        display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 12px; flex-shrink: 0;
    }
    .sub-metric-box {
        background: #F8FAFC; border: 1px solid var(--line); border-radius: 6px; padding: 10px 14px;
    }
    .sub-metric-lbl {
        font-size: 12.5px; font-weight: 700; color: var(--muted); margin-bottom: 3px;
    }
    .sub-metric-val-row {
        display: flex; align-items: baseline; gap: 6px; flex-wrap: wrap;
    }
    .sub-metric-val {
        font-size: 21px; font-weight: 800; color: var(--text); font-variant-numeric: tabular-nums; line-height: 1.2;
    }
    .sub-metric-calc {
        font-size: 12.5px; font-weight: 600; color: var(--muted); font-variant-numeric: tabular-nums;
    }

    /* 03번 하단: 전 영역 환산 및 반영 판정 보드 */
    .audit-wrap {
        flex: 1; display: flex; flex-direction: column; justify-content: flex-end;
    }
    .audit-header {
        font-size: 12.5px; font-weight: 700; color: var(--muted); margin: 0px 0 6px 2px;
        display: flex; align-items: center; justify-content: space-between;
    }
    .audit-grid {
        flex: 1; display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: repeat(3, 1fr); gap: 6px;
    }
    .audit-item {
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 12px; border-radius: 6px; border: 1px solid var(--line); background: #FFFFFF;
        font-size: 13px;
    }
    .audit-item.active-60 {
        border-left: 3px solid var(--navy); background: #F8FAFC;
    }
    .audit-item.active-40 {
        border-left: 3px solid #047857; background: #F8FAFC;
    }
    .audit-item.dropped {
        background: #FFFFFF; opacity: 0.78;
    }
    .audit-left { display: flex; flex-direction: column; gap: 1px; min-width: 0; }
    .audit-subj { font-weight: 750; color: var(--text); font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .audit-raw { font-size: 11px; color: var(--muted); font-weight: 500; font-variant-numeric: tabular-nums; }
    .audit-right { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }
    .audit-conv { font-size: 13.5px; font-weight: 800; color: var(--text); font-variant-numeric: tabular-nums; }
    .tag-60 { background: var(--tint); color: var(--navy); border: 1px solid var(--line); font-size: 11px; font-weight: 700; padding: 1.5px 6px; border-radius: 4px; }
    .tag-40 { background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; font-size: 11px; font-weight: 700; padding: 1.5px 6px; border-radius: 4px; }
    .tag-drop { background: #F1F5F9; color: #64748B; font-size: 11px; font-weight: 600; padding: 1.5px 6px; border-radius: 4px; }

    /* 04번 판정 배너 (파스텔 배경 대신 화이트 카드 + 좌측 4px 상태 바) */
    .status {
        border: 1px solid var(--line); border-left-width: 4px;
        border-radius: 6px; padding: 13px 16px; margin: 0 0 12px 0;
        background: #FFFFFF !important;
        font-size: 15px; font-weight: 800; line-height: 1.5; flex-shrink: 0;
    }
    .cmp-list {
        flex: 1; display: flex; flex-direction: column; justify-content: space-between; gap: 8px; margin-top: 0;
    }
    .cmp-row {
        flex: 1; display: flex; align-items: center; justify-content: space-between;
        padding: 0 14px; background: #F8FAFC; border: 1px solid var(--line);
        border-radius: 6px;
    }
    .cmp-lbl { font-size: 14px; font-weight: 700; color: var(--text); }
    .cmp-val-group { display: flex; align-items: center; gap: 10px; }
    .cmp-score { font-size: 16.5px; font-weight: 800; color: var(--text); font-variant-numeric: tabular-nums; }
    .pill-badge {
        padding: 3px 9px; border-radius: 4px; font-size: 12.5px; font-weight: 750;
        font-variant-numeric: tabular-nums; display: inline-flex; align-items: center;
    }
    .pill-plus { background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }
    .pill-minus { background: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA; }
    .pill-same { background: #F1F5F9; color: var(--text); border: 1px solid var(--line); }

    .empty-state {
        text-align: center; padding: 44px 20px; background: #FFFFFF;
        border: 1px solid var(--line); border-radius: 8px; color: var(--muted); line-height: 1.8;
    }
    .empty-state strong { display: block; color: var(--text); font-size: 17px; font-weight: 800; margin-bottom: 6px; }

    div[data-testid="stHorizontalBlock"] { align-items: stretch; }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] { min-width: 0; }

    /* 06번 3개년 요약 카드 */
    .yr-card-list {
        flex: 1; display: flex; flex-direction: column; justify-content: space-between; gap: 8px; margin-top: 2px;
    }
    .yr-card {
        flex: 1; display: flex; flex-direction: column; justify-content: center;
        background: #F8FAFC; border: 1px solid var(--line);
        border-radius: 6px; padding: 8px 14px;
    }
    .yr-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 5px; flex-wrap: wrap; gap: 6px; }
    .yr-title { font-size: 14.5px; font-weight: 800; color: var(--text); }
    .yr-tags { display: flex; gap: 6px; }
    .yr-tag {
        font-size: 12px; font-weight: 600; padding: 1.5px 8px; border-radius: 4px;
        background: #FFFFFF; border: 1px solid var(--line); color: var(--muted);
    }
    .yr-tag b { color: var(--text); font-weight: 800; }
    .yr-metrics {
        display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px;
        background: #FFFFFF; border: 1px solid var(--silver); border-radius: 4px; padding: 5px 8px; text-align: center;
    }
    .yr-m-lbl { font-size: 11.5px; font-weight: 600; color: var(--muted); margin-bottom: 1px; }
    .yr-m-val { font-size: 15.5px; font-weight: 800; color: var(--text); font-variant-numeric: tabular-nums; line-height: 1.25; }

    /* 07번 칸반 보드 & 스펙 카드 (안정=초록, 적정·경계=앰버, 상향=레드 시맨틱 통일) */
    .kb-header {
        display: flex; align-items: center; justify-content: space-between;
        padding: 10px 14px; border-radius: 6px; margin-bottom: 8px; font-weight: 800; font-size: 15px;
        background: #FFFFFF; border: 1px solid var(--line); border-top-width: 3px;
    }
    .kb-safe { border-top-color: #059669; color: #065F46; }
    .kb-fit { border-top-color: #D97706; color: #92400E; }
    .kb-up { border-top-color: #DC2626; color: #991B1B; }
    .kb-cnt {
        background: var(--tint); padding: 2px 8px; border-radius: 4px; font-size: 12.5px;
        font-weight: 700; color: var(--text);
    }
    .kb-card {
        background: #FFFFFF; border: 1px solid var(--line); border-radius: 6px;
        padding: 12px 14px; margin-bottom: 8px;
    }
    .kb-card:hover { border-color: var(--navy); }
    .kb-card-top { display: flex; align-items: center; justify-content: space-between; gap: 6px; margin-bottom: 6px; }
    .kb-dept { font-size: 15px; font-weight: 800; color: var(--text); }
    .kb-quota { font-size: 12px; font-weight: 600; color: var(--muted); background: var(--bg); border: 1px solid var(--silver); padding: 1.5px 7px; border-radius: 4px; flex-shrink: 0; }
    .kb-scores {
        display: flex; align-items: center; justify-content: space-between;
        font-size: 12.5px; color: var(--muted); background: #F8FAFC; padding: 6px 10px; border-radius: 4px; margin-bottom: 6px;
    }
    .kb-scores b { color: var(--text); font-weight: 800; font-size: 13px; }
    .kb-foot { display: flex; align-items: center; justify-content: space-between; font-size: 12px; font-weight: 750; }

    .spec-card {
        background: #FFFFFF; border: 1px solid var(--line); border-top: 3px solid var(--navy);
        border-radius: 6px; overflow: hidden; margin-top: 6px; margin-bottom: 8px;
    }
    .spec-top {
        background: #F8FAFC; border-bottom: 1px solid var(--line);
        color: var(--text); padding: 14px 16px; text-align: center;
    }
    .spec-dept { font-size: 17px; font-weight: 800; color: var(--navy); margin-bottom: 4px; letter-spacing: -0.3px; }
    .spec-quota {
        display: inline-block; font-size: 12px; font-weight: 600; color: var(--muted);
        background: #FFFFFF; border: 1px solid var(--line); padding: 2px 9px; border-radius: 4px; margin-bottom: 8px;
    }
    .spec-my-lbl { font-size: 12px; color: var(--muted); font-weight: 600; }
    .spec-my-val { font-size: 24px; font-weight: 850; color: var(--text); font-variant-numeric: tabular-nums; line-height: 1.2; margin-top: 2px; }
    .spec-body { padding: 12px; display: flex; flex-direction: column; gap: 8px; background: #FFFFFF; }
    .spec-yr-box { background: #F8FAFC; border: 1px solid var(--line); border-radius: 6px; padding: 9px 11px; }
    .spec-yr-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
    .spec-yr-name { font-size: 13.5px; font-weight: 800; color: var(--text); }
    .bdg-safe { background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 750; }
    .bdg-fit { background: #FFFBEB; color: #B45309; border: 1px solid #FDE68A; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 750; }
    .bdg-up { background: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 750; }
    .bdg-none { background: #F1F5F9; color: var(--muted); padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }

    [data-testid="stAlert"] { border-radius: 6px; }

    @media (max-width: 900px) {
        .block-container { padding-top: 1.5rem; }
        .rule-strip { grid-template-columns: 1fr; }
        .score-hero { padding: 16px; }
        .section-title { font-size: 16.5px; }
        .master-card, .master-card-056 { height: auto; }
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


def display_quota(value):
    if value is None or pd.isna(value):
        return "—"
    text = str(value).strip()
    if not text or text == "-":
        return "—"
    if "명" in text:
        return text
    number = to_number(text)
    if number is not None:
        return f"{int(number):,}명" if number.is_integer() else f"{number:,.1f}명"
    return text


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
# 5. 계산 함수 (원본 산출 공식 100% 보존)
# ==================================================
def calculate_score(dept, kor, math_subj, math_val, eng_g, hist_g,
                    inq1_subj, inq1, inq2_subj, inq2):
    engineering = dept in ENG_DEPTS
    math_bonus = engineering and math_subj in ("미적분", "기하")
    math_adj = math_val * (1.1 if math_bonus else 1)

    def inquiry_info(subj, value):
        if subj == "선택안함":
            return 0.0, False
        sci = any(name in subj for name in ("물리학", "화학", "생명과학", "지구과학"))
        bonus = engineering and sci
        return value * (1.07 if bonus else 1), bonus

    inq1_adj, inq1_bonus = inquiry_info(inq1_subj, inq1)
    inq2_adj, inq2_bonus = inquiry_info(inq2_subj, inq2)
    inquiry_scores = [inq1_adj, inq2_adj]
    best_inquiry = max(range(2), key=lambda index: inquiry_scores[index])

    eng_score = GRADE_MAP.get(eng_g, 0)
    hist_score = GRADE_MAP.get(hist_g, 0)

    primary = [("국어", kor), ("수학", math_adj), ("영어", eng_score)]
    first_index = max(range(3), key=lambda index: primary[index][1])
    first = primary[first_index]

    remaining = [item for index, item in enumerate(primary) if index != first_index]
    remaining += [
        (f"탐구 {best_inquiry + 1}", inquiry_scores[best_inquiry]),
        ("한국사", hist_score),
    ]
    second = max(remaining, key=lambda item: item[1])

    raw_score = first[1] * 0.6 + second[1] * 0.4

    all_subjects = [
        {
            "key": "국어",
            "title": "국어",
            "raw": f"백분위 {kor:.0f}",
            "conv": kor,
            "role": "60% 반영" if first[0] == "국어" else ("40% 반영" if second[0] == "국어" else "미반영"),
        },
        {
            "key": "수학",
            "title": f"수학 ({math_subj})",
            "raw": f"백분위 {math_val:.0f}" + (" (+10%)" if math_bonus else ""),
            "conv": math_adj,
            "role": "60% 반영" if first[0] == "수학" else ("40% 반영" if second[0] == "수학" else "미반영"),
        },
        {
            "key": "영어",
            "title": "영어",
            "raw": f"{eng_g}등급 환산",
            "conv": float(eng_score),
            "role": "60% 반영" if first[0] == "영어" else ("40% 반영" if second[0] == "영어" else "미반영"),
        },
        {
            "key": "한국사",
            "title": "한국사",
            "raw": f"{hist_g}등급 환산",
            "conv": float(hist_score),
            "role": "40% 반영" if second[0] == "한국사" else "미반영",
        },
        {
            "key": "탐구 1",
            "title": f"탐구1 ({inq1_subj})" if inq1_subj != "선택안함" else "탐구1 (미선택)",
            "raw": (f"백분위 {inq1:.0f}" + (" (+7%)" if inq1_bonus else "")) if inq1_subj != "선택안함" else "미응시",
            "conv": inq1_adj,
            "role": "40% 반영" if second[0] == "탐구 1" else ("탐구상위" if best_inquiry == 0 and inq1_subj != "선택안함" else "미반영"),
        },
        {
            "key": "탐구 2",
            "title": f"탐구2 ({inq2_subj})" if inq2_subj != "선택안함" else "탐구2 (미선택)",
            "raw": (f"백분위 {inq2:.0f}" + (" (+7%)" if inq2_bonus else "")) if inq2_subj != "선택안함" else "미응시",
            "conv": inq2_adj,
            "role": "40% 반영" if second[0] == "탐구 2" else ("탐구상위" if best_inquiry == 1 and inq2_subj != "선택안함" else "미반영"),
        },
    ]

    return {
        "score": round(raw_score, 2),
        "score1000": round(raw_score * 10, 2),
        "first": first,
        "second": second,
        "engineering": engineering,
        "all_subjects": all_subjects,
    }


def get_record_value(record, keywords):
    matches = [c for c in record.index if all(kw in str(c) for kw in keywords)]
    if len(matches) == 1 and pd.notna(record[matches[0]]):
        return record[matches[0]]
    return None


def get_quota_value(record):
    if record is None:
        return None
    for kw_list in (["2027", "모집"], ["2027", "인원"], ["모집인원"], ["선발인원"], ["모집정원"], ["정원"], ["인원"]):
        matches = [
            c for c in record.index
            if all(kw in str(c) for kw in kw_list)
            and not any(yr in str(c) for yr in ("2024", "2025", "2026"))
            and "모집단위" not in str(c)
        ]
        if matches and pd.notna(record[matches[0]]):
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
head_c1, head_c2 = st.columns([0.8, 9.2], vertical_alignment="center")

with head_c1:
    logo_png = BASE_DIR / "logo.png"
    logo_jpg = BASE_DIR / "logo.jpg"
    if logo_png.exists():
        show_logo(str(logo_png))
    elif logo_jpg.exists():
        show_logo(str(logo_jpg))

with head_c2:
    st.markdown(
        '<div class="page-title" style="text-align: left; display: flex; align-items: center; min-height: 92px; margin: 0;">'
        '2027학년도 대진대학교 정시 입학상담 솔루션'
        '</div>',
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="rule-strip">
        <div class="rule-item"><strong>01 &nbsp; 우수 영역 60% 반영</strong>국어 · 수학 · 영어 중 백분위(환산) 최상위 1개 영역</div>
        <div class="rule-item"><strong>02 &nbsp; 차순위 영역 40% 반영</strong>60% 미반영 국·수·영, 탐구 상위 1과목, 한국사 중 최상위 1개 영역</div>
        <div class="rule-item"><strong>03 &nbsp; 이공계열 가산점 부여</strong>수학(미적분·기하) 10% 가산 / 과학탐구 7% 가산</div>
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

    dept_col, quota_col, info_col = st.columns([5, 1.6, 3.4])
    with dept_col:
        selected_dept = st.selectbox(
            "모집단위", departments, key="selected_dept", on_change=invalidate_result
        )

    record = None
    if not db.empty:
        matching = db[db["모집단위명"] == selected_dept]
        if len(matching) >= 1:
            record = matching.iloc[0]

    quota_text = display_quota(get_quota_value(record))

    with quota_col:
        st.markdown(
            f"""
            <div style="font-size: 13.5px; font-weight: 700; color: var(--text); margin-bottom: 4px; line-height: 1.45;">2027 모집인원</div>
            <div style="min-height: 42px; box-sizing: border-box; background-color: var(--tint); border: 1px solid var(--line); border-radius: 6px; padding: 8px 14px; color: var(--navy); font-weight: 800; font-size: 16.5px; display: flex; align-items: center; justify-content: center;">
                {escape(quota_text)}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with info_col:
        is_eng = selected_dept in ENG_DEPTS
        info_bg = "#EFF6FF" if is_eng else "#F8FAFC"
        info_border = "1px solid #BFDBFE" if is_eng else "1px solid var(--line)"
        info_color = "#1E40AF" if is_eng else "#475569"
        info_text = "이공계열 · 수학(미적/기하) 10% 및 과탐 7% 가산점 적용" if is_eng else "인문사회·일반계열 · 별도 선택과목 가산점 없음"
        st.markdown(
            f"""
            <div style="font-size: 13.5px; font-weight: 700; color: var(--text); margin-bottom: 4px; line-height: 1.45;">계열 및 가산점 안내</div>
            <div style="min-height: 42px; box-sizing: border-box; background-color: {info_bg}; border: {info_border}; border-radius: 6px; padding: 8px 14px; color: {info_color}; font-weight: 700; font-size: 13.5px; display: flex; align-items: center;">
                {info_text}
            </div>
            """,
            unsafe_allow_html=True,
        )

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
# 7. 결과 출력 (03, 04번: 565px 고정 대칭 유지)
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

result_col, comparison_col = st.columns([6, 4], gap="large")

with result_col:
    first_name, first_score = result["first"]
    second_name, second_score = result["second"]

    audit_cards_html = ""
    for s_item in result["all_subjects"]:
        role = s_item["role"]
        if role == "60% 반영":
            item_cls, badge_html = "active-60", '<span class="tag-60">60% 반영</span>'
        elif role == "40% 반영":
            item_cls, badge_html = "active-40", '<span class="tag-40">40% 반영</span>'
        elif role == "탐구상위":
            item_cls, badge_html = "dropped", '<span class="tag-drop">후보(미반영)</span>'
        else:
            item_cls, badge_html = "dropped", '<span class="tag-drop">미반영</span>'

        audit_cards_html += (
            f'<div class="audit-item {item_cls}">'
            f'<div class="audit-left">'
            f'<span class="audit-subj">{escape(s_item["title"])}</span>'
            f'<span class="audit-raw">{escape(s_item["raw"])}</span>'
            f'</div>'
            f'<div class="audit-right">'
            f'<span class="audit-conv">{s_item["conv"]:.2f}점</span>'
            f'{badge_html}'
            f'</div></div>'
        )

    st.markdown(
        f"""
        <div class="master-card">
            <div class="section-title"><span class="step">03</span>환산 점수</div>
            <div class="score-hero">
                <div class="score-label">{escape(selected_dept)}</div>
                <div class="score-number">{result["score"]:.2f} <small>점</small></div>
                <div class="score-footer">
                    100점 기준 환산값 &nbsp;·&nbsp; 1,000점 기준 <b>{result["score1000"]:,.2f}점</b>
                </div>
            </div>
            <div class="sub-metric-grid">
                <div class="sub-metric-box">
                    <div class="sub-metric-lbl">60% 반영 · {escape(first_name)}</div>
                    <div class="sub-metric-val-row">
                        <span class="sub-metric-val">{first_score * 0.6:.2f}</span>
                        <span class="sub-metric-calc">({first_score:.2f} × 60%)</span>
                    </div>
                </div>
                <div class="sub-metric-box">
                    <div class="sub-metric-lbl">40% 반영 · {escape(second_name)}</div>
                    <div class="sub-metric-val-row">
                        <span class="sub-metric-val">{second_score * 0.4:.2f}</span>
                        <span class="sub-metric-calc">({second_score:.2f} × 40%)</span>
                    </div>
                </div>
            </div>
            <div class="audit-wrap">
                <div class="audit-header">
                    <span>전 영역 환산 및 반영 판정 내역</span>
                    <span style="font-weight:600; font-size:11.5px;">가산점·등급 환산 적용 후 상위 2개 영역 자동 채택</span>
                </div>
                <div class="audit-grid">
                    {audit_cards_html}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with comparison_col:
    if record is not None and not data_scale and not db.empty:
        with st.container(border=True):
            section_title("04", "전년도 입시 결과 비교")
            st.warning("점수 단위를 판별하지 못해 비교를 표시하지 않습니다.")
    elif history.empty:
        with st.container(border=True):
            section_title("04", "전년도 입시 결과 비교")
            st.info("비교할 입시 결과 데이터가 없습니다.")
    else:
        recent = history[history["연도"] == "2026"].iloc[0]
        max_score = to_number(recent["최고"])
        avg_score = to_number(recent["평균"])
        cut_score = to_number(recent["최저"])

        valid_history = all(
            v is not None and 0 <= v <= 1000
            for v in (max_score, avg_score, cut_score)
        )
        ordered_history = valid_history and max_score >= avg_score >= cut_score

        if ordered_history:
            score = result["score"]

            if score >= max_score:
                msg, border_c, text_c = "[안정권] 전년도 최고점 이상 우수 성적", "#059669", "#065F46"
            elif score >= avg_score:
                msg, border_c, text_c = "[안정·적정권] 전년도 평균점 이상 성적", "#1D4ED8", "#1E40AF"
            elif score >= cut_score:
                msg, border_c, text_c = "[적정·경계권] 전년도 최저점 이상 · 평균점 미만", "#D97706", "#92400E"
            else:
                msg, border_c, text_c = "[상향지원] 전년도 최저점(커트라인) 미만", "#DC2626", "#991B1B"

            strip_html = '<div class="cmp-list">'
            for lbl, target in [("2026 최고점 기준", max_score), ("2026 평균점 기준", avg_score), ("2026 최저점 기준", cut_score)]:
                diff = score - target
                if abs(diff) < 0.005:
                    b_cls, b_txt = "pill-same", "동일 (0.00)"
                elif diff > 0:
                    b_cls, b_txt = "pill-plus", f"+{diff:,.2f}점 여유"
                else:
                    b_cls, b_txt = "pill-minus", f"-{abs(diff):,.2f}점 부족"

                strip_html += (
                    f'<div class="cmp-row">'
                    f'<span class="cmp-lbl">{lbl}</span>'
                    f'<div class="cmp-val-group">'
                    f'<span class="cmp-score">{target:,.2f}점</span>'
                    f'<span class="pill-badge {b_cls}">{b_txt}</span>'
                    f'</div></div>'
                )
            strip_html += "</div>"

            st.markdown(
                f"""
                <div class="master-card">
                    <div class="section-title"><span class="step">04</span>전년도 입시 결과 비교</div>
                    <div class="top3-grid">
                        <div><div class="top3-lbl">2026 최고점</div><div class="top3-val top3-max">{display_number(max_score)}</div></div>
                        <div><div class="top3-lbl">2026 평균점</div><div class="top3-val top3-avg">{display_number(avg_score)}</div></div>
                        <div><div class="top3-lbl">2026 최저점</div><div class="top3-val top3-min">{display_number(cut_score)}</div></div>
                    </div>
                    <div class="status" style="border-left-color:{border_c}; color:{text_c};">
                        {msg}<br>
                        <span style="font-size:13.5px; font-weight:700; color:var(--muted);">
                            전년도 평균({avg_score:.2f}점) 대비 {score - avg_score:+.2f}점
                        </span>
                    </div>
                    {strip_html}
                </div>
                """,
                unsafe_allow_html=True,
            )

        elif all(v is not None for v in (max_score, avg_score, cut_score)):
            with st.container(border=True):
                section_title("04", "전년도 입시 결과 비교")
                st.warning(
                    "2026년 최고·평균·최저 점수의 값 또는 순서가 올바르지 않아 "
                    "판정 문구를 표시하지 않습니다. 원본 입시 결과 자료를 확인해 주세요."
                )
        else:
            with st.container(border=True):
                section_title("04", "전년도 입시 결과 비교")
                st.info("2026년 최고·평균·최저 점수 중 일부가 없어 비교 판정을 표시하지 않습니다.")

# ==================================================
# 8. 결과 출력 (05, 06번 영역: 높이 440px 완벽 대칭 동기화)
# ==================================================
if not history.empty:
    chart_col, table_col = st.columns([6, 4], gap="large")

    with chart_col:
        with st.container(height=440, border=True):
            st.markdown(
                '<div class="section-title sec-05-marker"><span class="step">05</span>최근 3개년 점수 분포</div>',
                unsafe_allow_html=True,
            )

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
                        labelColor="#0F172A",
                        ticks=False,
                        domain=False,
                        grid=True,
                        gridColor="#E2E8F0",
                        gridWidth=1,
                    ),
                )

                base = alt.Chart(chart_data).encode(y=y_encoding)
                x_scale = alt.Scale(domain=[domain_min, domain_max], zero=False, nice=False)

                range_rule = base.mark_rule(
                    color="#CBD5E1", strokeWidth=5, strokeCap="round"
                ).encode(
                    x=alt.X(
                        "최저:Q",
                        title="환산점수 · 100점 기준",
                        scale=x_scale,
                        axis=alt.Axis(
                            titleFontSize=12,
                            titleFontWeight=600,
                            titleColor="#475569",
                            titlePadding=14,
                            labelFontSize=11,
                            labelColor="#475569",
                            tickCount=6,
                            grid=True,
                            gridColor="#E2E8F0",
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
                    filled=True, color="#047857", size=90, stroke="#FFFFFF", strokeWidth=1.5
                ).encode(
                    x=alt.X("최저:Q", scale=x_scale, axis=None),
                    tooltip=[
                        alt.Tooltip("연도:N", title="학년도"),
                        alt.Tooltip("최저:Q", format=".2f", title="최저점"),
                    ],
                )

                max_point = base.mark_point(
                    filled=True, color="#1E40AF", size=90, stroke="#FFFFFF", strokeWidth=1.5
                ).encode(
                    x=alt.X("최고:Q", scale=x_scale, axis=None),
                    tooltip=[
                        alt.Tooltip("연도:N", title="학년도"),
                        alt.Tooltip("최고:Q", format=".2f", title="최고점"),
                    ],
                )

                avg_point = base.mark_point(
                    filled=True, color="#0F172A", shape="diamond", size=145,
                    stroke="#FFFFFF", strokeWidth=1,
                ).encode(
                    x=alt.X("평균:Q", scale=x_scale, axis=None),
                    tooltip=[
                        alt.Tooltip("연도:N", title="학년도"),
                        alt.Tooltip("평균:Q", format=".2f", title="평균점"),
                    ],
                )

                max_txt = base.mark_text(
                    align="left", dx=8, dy=-10, fontSize=11, color="#1E40AF", fontWeight=700
                ).encode(
                    x=alt.X("최고:Q", scale=x_scale, axis=None),
                    text=alt.Text("최고:Q", format=".2f"),
                )

                min_txt = base.mark_text(
                    align="right", dx=-8, dy=10, fontSize=11, color="#047857", fontWeight=700
                ).encode(
                    x=alt.X("최저:Q", scale=x_scale, axis=None),
                    text=alt.Text("최저:Q", format=".2f"),
                )

                my_score_df = pd.DataFrame({"내 점수": [float(result["score"])]})
                my_line = alt.Chart(my_score_df).mark_rule(
                    color="#DC2626", strokeWidth=2, strokeDash=[5, 4], opacity=0.95
                ).encode(
                    x=alt.X("내 점수:Q", scale=x_scale, axis=None),
                    tooltip=[alt.Tooltip("내 점수:Q", title="내 환산점수", format=".2f")],
                )

                chart = (
                    alt.layer(range_rule, min_point, max_point, avg_point, min_txt, max_txt, my_line)
                    .properties(
                        height=325,
                        padding={"left": 8, "right": 24, "top": 10, "bottom": 2},
                    )
                    .configure_view(stroke=None, fill="#FFFFFF")
                    .configure_axis(
                        labelFont="Malgun Gothic, sans-serif",
                        titleFont="Malgun Gothic, sans-serif",
                    )
                )

                st.altair_chart(chart, use_container_width=True)

                st.markdown(
                    "<div style='width:100%;text-align:center;margin-top:0px;font-size:12.5px;line-height:1.4;'>"
                    "<span style='color:#1E40AF;font-weight:700;'>● 최고점</span> "
                    "<span style='color:#047857;font-weight:700;'>● 최저점</span> "
                    "<span style='color:#0F172A;font-weight:700;'>◆ 평균점</span> "
                    "<span style='color:#DC2626;font-weight:700;'>┆ 내 점수</span>"
                    "</div>",
                    unsafe_allow_html=True,
                )

    with table_col:
        sorted_hist = history.sort_values("연도", ascending=False)
        cards_html = '<div class="yr-card-list">'
        for _, h_row in sorted_hist.iterrows():
            yr_label = f"{escape(str(h_row['연도']))}학년도"
            mx_s = display_number(h_row["최고"])
            av_s = display_number(h_row["평균"])
            mn_s = display_number(h_row["최저"])
            comp_s = escape(display_ratio(h_row["경쟁률"]))
            add_s = escape(display_count(h_row["추가합격"]))
            if add_s != "—" and not add_s.endswith("명"):
                add_s += "명"

            cards_html += (
                f'<div class="yr-card">'
                f'<div class="yr-head">'
                f'<span class="yr-title">{yr_label}</span>'
                f'<div class="yr-tags">'
                f'<span class="yr-tag">경쟁률 <b>{comp_s}</b></span>'
                f'<span class="yr-tag">추합 <b>{add_s}</b></span>'
                f'</div></div>'
                f'<div class="yr-metrics">'
                f'<div><div class="yr-m-lbl">최고점</div><div class="yr-m-val" style="color:#1E40AF;">{mx_s}</div></div>'
                f'<div><div class="yr-m-lbl">평균점</div><div class="yr-m-val">{av_s}</div></div>'
                f'<div><div class="yr-m-lbl">최저점</div><div class="yr-m-val" style="color:#047857;">{mn_s}</div></div>'
                f'</div></div>'
            )
        cards_html += "</div>"

        st.markdown(
            f"""
            <div class="master-card-056">
                <div class="section-title"><span class="step">06</span>3개년 입시 결과</div>
                {cards_html}
            </div>
            """,
            unsafe_allow_html=True,
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
            "모집인원": display_quota(get_quota_value(dept_record)),
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
        st.markdown("#### 현재 점수 기준 지원 가능권역 보드")
        st.caption(
            "분류 기준: 내 환산점수 ≥ 2026 평균 이상 → 안정 지원권 / "
            "2026 최저 이상~평균 미만 → 적정·경계권 / 2026 최저 미만 → 상향 도전권 (평균 대비 높은 순 정렬)"
        )

        valid_items = [item for item in analysis_by_dept.values() if item["분류"] != "자료 확인 필요"]
        if valid_items:
            kb_cols = st.columns(3, gap="medium")
            categories = [
                ("안정", "안정 지원권", "kb-safe", "#047857"),
                ("적정·경계", "적정 · 경계권", "kb-fit", "#B45309"),
                ("상향", "상향 도전권", "kb-up", "#B91C1C"),
            ]

            for col, (cat_key, cat_title, head_cls, accent_color) in zip(kb_cols, categories):
                cat_items = sorted(
                    [it for it in valid_items if it["분류"] == cat_key],
                    key=lambda x: (x["평균 대비"] if x["평균 대비"] is not None else -999),
                    reverse=True,
                )
                with col:
                    st.markdown(
                        f'<div class="kb-header {head_cls}">'
                        f'<span>{cat_title}</span>'
                        f'<span class="kb-cnt">{len(cat_items)}개 학과</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    with st.container(height=450, border=True):
                        if not cat_items:
                            st.markdown(
                                '<div style="text-align:center; padding:40px 10px; color:var(--muted); font-size:14px;">'
                                '해당 권역에 속하는 모집단위가 없습니다.</div>',
                                unsafe_allow_html=True,
                            )
                        else:
                            cards_str = ""
                            for it in cat_items:
                                g_avg = it["평균 대비"]
                                g_min = it["최저 대비"]
                                avg_badge = f"평균 대비 {g_avg:+.2f}점" if g_avg is not None else "—"
                                min_badge = f"최저 대비 {g_min:+.2f}점" if g_min is not None else "—"

                                cards_str += (
                                    f'<div class="kb-card">'
                                    f'<div class="kb-card-top">'
                                    f'<span class="kb-dept">{escape(it["모집단위"])}</span>'
                                    f'<span class="kb-quota">모집 {escape(it["모집인원"])}</span>'
                                    f'</div>'
                                    f'<div class="kb-scores">'
                                    f'<span>내 점수 <b>{it["현재 환산점수"]:.2f}</b></span>'
                                    f'<span>26평균 <b>{display_number(it["2026 평균"])}</b></span>'
                                    f'<span>26최저 <b>{display_number(it["2026 최저"])}</b></span>'
                                    f'</div>'
                                    f'<div class="kb-foot">'
                                    f'<span style="color:{accent_color};">{avg_badge}</span>'
                                    f'<span style="color:var(--muted);">{min_badge}</span>'
                                    f'</div></div>'
                                )
                            st.markdown(cards_str, unsafe_allow_html=True)
        else:
            st.info("추천 분류에 필요한 2026학년도 입시 결과가 충분하지 않습니다.")

    with comparison_tab:
        st.markdown("#### 모집단위별 점수·입결 다이렉트 비교")

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
            spec_cols = st.columns(len(compare_depts), gap="medium")
            for s_col, dept_name in zip(spec_cols, compare_depts):
                item = analysis_by_dept[dept_name]
                with s_col:
                    card_html = (
                        f'<div class="spec-card">'
                        f'<div class="spec-top">'
                        f'<div class="spec-dept">{escape(dept_name)}</div>'
                        f'<div class="spec-quota">2027 모집인원 · {escape(item["모집인원"])}</div>'
                        f'<div class="spec-my-lbl">현재 내 환산점수</div>'
                        f'<div class="spec-my-val">{item["현재 환산점수"]:.2f}<span style="font-size:14px; font-weight:600; color:var(--muted);"> 점</span></div>'
                        f'</div>'
                        f'<div class="spec-body">'
                    )

                    for yr in ("2026", "2025", "2024"):
                        yr_info = item["연도별"].get(yr, {})
                        st_txt = yr_info.get("판정", "자료 없음")
                        if st_txt == "안정":
                            b_cls = "bdg-safe"
                        elif st_txt == "적정·경계":
                            b_cls = "bdg-fit"
                        elif st_txt == "상향":
                            b_cls = "bdg-up"
                        else:
                            b_cls = "bdg-none"

                        mx_v = display_number(yr_info.get("최고"))
                        av_v = display_number(yr_info.get("평균"))
                        mn_v = display_number(yr_info.get("최저"))

                        card_html += (
                            f'<div class="spec-yr-box">'
                            f'<div class="spec-yr-head">'
                            f'<span class="spec-yr-name">{yr}학년도</span>'
                            f'<span class="{b_cls}">{escape(st_txt)}</span>'
                            f'</div>'
                            f'<div class="yr-metrics">'
                            f'<div><div class="yr-m-lbl">최고</div><div class="yr-m-val" style="color:#1E40AF; font-size:15.5px;">{mx_v}</div></div>'
                            f'<div><div class="yr-m-lbl">평균</div><div class="yr-m-val" style="font-size:15.5px;">{av_v}</div></div>'
                            f'<div><div class="yr-m-lbl">최저</div><div class="yr-m-val" style="color:#047857; font-size:15.5px;">{mn_v}</div></div>'
                            f'</div></div>'
                        )

                    card_html += "</div></div>"
                    st.markdown(card_html, unsafe_allow_html=True)
        else:
            st.info("비교할 모집단위를 하나 이상 선택해 주세요.")
