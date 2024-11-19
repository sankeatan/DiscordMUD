import sqlite3
import json

DB_PATH = "game_data.db"

def initialize_database():
    """Initialize the characters table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
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
    conn.close()

def save_character(discord_id, character):
    """Save a character to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO characters (
            discord_id, name, class, level, hp, attack, defense, magic, inventory, location
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        discord_id,
        character.name,
        character.player_class,
        character.level,
        character.stats["HP"],
        character.stats["Attack"],
        character.stats["Defense"],
        character.stats["Magic"],
        ",".join(character.inventory),
        json.dumps(character.location)# Convert list to string for storage
    ))
    conn.commit()
    conn.close()

def load_character(discord_id):
    """Load a character from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM characters WHERE discord_id = ?', (discord_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "discord_id": row[0],
            "name": row[1],
            "class": row[2],
            "level": row[3],
            "stats": {
                "HP": row[4],
                "Attack": row[5],
                "Defense": row[6],
                "Magic": row[7]
            },
            "inventory": row[8].split(",") if row[8] else [],
            "location": json.loads(row[9]) if row[9] else (0, 0),
        }
    return None
