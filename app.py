import streamlit as st
import pandas as pd
import requests
import urllib.parse
import os
import uuid
from datetime import datetime
from legal_db import LEGAL_DB


# ---------------------------------------------------
# Streamlit Page Setup
# ---------------------------------------------------
st.set_page_config(page_title="Rural ACT", layout="wide")

st.title("🌾 Rural ACT – தமிழ் சட்ட விழிப்புணர்வு")
st.write("English → Tamil Translation • Tamil Voice • Legal Awareness • Smart Feedback")


# ---------------------------------------------------
# 100% STABLE TAMIL TRANSLATION (MYMEMORY API)
# ---------------------------------------------------
def translate_to_tamil(text):

    text_encoded = urllib.parse.quote(text)

    url = f"https://api.mymemory.translated.net/get?q={text_encoded}&langpair=en|ta"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if "responseData" in data and "translatedText" in data["responseData"]:
            return data["responseData"]["translatedText"]

        return "⚠️ Unable to translate right now."

    except Exception:
        return "⚠️ Translation service temporarily unavailable."


# ---------------------------------------------------
# LONG TEXT TAMIL TTS (CHUNK PROCESSING FIX)
# ---------------------------------------------------
def generate_audio(text):

    chunk_size = 180
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    audio_files = []

    for chunk in chunks:
        try:
            text_encoded = urllib.parse.quote(chunk)
            url = (
                f"https://translate.google.com/translate_tts?"
                f"ie=UTF-8&q={text_encoded}&tl=ta&client=tw-ob"
            )

            filename = f"voice_{uuid.uuid4()}.mp3"
            response = requests.get(url)

            if response.status_code == 200:
                with open(filename, "wb") as f:
                    f.write(response.content)
                audio_files.append(filename)

        except:
            continue

    return audio_files


# ---------------------------------------------------
# SAVE FEEDBACK TO CSV
# ---------------------------------------------------
def append_feedback(data):
    df = pd.DataFrame([data])
    file = "user_feedback.csv"

    if os.path.exists(file):
        df.to_csv(file, mode="a", header=False, index=False)
    else:
        df.to_csv(file, index=False)


# ---------------------------------------------------
# DETECT LEGAL SECTION
# ---------------------------------------------------
def detect_legal_section(text):
    text_low = text.lower()
    for keyword, info in LEGAL_DB.items():
        if keyword in text_low:
            return info
    return None


# ---------------------------------------------------
# SESSION STATE SETUP
# ---------------------------------------------------
if "show_detail_buttons" not in st.session_state:
    st.session_state.show_detail_buttons = False
if "last_input" not in st.session_state:
    st.session_state.last_input = None


# ---------------------------------------------------
# INPUT TEXT AREA
# ---------------------------------------------------
user_input = st.text_area("Enter English text:", height=150)


# ---------------------------------------------------
# MAIN PROCESS
# ---------------------------------------------------
if st.button("Translate & Analyze"):
    if not user_input.strip():
        st.warning("⚠️ Please enter text.")
        st.stop()

    st.session_state.last_input = user_input

    # Translate to Tamil using MyMemory
    tamil_text = translate_to_tamil(user_input)
    st.session_state["last_tamil"] = tamil_text

    st.subheader("📌 தமிழ் மொழிபெயர்ப்பு:")
    st.success(tamil_text)

    st.write("### 🔊 தமிழ் குரல்")

    audio_parts = generate_audio(tamil_text)
    if audio_parts:
        for part in audio_parts:
            st.audio(part)

    # Legal Awareness
    st.subheader("⚖️ சட்ட விழிப்புணர்வு (தமிழில்):")

    legal = detect_legal_section(user_input)

    if legal:
        st.session_state["last_sections"] = [legal["section"]]

        st.markdown(f"""
### ⚖️ **{legal['section']}**
**{legal['tamil']}**

**தண்டனை:** {legal['punishment']}  
**உதவி எண்:** {legal['helpline']}  
**📚 உதாரணம்:** {legal['example']}
""")

        st.write("### 🔊 சட்ட விளக்கம் (குரல்)")
        legal_audio_parts = generate_audio(legal["tamil"])
        if legal_audio_parts:
            for part in legal_audio_parts:
                st.audio(part)

    else:
        st.session_state["last_sections"] = []
        st.info("⚠️ சட்ட மீறல் தொடர்பான தகவல் எதுவும் இல்லை.")


# ---------------------------------------------------
# FEEDBACK SECTION
# ---------------------------------------------------
st.divider()
st.subheader("🗣️ பயனர் கருத்து (User Feedback)")

if st.session_state.last_input:

    c1, c2 = st.columns(2)

    with c1:
        if st.button("✅ Understand"):
            append_feedback({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "input_english": st.session_state["last_input"],
                "tamil_translation": st.session_state["last_tamil"],
                "detected_sections": ",".join(st.session_state["last_sections"]),
                "feedback": "Understand",
                "feedback_detail": ""
            })
            st.success("✔ Feedback saved successfully.")

    with c2:
        if st.button("❌ Not Understand"):
            st.session_state.show_detail_buttons = True

    if st.session_state.show_detail_buttons:
        st.markdown("### 😕 எது புரியவில்லை?")

        d1, d2, d3 = st.columns(3)

        if d1.button("📝 Text"):
            append_feedback({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "input_english": st.session_state["last_input"],
                "tamil_translation": st.session_state["last_tamil"],
                "detected_sections": ",".join(st.session_state["last_sections"]),
                "feedback": "Not Understand",
                "feedback_detail": "Text"
            })
            st.success("✔ Saved.")
            st.session_state.show_detail_buttons = False

        if d2.button("🔊 Voice"):
            append_feedback({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "input_english": st.session_state["last_input"],
                "tamil_translation": st.session_state["last_tamil"],
                "detected_sections": ",".join(st.session_state["last_sections"]),
                "feedback": "Not Understand",
                "feedback_detail": "Voice"
            })
            st.success("✔ Saved.")
            st.session_state.show_detail_buttons = False

        if d3.button("🔁 Both"):
            append_feedback({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "input_english": st.session_state["last_input"],
                "tamil_translation": st.session_state["last_tamil"],
                "detected_sections": ",".join(st.session_state["last_sections"]),
                "feedback": "Not Understand",
                "feedback_detail": "Both"
            })
            st.success("✔ Saved.")
            st.session_state.show_detail_buttons = False

else:
    st.info("👇 முதலில் மொழிபெயர்ப்பு செய்து கருத்து அளிக்கவும்.")


# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------
st.markdown("---")
st.caption("Developed for rural Tamil users — Translation • Voice • Legal Awareness • Smart Feedback")




