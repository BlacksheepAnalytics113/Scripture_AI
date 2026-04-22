import sqlite3
import json
import os
import urllib.request

KJV_URL = "https://raw.githubusercontent.com/aruljohn/Bible-kjv/master/Books.json"


def format_book_url(book_name):
    """Format book name correctly for GitHub URL"""
    
    # Special cases that don't follow normal rules
    special_cases = {
        "Song of Solomon": "SongofSolomon",
        "1 Samuel": "1Samuel",
        "2 Samuel": "2Samuel",
        "1 Kings": "1Kings",
        "2 Kings": "2Kings",
        "1 Chronicles": "1Chronicles",
        "2 Chronicles": "2Chronicles",
        "1 Corinthians": "1Corinthians",
        "2 Corinthians": "2Corinthians",
        "1 Thessalonians": "1Thessalonians",
        "2 Thessalonians": "2Thessalonians",
        "1 Timothy": "1Timothy",
        "2 Timothy": "2Timothy",
        "1 Peter": "1Peter",
        "2 Peter": "2Peter",
        "1 John": "1John",
        "2 John": "2John",
        "3 John": "3John",
        "1 Samuel": "1Samuel",
        "2 Samuel": "2Samuel",
    }

    if book_name in special_cases:
        formatted = special_cases[book_name]
    elif book_name[0].isdigit():
        formatted = book_name.replace(" ", "", 1)
    else:
        formatted = book_name.replace(" ", "%20")

    return (
        "https://raw.githubusercontent.com/aruljohn/Bible-kjv/master/"
        + formatted
        + ".json"
    )


def setup_database(db_path: str):

    dir_name = os.path.dirname(db_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    db_con = sqlite3.connect(db_path)
    cursor_connect = db_con.cursor()

    cursor_connect.execute("""
        CREATE TABLE IF NOT EXISTS Verses_db (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            book        TEXT NOT NULL,
            chapter     INTEGER NOT NULL,
            verse       INTEGER NOT NULL,
            text        TEXT NOT NULL,
            translation TEXT NOT NULL DEFAULT 'KJV'
        )
    """)

    cursor_connect.execute("""
        CREATE INDEX IF NOT EXISTS idx_verse_lookup
        ON Verses_db(book, chapter, verse, translation)
    """)

    db_con.commit()

    # Check if already populated
    cursor_connect.execute("SELECT COUNT(*) FROM Verses_db WHERE translation = 'KJV'")
    count = cursor_connect.fetchone()[0]

    if count > 0:
        print(f"Bible database already has {count:,} KJV verses")
        db_con.close()
        return
    print("Downloading KJV Bible data...")

    try:
        # Get list of book names
        with urllib.request.urlopen(KJV_URL) as response:
            book_names = json.loads(response.read().decode())

        print(f"Found {len(book_names)} books")
    
        verse_count = 0
        failed_books = []
        for book_name in book_names:
            book_url = format_book_url(book_name)

            try:
                with urllib.request.urlopen(book_url) as response:
                    book_data = json.loads(response.read().decode())

                chapters = book_data.get("chapters", [])

                for chapter_idx, chapter_data in enumerate(chapters, 1):
                    if isinstance(chapter_data, dict):
                        chapter_number = int(chapter_data.get("chapter", chapter_idx))
                        verse_list = chapter_data.get("verses", [])
                    else:
                        chapter_number = chapter_idx
                        verse_list = chapter_data

                    if isinstance(verse_list, list) and verse_list and isinstance(verse_list[0], dict):
                        for verse_item in verse_list:
                            verse_idx = int(verse_item.get("verse", 0))
                            verse_text = verse_item.get("text", "").strip()
                            cursor_connect.execute("""
                                INSERT INTO Verses_db (book, chapter, verse, text, translation)
                                VALUES (?, ?, ?, ?, 'KJV')
                            """, (book_name, chapter_number, verse_idx, verse_text))
                            verse_count += 1
                    else:
                        for verse_idx, verse_text in enumerate(verse_list, 1):
                            cursor_connect.execute("""
                                INSERT INTO Verses_db (book, chapter, verse, text, translation)
                                VALUES (?, ?, ?, ?, 'KJV')
                            """, (book_name, chapter_number, verse_idx, verse_text))
                            verse_count += 1

                db_con.commit()
                print(f"{book_name} ({verse_count:,} verses so far...)")

            except Exception as e:
                print(f"Failed: {book_name} — {e}")
                failed_books.append(book_name)
                continue

        print(f"\nDone! {verse_count:,} KJV verses loaded")

        if failed_books:
            print(f"{len(failed_books)} books failed: {failed_books}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db_con.close()
setup_database("bible.db")


