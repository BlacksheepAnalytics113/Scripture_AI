"""
config.py — Central configuration for ScriptureAI
All settings loaded from environment variables with sensible defaults
"""

import os
from dotenv import load_dotenv
load_dotenv()

class sensitiveconfig: 
    # Anthropic API
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    # Bible path
    DEFAULT_TRANSLATION = os.getenv("DEFAULT_TRANSLATION","KJV")
    BIBLE_PATH = os.path.join(os.path.dirname(__file__),"bible_path","bible.db")

    # Audio setting
    AUDIO_CHUNK_DURATION = int(os.getenv("AUDIO_CHUNK_DURATION", 5))
    AUDIO_SIMPLE_RATE = int(os.getenv("AUDIO_SIMPLE_RATE",16000))
    AUDIO_CHANNELS = int(os.getenv("AUDIO_CHANNELS",1))

    # Display Server
    DISPLAY_HOST = os.getenv("DISPLAY_HOST", "0.0.0.0")
    DISPLAY_PORT = int(os.getenv("DISPLAY_PORT", 8000))

    # Detection
    DETECTION_CONFIDENCE_THRESHOLD = float(
        os.getenv("DETECTION_CONFIDENCE_THRESHOLD", 0.7)
    )
 
    # Transcript
    SAVE_TRANSCRIPT = os.getenv("SAVE_TRANSCRIPT", "true").lower() == "true"
    TRANSCRIPT_OUTPUT_DIR = os.getenv("TRANSCRIPT_OUTPUT_DIR", "transcripts")
 
    # Whisper model size
    # Options: tiny, base, small, medium, large
    # tiny = fastest, least accurate
    # medium = good balance for sermon detection
    WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
 
    @classmethod
    def validate(cls):
        """Validate required configuration is present"""
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError(
                "ANTHROPIC_API_KEY is required. "
                "Get yours at console.anthropic.com and add it to your .env file"
            )
        return True
 
 
config = sensitiveconfig()