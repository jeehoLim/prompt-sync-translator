import streamlit as st
import deepl
import os
from dotenv import load_dotenv

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
