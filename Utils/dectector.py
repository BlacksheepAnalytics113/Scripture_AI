"""
Takes transcribed sermon text and uses Claude to:
1. Detect if a Bible scripture is being referenced
2. Extract the book, chapter, and verse
3. Return structured detection results
"""

import json
import logging
import anthropic
import os

logger = logging.getLogger(__name__)


class ScriptureDetector:

    def __init__(self, api_key: str):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = "claude-sonnet-4-6"
        self._recent_detections = []
        self._max_recent = 5

    async def detect(self, text: str) -> dict | None:
        if not text or len(text.strip()) < 5:
            return None

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=300,
                messages=[
                    {
                        "role": "user",
                        "content": self._build_prompt(text)
                    }
                ]
            )

            result_text = response.content[0].text.strip()
            result = self._parse_response(result_text)

            if result and result.get("detected"):
                ref_key = f"{result['book']}{result['chapter']}:{result['verse']}"
                if ref_key in self._recent_detections:
                    logger.debug(f"Skipping recently shown scripture: {ref_key}")
                    return None
                self._recent_detections.append(ref_key)
                if len(self._recent_detections) > self._max_recent:
                    self._recent_detections.pop(0)
                return result
            return None
        except Exception as e:
            logger.error(f"Scripture detection error: {e}")
            return None

    def _build_prompt(self, text: str) -> str:
        return f"""You are analysing transcribed sermon speech to detect Bible scripture references.
Transcribed text:
"{text}"

Return this exact JSON format:

If scripture IS detected:
{{
  "detected": true,
  "book": "John",
  "chapter": 3,
  "verse": 16,
  "confidence": 0.95,
  "original_reference": "John 3 verse 16"
}}

If scripture is NOT detected:
{{
  "detected": false
}}
"""

    def _parse_response(self, response_text: str) -> dict | None:
        """Parse Claude's JSON response"""
        try:
            clean = response_text.strip()
            clean = clean.replace("```json", "").replace("```", "").strip()

            result = json.loads(clean)
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse detection response: {e}")
            logger.debug(f"Raw response: {response_text}")
            return None


# (for testing)
if __name__ == "__main__":
    import asyncio
    import os

    async def test_detector():
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("Please set ANTHROPIC_API_KEY environment variable")
            return

        detector = ScriptureDetector(api_key)
        test_text = "As it is written in John chapter 3 verse 16, for God so loved the world..."
        result = await detector.detect(test_text)

        if result:
            print(f"Detected scripture: {result}")
        else:
            print("No scripture detected")
    asyncio.run(test_detector())