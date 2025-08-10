import os
import tempfile
import streamlit as st
from gtts import gTTS  # or your TTS library

def synthesize_voice(text, lang="en"):
    """Generate TTS audio file and return file path."""
    tts = gTTS(text=text, lang=lang)
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp_file.name)
    return tmp_file.name

def play_audio(file_path):
    """Play audio in the browser (works in Streamlit Cloud)."""
    with open(file_path, "rb") as f:
        audio_bytes = f.read()
    st.audio(audio_bytes, format="audio/mp3")

def cleanup_audio_file(file_path):
    """Remove temp audio file."""
    if os.path.exists(file_path):
        os.remove(file_path)
