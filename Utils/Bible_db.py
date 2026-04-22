
"""
Downlaod and populates the local SQLite Bible database with KJV translation data from publiic domain source.
Run this once before starting ScriptureAI:
    python utils/setup_bible_db.py
"""

import sqlite3
import json
import os
import urllib.request
import logging


logger = logging.getLogger(__name__)

# KJV Bible: format;JSON
# Source: https://github.com/aruljohn/Bible-kjv 

KJV_URL = "https://github.com/aruljohn/Bible-kjv/blob/master/Books.json"


def setup_database(db_path:str):
    os.path.join(os.path.dirname(db_path),exist_ok=True)
    db_con = sqlite3.Cursor(db_path)
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
        ON verses(book, chapter, verse, translation)
    """)
 
    db_con.commit()

    # check if the data has been populated
    cursor_connect.execute("SELECT COUNT(*) FROM verses_db WHERE translation = 'KJV'")
    count = cursor_connect.fetchone()[0]

    if count > 0:
        print(f"Bible database already has a {count:} KJV verses")
        db_con.close()
        return
    # Download  KJV Data
    try:
        with urllib.request.urlopen(KJV_URL) as response:
            data = json.loads(response.read().decode())
        print(f"Download complete, Populating database!!!")

    # Insert verse
    count_verses = 0
    for d in data:
        book_name = data["name"]
        




    

