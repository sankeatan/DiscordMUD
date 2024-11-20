import json
from typing import Optional
import logging
from ...models.character import Character
from ..db_manager import DatabaseManager

logger = logging.getLogger("character_repository")

class CharacterRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def save(self, discord_id: str, character: Character) -> None:
        """Save a character to the database."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO characters (
                    discord_id, name, class, level, hp, attack, defense, magic, 
                    inventory, location
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
                json.dumps(character.location)
            ))
            conn.commit()

    def load(self, discord_id: str) -> Optional[Character]:
        """Load a character from the database."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM characters WHERE discord_id = ?', (discord_id,))
            row = cursor.fetchone()

        if row:
            return Character(
                name=row[1],
                player_class=row[2],
                level=row[3],
                stats={
                    "HP": row[4],
                    "Attack": row[5],
                    "Defense": row[6],
                    "Magic": row[7]
                },
                inventory=row[8].split(",") if row[8] else [],
                location=tuple(json.loads(row[9])) if row[9] else (0, 0)
            )
        return None