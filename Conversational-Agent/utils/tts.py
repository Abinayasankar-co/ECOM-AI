import pyttsx3
import tempfile
import io
from gtts import gTTS

#Buffer and Streaming for faster transmission to user
def speak_stream(text):
    engine = pyttsx3.init()
    buf = io.BytesIO()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as fp:
        filename = fp.name
    engine.save_to_file(text, filename)
    engine.runAndWait()
    with open(filename, "rb") as f:
        buf.write(f.read())
    buf.seek(0)
    return buf

def speaker_stream(text, lang="en"):
    buf = io.BytesIO()
    tts = gTTS(text=text, lang=lang)
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf

if __name__ == "__main__":
    text = "Hello all"
    output_wav = speaker_stream(text)


