import streamlit as st
import json, os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from BabyCryLast import analyze  # your working function

# ================================
# Load Translations
# ================================
TRANSLATIONS_PATH = os.path.join(os.path.dirname(__file__), "translations.json")

with open(TRANSLATIONS_PATH, "r", encoding="utf-8") as f:
    translations = json.load(f)

LANG = st.session_state.get("LANG", "en")

# ================================
# Sidebar – Language Selector
# ================================
st.set_page_config(
    page_title="BabyCry Analyzer",
    page_icon="👶",
    layout="centered",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3069/3069289.png", width=80)
    st.markdown("### 🌐 Choose Language")
    lang_choice = st.radio("", ["en", "tj", "ru"], index=["en","tj","ru"].index(LANG))
    st.session_state["LANG"] = lang_choice
    t = translations[lang_choice]
    st.markdown("---")
    st.caption("Made with ❤️ using Streamlit")

# ================================
# Main UI Layout
# ================================
st.markdown(
    f"<h1 style='text-align:center;color:#ff4081;'>{t['title']}</h1>",
    unsafe_allow_html=True
)
st.markdown(f"<p style='text-align:center;font-size:18px;'>{t['description']}</p>", unsafe_allow_html=True)

# Upload / Record Section
st.markdown("### 🎤 " + t["upload_label"])
audio_file = st.file_uploader("", type=["wav", "mp3", "m4a"])

# Action Button
if st.button("🔍 Analyze"):
    if audio_file is None:
        st.warning("Please upload or record an audio first.")
    else:
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_file.read())
        result_text = analyze("temp_audio.wav")
        st.markdown("---")
        if "🔴" in result_text:
            st.error(result_text)
        elif "🟩" in result_text:
            st.success(result_text)
        elif "🟦" in result_text:
            st.info(result_text)
        else:
            st.warning(result_text)

st.markdown("<br><hr><p style='text-align:center;font-size:13px;'>© 2025 BabyCry Project | Muslim Saidov</p>", unsafe_allow_html=True)
