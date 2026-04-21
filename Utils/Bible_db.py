
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

# Public domain KJV Bible JSON
