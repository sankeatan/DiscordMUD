import sqlite3
from contextlib import contextmanager
from typing import Generator
import logging

logger = logging.getLogger("db_manager")

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Create a context-managed database connection."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def initialize_database(self) -> None:
        """Initialize all database tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS characters (
                    discord_id TEXT PRIMARY KEY,
                    name TEXT UNIQUE,
                    class TEXT,
                    level INTEGER,
                    hp INTEGER,
                    attack INTEGER,
                    defense INTEGER,
                    magic INTEGER,
                    inventory TEXT,
                    location TEXT
                )
            ''')
            conn.commit()