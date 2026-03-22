from gtts import gTTS
import os
import uuid

def text_to_speech(text, lang="en"):
    """
    Converts text to speech and saves it as an MP3 file.
    Returns the file path.
    """
    filename = f"static/audio/{uuid.uuid4()}.mp3"
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)
    return filename