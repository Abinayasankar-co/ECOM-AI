import pyttsx3
import tempfile
import io

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


if __name__ == "__main__":
    txt = "Hello world"
    speak(txt)