import streamlit as st
from datetime import datetime
from utils import get_answer_from_doc
from gtts import gTTS
import io
import re

# ---------------- Page Config ----------------
st.set_page_config(page_title="📄 DocuChat Gemini Chatbot", layout="wide")
st.title("📄 DocuChat - Gemini Chatbot")

# ---------------- Session State ----------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# ---------------- File Upload ----------------
uploaded_file = st.file_uploader(
    "Upload your PDF, DOCX, or TXT file",
    type=["pdf", "docx", "txt"]
)

# ---------------- Helper Functions ----------------
def add_message(sender, text):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.chat_history.append({
        "sender": sender,
        "text": text,
        "time": timestamp
    })


def speak_text(text):
    clean_text = re.sub(r'[*_`]', '', text)
    tts = gTTS(text=clean_text, lang='en')
    audio_bytes = io.BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    st.audio(audio_bytes.read(), format="audio/mp3")


def send_message():
    user_text = st.session_state.user_input

    if uploaded_file is None:
        st.warning("⚠️ Please upload a document first!")
        return

    if not user_text.strip():
        st.warning("⚠️ Please enter a question!")
        return

    # Add user message
    add_message("user", user_text)
    st.session_state.user_input = ""

    with st.spinner("🤖 Generating answer..."):
        try:
            answer = get_answer_from_doc(uploaded_file, user_text)
            add_message("bot", answer)
        except Exception as e:
            add_message("bot", f"❌ Error: {str(e)}")

# ---------------- Chat Display ----------------
chat_container = st.container()

for i, msg in enumerate(st.session_state.chat_history):
    if msg["sender"] == "user":
        chat_container.markdown(
            f"""
            <div style="text-align:right; margin:6px 0; display:flex; justify-content:flex-end;">
                <div style="background:#DCF8C6; padding:10px 14px;
                            border-radius:15px; max-width:70%;">
                    {msg['text']}<br>
                    <span style="font-size:10px; color:#555;">{msg['time']}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        chat_container.markdown(
            f"""
            <div style="text-align:left; margin:6px 0; display:flex; justify-content:flex-start;">
                <div style="background:#F1F0F0; padding:10px 14px;
                            border-radius:15px; max-width:70%;">
                    {msg['text']}<br>
                    <span style="font-size:10px; color:#555;">{msg['time']}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Voice button
        if st.button("🔊 Play Voice Output", key=f"voice_{i}"):
            speak_text(msg["text"])

# ---------------- Input Box ----------------
with st.form("chat_form", clear_on_submit=True):
    st.text_input(
        "Type your question here:",
        key="user_input",
        placeholder="Ask something from the document..."
    )
    st.form_submit_button("Send", on_click=send_message)
