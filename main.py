import os
import base64
import time
import streamlit as st
from PyPDF2 import PdfReader
from deep_translator import GoogleTranslator

from utils.auth import authenticate, create_user
from utils.summarizer import generate_summary
from utils.mindmap import generate_mindmap
from utils.tts import text_to_speech

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

st.set_page_config(page_title="MindMapBot", page_icon="🧠", layout="wide")

def ensure_state():
    defaults = {
        "authenticated": False,
        "user": None,
        "summary_points": [],
        "translated_points": [],
        "full_text": "",
        "flashcard_index": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def download_link(text, filename, label):
    encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
    return (
        '<a href="data:text/plain;base64,{}" download="{}" '
        'style="text-decoration:none;background:#1976d2;color:white;'
        'padding:10px 16px;border-radius:8px;display:inline-block;">'
        '{}</a>'
    ).format(encoded, filename, label)

def reset_session():
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.summary_points = []
    st.session_state.translated_points = []
    st.session_state.full_text = ""
    st.session_state.flashcard_index = 0

ensure_state()
st.title("🧠 MindMapBot")
st.caption("AI-Powered Learning Companion")

if not st.session_state.authenticated:
    page = st.sidebar.radio("Account", ["🔐 Login", "🆕 Register"])

    if page == "🔐 Login":
        st.subheader("🔐 Login")
        with st.form("login_form"):
            login_id = st.text_input("Email or Phone")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

        if submit:
            ok, msg, user = authenticate(login_id, password)
            if ok:
                st.session_state.authenticated = True
                st.session_state.user = user
                st.rerun()
            else:
                st.error(msg)
    else:
        st.subheader("🆕 Create Account")
        with st.form("register_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            password = st.text_input("Password", type="password")
            confirm = st.text_input("Confirm Password", type="password")
            submit = st.form_submit_button("Create Account")

        if submit:
            if password != confirm:
                st.error("Passwords do not match.")
            else:
                ok, msg = create_user(username, email, phone, password)
                if ok:
                    st.success(msg + " Go to Login.")
                else:
                    st.error(msg)

    st.stop()

st.sidebar.markdown("**👤 {}**".format(st.session_state.user["username"]))

section = st.sidebar.radio(
    "Navigate",
    [
        "📤 Upload PDF",
        "📋 English & Hindi Summary",
        "🧠 Flashcards",
        "🗺️ Mind Map",
        "🔊 Text-to-Speech",
        "🚪 Logout",
    ],
)

if section == "🚪 Logout":
    reset_session()
    st.success("Logged out.")
    st.rerun()

elif section == "📤 Upload PDF":
    st.header("📤 Upload PDF")

    uploaded = st.file_uploader(
        "Choose a PDF file", type=["pdf"]
    )

    if uploaded:
        st.success("PDF uploaded successfully.")

        file_path = os.path.join(TEMP_DIR, os.path.basename(uploaded.name))
        with open(file_path, "wb") as f:
            f.write(uploaded.getbuffer())

        try:
            reader = PdfReader(file_path)
            pages = []
            for page in reader.pages:
                pages.append(page.extract_text() or "")
            full_text = "\n".join(pages).strip()
        except Exception as e:
            st.error("Could not read this PDF: {}".format(e))
            st.stop()

        st.session_state.full_text = full_text

        if not full_text:
            st.error(
                "No selectable text was found. This may be a scanned/image-only PDF."
            )
        else:
            st.subheader("📄 Extracted Text Preview")
            st.text_area(
                "PDF text",
                full_text[:5000],
                height=260,
            )
            st.caption(
                "Extracted approximately {} characters.".format(len(full_text))
            )

            if st.button("📝 Generate AI Summary", type="primary"):
                with st.spinner("Gemini is generating the summary..."):
                    start = time.time()
                    try:
                        points = generate_summary(full_text)

                        if points and not (
                            len(points) == 1
                            and points[0].startswith(("❌", "ERROR"))
                        ):
                            st.session_state.summary_points = points

                            translated = []
                            translator = GoogleTranslator(
                                source="auto", target="hi"
                            )

                            for point in points:
                                try:
                                    result = translator.translate(point)
                                    translated.append(result or "")
                                except Exception:
                                    translated.append("अनुवाद उपलब्ध नहीं है।")

                            st.session_state.translated_points = translated
                            st.session_state.flashcard_index = 0

                            st.success("✅ English and Hindi summaries generated.")
                            st.caption(
                                "Time taken: {:.2f} seconds".format(
                                    time.time() - start
                                )
                            )
                        else:
                            st.error(points[0] if points else "No summary generated.")

                    except Exception as e:
                        st.error("❌ Summary generation failed: {}".format(e))

elif section == "📋 English & Hindi Summary":
    points = [
        p for p in st.session_state.summary_points
        if isinstance(p, str) and p.strip()
    ]

    if not points:
        st.info("Upload a PDF and generate a summary first.")
    else:
        hindi = [
            p for p in st.session_state.translated_points
            if isinstance(p, str) and p.strip()
        ]

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📝 English Summary")
            for i, point in enumerate(points, 1):
                st.markdown("**{}.** {}".format(i, point))

            english_text = "\n".join(points)
            st.markdown(
                download_link(
                    english_text,
                    "summary_english.txt",
                    "📥 Download English Summary",
                ),
                unsafe_allow_html=True,
            )

            if st.button("🔊 Play English Audio"):
                path = text_to_speech(
                    english_text, "en", "summary_english.mp3"
                )
                st.audio(path, format="audio/mp3")

        with col2:
            st.subheader("🌐 Hindi Summary")
            for i, point in enumerate(hindi, 1):
                st.markdown("**{}.** {}".format(i, point))

            hindi_text = "\n".join(hindi)
            st.markdown(
                download_link(
                    hindi_text,
                    "summary_hindi.txt",
                    "📥 Download Hindi Summary",
                ),
                unsafe_allow_html=True,
            )

            if st.button("🔊 Play Hindi Audio"):
                path = text_to_speech(
                    hindi_text, "hi", "summary_hindi.mp3"
                )
                st.audio(path, format="audio/mp3")

elif section == "🧠 Flashcards":
    points = st.session_state.summary_points

    if not points:
        st.info("Generate a summary first.")
    else:
        total = len(points)
        index = min(st.session_state.flashcard_index, total - 1)

        st.subheader("🧠 Flashcards")
        st.markdown("### Flashcard {} / {}".format(index + 1, total))
        st.info(points[index])

        left, right = st.columns(2)
        with left:
            if st.button("⬅️ Previous") and index > 0:
                st.session_state.flashcard_index -= 1
                st.rerun()
        with right:
            if st.button("Next ➡️") and index < total - 1:
                st.session_state.flashcard_index += 1
                st.rerun()

elif section == "🗺️ Mind Map":
    if not st.session_state.summary_points:
        st.info("Generate a summary first.")
    else:
        st.subheader("🗺️ Visual Mind Map")
        try:
            image_path = generate_mindmap(
                st.session_state.summary_points
            )
            st.image(
                image_path,
                caption="AI-generated Mind Map",
                use_container_width=True,
            )
            with open(image_path, "rb") as f:
                st.download_button(
                    "📥 Download Mind Map",
                    f,
                    file_name="mindmap.png",
                    mime="image/png",
                )
        except Exception as e:
            st.error("Mind map generation failed: {}".format(e))

elif section == "🔊 Text-to-Speech":
    if not st.session_state.summary_points:
        st.info("Generate a summary first.")
    else:
        st.subheader("🔊 Text-to-Speech")
        language = st.selectbox(
            "Language", ["English", "Hindi"]
        )

        if language == "English":
            text = "\n".join(st.session_state.summary_points)
            lang = "en"
            filename = "summary_english.mp3"
        else:
            text = "\n".join(st.session_state.translated_points)
            lang = "hi"
            filename = "summary_hindi.mp3"

        if st.button("Generate Audio"):
            try:
                path = text_to_speech(text, lang, filename)
                st.audio(path, format="audio/mp3")
                with open(path, "rb") as f:
                    st.download_button(
                        "📥 Download Audio",
                        f,
                        file_name=filename,
                        mime="audio/mpeg",
                    )
            except Exception as e:
                st.error("Audio generation failed: {}".format(e))
