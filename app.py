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
st.set_page_config(page_title="Rural ACT", layout="wide")

st.title("🌾 Rural ACT – தமிழ் சட்ட விழிப்புணர்வு")
st.write("English → Tamil Translation • Tamil Voice • Legal Awareness • Smart Feedback")


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
def append_feedback(data):
    df = pd.DataFrame([data])

    file = "user_feedback.csv"

    if os.path.exists(file):
        df.to_csv(file, mode="a", header=False, index=False)
    else:
        df.to_csv(file, index=False)


# ---------------------------------------------------
# Detect Legal Section
# ---------------------------------------------------
def detect_legal_section(text):
    text_low = text.lower()
    for keyword, info in LEGAL_DB.items():
        if keyword in text_low:
            return info
    return None


# Initialize session variables
if "show_detail_buttons" not in st.session_state:
    st.session_state.show_detail_buttons = False
if "last_input" not in st.session_state:
    st.session_state.last_input = None


# ---------------------------------------------------
# UI Input Box
# ---------------------------------------------------
user_input = st.text_area("Enter English text:", height=150)


# ---------------------------------------------------
# MAIN PROCESS
# ---------------------------------------------------
if st.button("Translate & Analyze"):
    if not user_input.strip():
        st.warning("⚠️ Please enter text.")
        st.stop()

    # Save input
    st.session_state.last_input = user_input

    # Tamil Translation
    tamil_text = GoogleTranslator(source="auto", target="ta").translate(user_input)
    st.session_state["last_tamil"] = tamil_text

    st.subheader("📌 தமிழ் மொழிபெயர்ப்பு:")
    st.success(tamil_text)

    # Tamil Voice Output
    st.write("### 🔊 தமிழ் குரல்")
    audio_file = generate_audio(tamil_text)
    if audio_file:
        st.audio(audio_file)

    # Legal Detection
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

        # Tamil voice for legal explanation
        legal_audio = generate_audio(legal["tamil"])
        st.write("### 🔊 சட்ட விளக்கம் (குரல்)")
        if legal_audio:
            st.audio(legal_audio)

    else:
        st.session_state["last_sections"] = []
        st.info("⚠️ சட்ட மீறல் தொடர்பான தகவல் எதுவும் இல்லை.")


# ---------------------------------------------------
# FEEDBACK SECTION (Restored Working Version)
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
            st.success("✅ Feedback saved successfully.")

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


st.markdown("---")
st.caption("Developed for rural Tamil users — Translation • Voice • Legal Awareness • Smart Feedback")


