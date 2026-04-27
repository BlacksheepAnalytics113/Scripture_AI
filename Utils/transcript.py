import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TranscriptSaver:
    """
    Saves the full sermon transcript to a text file with timestamps and detected scriptures highlighted.
    Scriptures are highlighted using **bold** markdown.
    """

    def __init__(self, output_file: str = "sermon_transcript.txt"):
        self.output_file = output_file
        self.transcript_lines = []
        self.detected_scriptures = set()  

    def add_segment(self, start_time: float, end_time: float, text: str):
        timestamp = self._format_timestamp(start_time)
        line = f"[{timestamp}] {text.strip()}\n"
        self.transcript_lines.append(line)
        logger.info(f"Added transcript segment: {line.strip()}")

    def highlight_scripture(self, scripture_ref: str):
        if scripture_ref not in self.detected_scriptures:
            self.detected_scriptures.add(scripture_ref)
            # Find and highlight in existing lines
            for i, line in enumerate(self.transcript_lines):
                if scripture_ref in line:
                    self.transcript_lines[i] = line.replace(scripture_ref, f"**{scripture_ref}**")
            logger.info(f"Highlighted scripture: {scripture_ref}")

    def save_transcript(self):
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.writelines(self.transcript_lines)
            logger.info(f"Transcript saved to {self.output_file}")
        except Exception as e:
            logger.error(f"Failed to save transcript: {e}")

    def _format_timestamp(self, seconds: float) -> str:
        """
        Format seconds into HH:MM:SS.
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

# for testing
if __name__ == "__main__":
    saver = TranscriptSaver()
    saver.add_segment(0, 5, "In the beginning, God created the heavens and the earth.")
    saver.add_segment(5, 10, "As it is written in Genesis 1:1.")
    saver.highlight_scripture("Genesis 1:1")
    saver.save_transcript()