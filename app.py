import streamlit as st
import google.generativeai as genai
from datetime import datetime
import json
import csv
import os

# Set page config
st.set_page_config(page_title="AI Language Translator", page_icon="🌍")

# Load Gemini API key from secrets.toml
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Function to get one English word/phrase
def get_english_word():
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    prompt = "Give me one simple, common English word or short phrase that can be easily translated into a local language. Do not repeat previous suggestions."
    response = model.generate_content(prompt)
    return response.text.strip()

# Initialize or fetch current phrase
if "phrase" not in st.session_state:
    st.session_state.phrase = get_english_word()

# App UI
st.title("🌍 AI-powered Local Language Translator")
st.markdown("Translate the word or phrase below into your local language:")

st.subheader(f"🗣️ **{st.session_state.phrase}**")

# Translation input
user_translation = st.text_input("Your translation (in your language):")
user_language = st.selectbox("Which language are you using?", ["Yoruba", "Igbo", "Hausa","Ibibio", "Other"])

# Handle submission
if st.button("Submit Translation"):
    if user_translation.strip() == "":
        st.warning("Please enter a translation.")
    else:
        data = {
            "english": st.session_state.phrase,
            "translation": user_translation.strip(),
            "language": user_language,
            "timestamp": datetime.now().isoformat()
        }

        # Save to local file
        with open("translations.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")
        # Optionally save to CSV
        csv_file = "translations.csv"
        file_exists = os.path.isfile(csv_file)
        with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["english", "translation", "language", "timestamp"])
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)

        st.success("✅ Translation saved successfully!")
        st.session_state.phrase = get_english_word()  # Load next phrase
        st.rerun()  # Refresh page to update word
