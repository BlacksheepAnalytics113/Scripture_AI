"""
Real time audio captures: Basically captures audio from the default microphone in chunks and yeilds them as a numpy arrays for transacription
"""

import asyncio
import logging
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav
import tempfile
import os

logger = logging.getLogger(__name__)
 
 
class AudioCapture:
    """
    Captures live audio from the microphone in configurable chunks,
    each chunk is yielded as a tempoary WAV file path for the whisper transcriber to process
    """
    def __init__(self,sample_rate: int = 16000,channels: int = 1,chunk_duration: int = 5):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_duration = chunk_duration
        self.chunk_size = sample_rate * chunk_duration

    async def stream(self):
        """
        Async generator that yeilds audio as WAV file paths.Each chunk is chunk_duration of audio
        """
        logger.info(
            f"Starting audio capture"
            f"{self.chunk_duration}s chunks at {self.sample_rate}Hz"
        )
        loop = asyncio.get_event_loop()
        while True:
            # Capture audio chunk to avoid blocking
            audio_data = await loop.run_in_executor(
                None,
                self._capture_chunk
            )
 
            if audio_data is not None:
                # Save to temporary WAV file
                tmp_path = self._save_to_wav(audio_data)
                yield tmp_path
                # Clean up temp file after use
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass
 
    def _capture_chunk(self) -> np.ndarray:
        try:
            audio_data = sd.rec(
                frames=self.chunk_size,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.int16
            )
            sd.wait()  # Wait until recording is complete
            return audio_data
        except Exception as e:
            logger.error(f"Audio capture error: {e}")
            return None
 
    def _save_to_wav(self, audio_data: np.ndarray) -> str:
        """Save numpy audio array to temporary WAV file"""
        tmp_file = tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        )
        wav.write(tmp_file.name, self.sample_rate, audio_data)
        return tmp_file.name
 
    @staticmethod
    def list_devices():
        """List available audio input devices"""
        print("\nAvailable audio devices:")
        print(sd.query_devices())
