"""
main_demo_no_api.py — ScriptureAI Demo Without Anthropic API

This version tests the display server and Bible lookup WITHOUT requiring
Anthropic API credits. Uses hardcoded scripture references instead.

Perfect for testing the UI before setting up API credits.
"""

import asyncio
import logging
import threading
from Config.Config import config
from Bible_data.Database import BibleDatabase
from display.Server import DisplayServer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ScriptureAIDemo:
    """Simplified demo that tests display server without API calls"""

    def __init__(self):
        logger.info("Initializing ScriptureAI Demo (No API)...")
        
        # Initialize only necessary components
        self.bible_db = BibleDatabase(config.BIBLE_PATH)
        self.display_server = DisplayServer(
            host=config.DISPLAY_HOST,
            port=config.DISPLAY_PORT
        )
        
        logger.info("ScriptureAI Demo initialized successfully")

    def start_display_server(self):
        """Start the display server in a background thread"""
        logger.info(f"Starting display server on {config.DISPLAY_HOST}:{config.DISPLAY_PORT}")
        thread = threading.Thread(target=self.display_server.start, daemon=True)
        thread.start()
        logger.info("Display server running in background")

    async def run_demo(self):
        """Run demo with hardcoded scripture references (no API needed)"""
        logger.info("\n" + "="*60)
        logger.info("Running DEMO MODE (No Anthropic API required)")
        logger.info("="*60)
        
        # Hardcoded scriptures to display
        scriptures = [
            {"book": "Genesis", "chapter": 1, "verse": 1},
            {"book": "John", "chapter": 3, "verse": 16},
            {"book": "Psalms", "chapter": 23, "verse": 1},
            {"book": "Proverbs", "chapter": 3, "verse": 5},
            {"book": "Romans", "chapter": 8, "verse": 28},
        ]
        
        for i, scripture_ref in enumerate(scriptures, 1):
            book = scripture_ref["book"]
            chapter = scripture_ref["chapter"]
            verse = scripture_ref["verse"]
            
            logger.info(f"\n[{i}/{len(scriptures)}] Looking up {book} {chapter}:{verse}...")
            
            try:
                result = self.bible_db.get_verse(book, chapter, verse, "KJV")
                
                if result:
                    _, chap, v, text, trans = result
                    
                    # Create detection object
                    detection = {
                        "detected": True,
                        "book": book,
                        "chapter": chapter,
                        "verse": verse,
                        "text": text,
                        "original_reference": f"{book} {chapter}:{verse}",
                        "confidence": 1.0
                    }
                    
                    logger.info(f"Found: {text[:80]}...")
                    logger.info(f"Broadcasting to display screens...")
                    
                    # Broadcast to display
                    await self.display_server.broadcast(detection)
                else:
                    logger.warning(f"Verse not found in database: {book} {chapter}:{verse}")
            
            except Exception as e:
                logger.error(f"Error processing {book} {chapter}:{verse}: {e}")
            
            # Wait before next verse
            logger.info("Waiting 3 seconds before next verse...")
            await asyncio.sleep(3)
        
        logger.info("\n" + "="*60)
        logger.info("Demo completed successfully!")
        logger.info("="*60)


async def main():
    """Main entry point"""
    try:
        app = ScriptureAIDemo()
        
        # Start display server
        app.start_display_server()
        
        # Wait for server to start
        await asyncio.sleep(1)
        
        # Run demo
        await app.run_demo()
        
        logger.info(f"\nDisplay available at: http://localhost:{config.DISPLAY_PORT}/display")
        logger.info("Keep this running and open the display URL in a browser")
        logger.info("Open on multiple devices to test multi-screen broadcasting\n")
        
        # Keep running
        while True:
            await asyncio.sleep(1)
        
    except KeyboardInterrupt:
        logger.info("\n Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
