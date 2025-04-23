import streamlit as st
import deepl
import os
from dotenv import load_dotenv

# (선택) 페이지 기본 설정
st.set_page_config(
    page_title="JEEHOLAB Prompt Sync",
    page_icon="🧠",
    layout="wide"
)

# 💡 CSS는 set_page_config 다음에!
st.markdown(
    """
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
    <span style="font-size: 28px; font-weight: 700; color: #2c3e50;">🧠 JEEHOLAB</span>
    </div>
    <style>
    .stTextArea textarea {
        width: 100% !important;
        min-height: 400px;
        font-size: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

load_dotenv()
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")

translator = deepl.Translator(DEEPL_API_KEY)

# 세션 상태 초기화
if "en_text" not in st.session_state:
    st.session_state["en_text"] = ""
if "ko_text" not in st.session_state:
    st.session_state["ko_text"] = ""

# 영어 → 한국어 번역 함수
def translate_en_to_ko():
    st.session_state.ko_text = translator.translate_text(
        st.session_state.en_text, source_lang="EN", target_lang="KO"
    ).text

# 한국어 → 영어 번역 함수
def translate_ko_to_en():
    st.session_state.en_text = translator.translate_text(
        st.session_state.ko_text, source_lang="KO", target_lang="EN"
    ).text

st.title("🔄 Prompt Sync Translator")

col1, col2 = st.columns(2)

with col1:
    st.text_area(
        "🇺🇸 English Prompt",
        key="en_text",
        height=400,
        on_change=translate_en_to_ko,
    )

with col2:
    st.text_area(
        "🇰🇷 한국어 프롬프트",
        key="ko_text",
        height=400,
        on_change=translate_ko_to_en,
    )
