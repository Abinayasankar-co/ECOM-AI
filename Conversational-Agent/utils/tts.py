#import pyttsx3
import tempfile
import io
from gtts import gTTS



def speaker_stream(text, lang="en"):
    buf = io.BytesIO()
    tts = gTTS(text=text, lang=lang)
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf

if __name__ == "__main__":
    text = "Hello all"
    output_wav = speaker_stream(text)


