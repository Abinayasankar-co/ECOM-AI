import pyttsx3
import soundfile as sf
import sounddevice as sd
import tempfile
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def synthesize_voice(text):
    """Synthesize voice from text with error handling"""
    try:
        engine = pyttsx3.init()
        
        # Configure voice settings
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)  # Use first available voice
        
        engine.setProperty('rate', 150)  # Speed of speech
        engine.setProperty('volume', 0.9)  # Volume level
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            filename = tmp_file.name
        
        # Save to file
        engine.save_to_file(text, filename)
        engine.runAndWait()
        
        logger.info(f"Successfully synthesized audio for: {text[:50]}...")
        return filename
        
    except Exception as e:
        logger.error(f"Failed to synthesize voice: {e}")
        # Return a default audio file or None
        return None

def play_audio(file_path):
    """Play audio file with error handling"""
    if not file_path or not os.path.exists(file_path):
        logger.warning("Audio file not found or invalid path")
        return
    
    try:
        data, rate = sf.read(file_path)
        sd.play(data, rate)
        sd.wait()
        logger.info("Audio played successfully")
    except Exception as e:
        logger.error(f"Failed to play audio: {e}")

def cleanup_audio_file(file_path):
    """Clean up temporary audio files"""
    try:
        if file_path and os.path.exists(file_path):
            os.unlink(file_path)
            logger.info(f"Cleaned up audio file: {file_path}")
    except Exception as e:
        logger.error(f"Failed to cleanup audio file: {e}")
