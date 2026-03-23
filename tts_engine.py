import pyttsx3
import os
import uuid

def text_to_speech(text, lang="en"):
    """
    Converts text to speech (offline) and saves it as an MP3 file.
    Returns the file path.
    """
    try:
        if not text:
            return None

        # Ensure folder exists
        os.makedirs("static/audio", exist_ok=True)

        filename = f"static/audio/{uuid.uuid4()}.mp3"

        # Initialize a temporary TTS engine for this request
        engine = pyttsx3.init()
        engine.setProperty('rate', 180)   # speaking speed
        engine.setProperty('volume', 1.0) # volume 0-1

        # Save speech to file
        engine.save_to_file(text[:400], filename)  # limit text for faster generation
        engine.runAndWait()  # blocks only this request
        engine.stop()        # release resources

        return filename

    except Exception as e:
        print(f"TTS Error: {e}")
        return None