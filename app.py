import streamlit as st
import deepl
import os
import re
import difflib
from dotenv import load_dotenv

st.set_page_config(page_title="JEEHOLAB Prompt Sync", page_icon="🧠", layout="wide")

st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
        <span style="font-size: 28px; font-weight: 700; color: #2c3e50;">🧠 JEEHOLAB</span>
    </div>
""", unsafe_allow_html=True)

st.title("🔄 Prompt Sync Translator")

# CSS
st.markdown("""
<style>
.stTextArea textarea {
    width: 100% !important;
    min-height: 400px;
    font-size: 16px;
}
.highlight-added {
    background-color: #d0f0fd;
    color: black;
    font-weight: bold;
    padding: 1px 3px;
    border-radius: 3px;
}
</style>
""", unsafe_allow_html=True)

# Deepl API
load_dotenv()
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
translator = deepl.Translator(DEEPL_API_KEY)

# 초기 상태 설정
for key in ["en_text", "ko_text", "prev_en", "prev_ko"]:
    if key not in st.session_state:
        st.session_state[key] = ""

# 초기 번역 상태 설정 (문장 수 맞추기)
if not st.session_state.prev_en and st.session_state.en_text:
    st.session_state.prev_en = st.session_state.en_text
    st.session_state.ko_text = translator.translate_text(
        st.session_state.en_text, source_lang="EN", target_lang="KO"
    ).text
    st.session_state.prev_ko = st.session_state.ko_text

# 모드 선택
mode = st.radio(
    "Choose translation mode:",
    ["🔄 Fast Full Translation (default)", "🧚 Experimental Partial Update"]
)

# 문장 분리
def split_into_sentences(text):
    sentence_endings = re.compile(r'(?<=[.!?])\s+')
    return sentence_endings.split(text.strip())

# 강조
def highlight_diff_words_html(old, new):
    d = difflib.ndiff(old.split(), new.split())
    result = []
    for token in d:
        if token.startswith("+ "):
            result.append(f"<span class='highlight-added'>{token[2:]}</span>")
        elif token.startswith("- "):
            result.append(f"<del style='opacity: 0.5;'>{token[2:]}</del>")
        elif token.startswith("  "):
            result.append(token[2:])
    return " ".join(result)

# EN -> KO 부분 번역
def translate_diff_en_to_ko():
    old_paragraphs = st.session_state.prev_en.split("\n\n")
    new_paragraphs = st.session_state.en_text.split("\n\n")
    translated_paragraphs = st.session_state.ko_text.split("\n\n")

    result = translated_paragraphs[:]
    for i, (old, new) in enumerate(zip(old_paragraphs, new_paragraphs)):
        old_sents = split_into_sentences(old)
        new_sents = split_into_sentences(new)
        sm = difflib.SequenceMatcher(None, old_sents, new_sents)
        translated_sents = split_into_sentences(result[i]) if i < len(result) else []
        updated = translated_sents[:]
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag in ["replace", "insert"]:
                for j in range(j1, j2):
                    new_sentence = new_sents[j]
                    if j < len(old_sents) and new_sentence == old_sents[j]:
                        continue
                    translated = translator.translate_text(
                        new_sentence, source_lang="EN", target_lang="KO"
                    ).text
                    if j < len(updated):
                        updated[j] = translated
                    else:
                        updated.append(translated)
        result[i] = ". ".join(updated)
    st.session_state.ko_text = "\n\n".join(result)
    st.session_state.prev_en = st.session_state.en_text

# KO -> EN 부분 번역
def translate_diff_ko_to_en():
    old_paragraphs = st.session_state.prev_ko.split("\n\n")
    new_paragraphs = st.session_state.ko_text.split("\n\n")
    translated_paragraphs = st.session_state.en_text.split("\n\n")

    result = translated_paragraphs[:]
    for i, (old, new) in enumerate(zip(old_paragraphs, new_paragraphs)):
        old_sents = split_into_sentences(old)
        new_sents = split_into_sentences(new)
        sm = difflib.SequenceMatcher(None, old_sents, new_sents)
        translated_sents = split_into_sentences(result[i]) if i < len(result) else []
        updated = translated_sents[:]
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag in ["replace", "insert"]:
                for j in range(j1, j2):
                    new_sentence = new_sents[j]
                    if j < len(old_sents) and new_sentence == old_sents[j]:
                        continue
                    translated = translator.translate_text(
                        new_sentence, source_lang="KO", target_lang="EN"
                    ).text
                    if j < len(updated):
                        updated[j] = translated
                    else:
                        updated.append(translated)
        result[i] = ". ".join(updated)
    st.session_state.en_text = "\n\n".join(result)
    st.session_state.prev_ko = st.session_state.ko_text

# 전체 번역

def translate_full_en_to_ko():
    st.session_state.ko_text = translator.translate_text(
        st.session_state.en_text, source_lang="EN", target_lang="KO"
    ).text
    st.session_state.prev_en = st.session_state.en_text

def translate_full_ko_to_en():
    st.session_state.en_text = translator.translate_text(
        st.session_state.ko_text, source_lang="KO", target_lang="EN"
    ).text
    st.session_state.prev_ko = st.session_state.ko_text

# 입력 영역
col1, col2 = st.columns(2)
with col1:
    st.text_area(
        "🇺🇸 English Prompt",
        key="en_text",
        height=400,
        on_change=translate_diff_en_to_ko if mode == "🧚 Experimental Partial Update" else translate_full_en_to_ko,
    )
with col2:
    st.text_area(
        "🇰🇷 Korean Prompt",
        key="ko_text",
        height=400,
        on_change=translate_diff_ko_to_en if mode == "🧚 Experimental Partial Update" else translate_full_ko_to_en,
    )

# Diff 출력
if mode == "🧚 Experimental Partial Update":
    st.markdown("### 🔍 Diff Preview (Experimental)")
    en_diff = highlight_diff_words_html(st.session_state.prev_en, st.session_state.en_text)
    ko_diff = highlight_diff_words_html(st.session_state.prev_ko, st.session_state.ko_text)
    st.markdown("#### 📍 English Changes")
    st.markdown(f"<div>{en_diff}</div>", unsafe_allow_html=True)
    st.markdown("#### 📍 Korean Changes")
    st.markdown(f"<div>{ko_diff}</div>", unsafe_allow_html=True)

# Debug 영역
with st.expander("🔧 Debug Info"):
    st.subheader("English Prompt")
    st.text_area("Previous", value=st.session_state.prev_en, height=100, disabled=True)
    st.text_area("Current", value=st.session_state.en_text, height=100, disabled=True)
    st.subheader("Korean Prompt")
    st.text_area("Previous", value=st.session_state.prev_ko, height=100, disabled=True)
    st.text_area("Current", value=st.session_state.ko_text, height=100, disabled=True)
