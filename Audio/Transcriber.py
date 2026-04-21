"""
Whisper runs locally on your machine — no internet required for transcription. The model is downloaded once on first use.
"""

import logging
import whisper
import numpy as np
 
logger = logging.getLogger(__name__)
 
 
class Transcriber:
    """
    Converts audio files to text using OpenAI Whisper.
    Recommendation: Start with 'base', upgrade to 'small', if accuracy on pastor's accent is insufficient.
    """

    def __init__(self, model_size: str = "base"):
        logger.info(f"Loading Whisper model: {model_size}")
        logger.info("(First run downloads the model — this may take a minute)")
 
        self.model = whisper.load_model(model_size)
        self.model_size = model_size
 
        logger.info(f"Whisper {model_size} model loaded")

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribe an audio file to text.
        Args:
            audio_path: Path to WAV audio file
        Returns:
            Transcribed text string, or empty string if failed
        """
        try:
            result = self.model.transcribe(
                audio_path,
                language="en",          # English
                task="transcribe",
                fp16=False,         
                verbose=False
            )
 
            text = result.get("text", "").strip()
            return text
 
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""
 
    def transcribe_with_timestamps(self, audio_path: str) -> list:
        """
        Transcribe with word-level timestamps.
        Useful for more precise scripture timing.
 
        Returns list of segments with start/end times and text.
        """
        try:
            result = self.model.transcribe(
                audio_path,
                language="en",
                word_timestamps=True,
                verbose=False
            )
            return result.get("segments", [])
 
        except Exception as e:
            logger.error(f"Timestamped transcription error: {e}")
            return []