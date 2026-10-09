import os
from gtts import gTTS

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

def text_to_speech(text, lang="en", filename="speech.mp3"):
    if not text or not text.strip():
        raise ValueError("No text available for audio generation.")

    safe_name = os.path.basename(filename)
    path = os.path.join(TEMP_DIR, safe_name)
    gTTS(text=text, lang=lang).save(path)
    return path
