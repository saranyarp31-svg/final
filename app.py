import streamlit as st
from deep_translator import GoogleTranslator
import pandas as pd
import requests
import urllib.parse
import os
from datetime import datetime
from legal_db import LEGAL_DB

# ---------------------------------------------------
# Streamlit Page Setup
# ---------------------------------------------------
st.set_page_config(page_title="Rural ACT - Tamil Legal Translator", layout="wide")

st.title("🌾 Rural ACT – Tamil Legal Awareness Translator")
st.write("English → Tamil Translation • Legal Detection • Tamil Voice Output")


# ---------------------------------------------------
# SIMPLE GOOGLE TTS (100% works on Streamlit Cloud)
# ---------------------------------------------------
def generate_audio(text):
    try:
        text_encoded = urllib.parse.quote(text)
        url = (
            f"https://translate.google.com/translate_tts?"
            f"ie=UTF-8&q={text_encoded}&tl=ta&client=tw-ob"
        )

        audio_file = "tamil_voice.mp3"
        response = requests.get(url)

        if response.status_code == 200:
            with open(audio_file, "wb") as f:
                f.write(response.content)
            return audio_file
        else:
            return None

    except Exception:
        return None


# ---------------------------------------------------
# Save Feedback to CSV
# ---------------------------------------------------
def save_feedback(original, tamil, section, fb_type, fb_detail=""):
    data = {
        "timestamp": [datetime.now().isoformat()],
        "english_input": [original],
        "tamil_output": [tamil],
        "legal_section": [section],
        "feedback_type": [fb_type],
        "feedback_detail": [fb_detail]
    }

    df = pd.DataFrame(data)

    fname = "user_feedback.csv"
    if os.path.exists(fname):
        df.to_csv(fname, mode="a", header=False, index=False)
    else:
        df.to_csv(fname, index=False)


# ---------------------------------------------------
# Legal Keyword Detection
# ---------------------------------------------------
def detect_legal_section(text):
    text_low = text.lower()
    for keyword, info in LEGAL_DB.items():
        if keyword in text_low:
            return info
    return None


# ---------------------------------------------------
# UI Input Box
# ---------------------------------------------------
user_input = st.text_area("Enter English text to translate:", height=160)


# ---------------------------------------------------
# Main Process
# ---------------------------------------------------
if st.button("Translate & Analyze"):
    if not user_input.strip():
        st.warning("Please enter some text.")
        st.stop()

    # Translate to Tamil
    try:
        tamil_text = GoogleTranslator(source="auto", target="ta").translate(user_input)
        st.subheader("📌 Tamil Translation")
        st.success(tamil_text)
    except Exception as e:
        st.error("Translation error: " + str(e))
        tamil_text = ""

    # Tamil Voice Output for Translation
    st.subheader("🔊 Tamil Voice Output")
    audio_file = generate_audio(tamil_text)

    if audio_file:
        st.audio(audio_file)
    else:
        st.warning("Voice not available right now.")

    # Legal Section Detection
    st.subheader("⚖️ Legal Awareness")
    legal = detect_legal_section(user_input)

    if legal:
        st.write(f"**Section:** {legal['section']}")
        st.write(f"**Tamil Explanation:** {legal['tamil']}")
        st.write(f"**Punishment:** {legal['punishment']}")
        st.write(f"**Helpline:** {legal['helpline']}")
        st.info(f"Example: {legal['example']}")
        section_name = legal['section']

        # Tamil audio for legal explanation
        st.write("### 🔊 Legal Explanation (Tamil Voice)")
        legal_voice_text = legal["tamil"]
        legal_audio = generate_audio(legal_voice_text)

        if legal_audio:
            st.audio(legal_audio)
        else:
            st.warning("Legal audio unavailable.")

    else:
        st.info("No legal issues detected.")
        section_name = "None"


    # ---------------------------------------------------
    # Feedback Section
    # ---------------------------------------------------
    st.subheader("📝 Feedback")

    col1, col2 = st.columns(2)

    if col1.button("✅ I Understand"):
        save_feedback(user_input, tamil_text, section_name, "Understand")
        st.success("Feedback saved successfully!")

    if col2.button("❌ I Don't Understand"):
        st.write("### Choose what you need help with:")

        need = st.radio(
            "",
            ["📝 More Text Explanation", "🔊 Better Voice", "📝🔊 Both"],
        )

        save_feedback(user_input, tamil_text, section_name, "Not Understand", need)
        st.error("Feedback saved. We will improve the explanation!")


# Developer Mode - View Feedback Log
if st.checkbox("Show Feedback Log (Developer Only)"):
    if os.path.exists("user_feedback.csv"):
        st.dataframe(pd.read_csv("user_feedback.csv").tail(20))
    else:
        st.info("No feedback available yet.")

