import pyttsx3
import tempfile
import io

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

