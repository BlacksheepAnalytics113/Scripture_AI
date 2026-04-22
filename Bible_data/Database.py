import sqlite3
import logging
import os
import sys


logger = logging.getLogger(__name__)


class BibleDatabase:
    """
    Queries the local SQLite Bible database for verse text.
    Supports multiple translations (KJV, etc.).
    """

    def __init__(self, db_path: str = "bible.db"):
        """
        Initialize the Bible database connection
        Args:
            db_path: Path to the SQLite database file
        """
        if not os.path.isabs(db_path):
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_path = os.path.normpath(os.path.join(project_root, db_path))
        else:
            self.db_path = db_path

        dir_name = os.path.dirname(self.db_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        # Initialize database if it doesn't exist or has no data
        self._init_database_if_needed()

        self.db_con = sqlite3.connect(self.db_path)
        logger.info(f"Connected to Bible database: {self.db_path}")

    def _init_database_if_needed(self):
        """Initialize database if table doesn't exist."""
        db_con = sqlite3.connect(self.db_path)
        cursor_connect = db_con.cursor()
        
        try:
            cursor_connect.execute("SELECT COUNT(*) FROM Verses_db LIMIT 1")
            logger.info("Database table exists, skipping initialization")
            db_con.close()
            return
        except sqlite3.OperationalError:
            logger.info("Database table not found, initializing...")
            db_con.close()
            
            # Import and run setup from Bible_db
            try:
                from Utils.Bible_db import setup_database
                # from utils.Bible_db import setup_database
                setup_database(self.db_path)
                logger.info("Database initialized successfully")
            except ImportError as e:
                logger.error(f"Could not import setup_database: {e}")
                try:
                    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    from Utils.Bible_db import setup_database
                    setup_database(self.db_path)
                    logger.info("Database initialized successfully")
                except ImportError as e2:
                    logger.error(f"Failed to initialize database: {e2}")

    def get_verse(self, book: str, chapter: int, verse: int, translation: str = "KJV"):
        """
        Retrieve a single verse from the database.

        Args:
            book: Bible book name (e.g., "John", "Genesis")
            chapter: Chapter number
            verse: Verse number
            translation: Bible translation (default: "KJV")

        Returns:
            Tuple (book, chapter, verse, text, translation), or None if not found
        """
        try:
            cursor_connect = self.db_con.cursor()
            cursor_connect.execute("""
                SELECT book, chapter, verse, text, translation
                FROM Verses_db
                WHERE book = ? AND chapter = ? AND verse = ? AND translation = ?
            """, (book, chapter, verse, translation))

            result = cursor_connect.fetchone()
            return result if result else None
        except sqlite3.Error as e:
            logger.error(f"Database query error: {e}")
            return None

    def get_chapter(self, book: str, chapter: int, translation: str = "KJV"):
        """
        Retrieve all verses from a chapter.

        Args:
            book: Bible book name
            chapter: Chapter number
            translation: Bible translation (default: "KJV")

        Returns:
            List of verse tuples
        """
        try:
            cursor_connect = self.db_con.cursor()
            cursor_connect.execute("""
                SELECT book, chapter, verse, text, translation
                FROM Verses_db
                WHERE book = ? AND chapter = ? AND translation = ?
                ORDER BY verse ASC
            """, (book, chapter, translation))

            return cursor_connect.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Database query error: {e}")
            return []

    def get_verses_range(
        self,
        book: str,
        chapter: int,
        start_verse: int,
        end_verse: int,
        translation: str = "KJV"
    ):
        """
        Retrieve a range of verses from a chapter.

        Args:
            book: Bible book name
            chapter: Chapter number
            start_verse: Starting verse number
            end_verse: Ending verse number (inclusive)
            translation: Bible translation (default: "KJV")

        Returns:
            List of verse tuples
        """
        try:
            cursor_connect = self.db_con.cursor()
            cursor_connect.execute("""
                SELECT book, chapter, verse, text, translation
                FROM Verses_db
                WHERE book = ? AND chapter = ? AND verse BETWEEN ? AND ? AND translation = ?
                ORDER BY verse ASC
            """, (book, chapter, start_verse, end_verse, translation))

            return cursor_connect.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Database query error: {e}")
            return []

    def search_verses(
        self,
        search_text: str,
        translation: str = "KJV",
        limit: int = 200
    ):
        """
        Search for verses containing specific text (case-insensitive).

        Args:
            search_text: Text to search for
            translation: Bible translation (default: "KJV")
            limit: Maximum number of results (default: 200)

        Returns:
            List of verse tuples
        """
        try:
            cursor_connect = self.db_con.cursor()
            cursor_connect.execute("""
                SELECT book, chapter, verse, text, translation
                FROM Verses_db
                WHERE text LIKE ? AND translation = ?
                LIMIT ?
            """, (f"%{search_text}%", translation, limit))

            return cursor_connect.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Database query error: {e}")
            return []

    def get_verse_count(self, translation: str = "KJV") -> int:
        """
        Get total number of verses in the database for a translation.

        Args:
            translation: Bible translation (default: "KJV")

        Returns:
            Total number of verses
        """
        try:
            cursor_connect = self.db_con.cursor()
            cursor_connect.execute(
                "SELECT COUNT(*) FROM Verses_db WHERE translation = ?",
                (translation,)
            )
            count = cursor_connect.fetchone()[0]
            return count
        except sqlite3.Error as e:
            logger.error(f"Database query error: {e}")
            return 0

    def get_available_translations(self) -> list:
        """
        Get list of available Bible translations in the database.

        Returns:
            List of translation names
        """
        try:
            cursor_connect = self.db_con.cursor()
            cursor_connect.execute(
                "SELECT DISTINCT translation FROM Verses_db ORDER BY translation"
            )
            translations = [row[0] for row in cursor_connect.fetchall()]
            return translations
        except sqlite3.Error as e:
            logger.error(f"Database query error: {e}")
            return []

    def close(self):
        """Close the database connection."""
        if self.db_con:
            self.db_con.close()
            logger.info("Database connection closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Example usage (for testing)
if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_root, "bible.db")
    db = BibleDatabase(db_path)

    # Test getting a single verse
    verse = db.get_verse("John", 3, 16)
    if verse:
        book, chapter, verse_num, text, translation = verse
        print(f"{book} {chapter}:{verse_num} ({translation}): {text}")

    # Test getting a chapter
    chapter = db.get_chapter("John", 1)
    print(f"\nJohn Chapter 1 has {len(chapter)} verses")

    # Test search
    results = db.search_verses("love")
    print(results)
    print(f"\nFound {len(results)} verses with 'love':")

    # Test verse count
    print(f"\nTotal verses: {db.get_verse_count()}")

    # Test available translations
    print(f"Available translations: {db.get_available_translations()}")

    db.close()
