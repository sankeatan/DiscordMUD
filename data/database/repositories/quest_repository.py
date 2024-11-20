from typing import List, Optional, Dict, Any
import json
import logging
from datetime import datetime
from ...models.quest import Quest
from ..db_manager import DatabaseManager

logger = logging.getLogger(__name__)

class QuestRepository:
    """Repository for managing quest data in the database."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self._initialize_table()

    def _initialize_table(self) -> None:
        """Create the quests table if it doesn't exist."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quests (
                    quest_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    difficulty INTEGER NOT NULL,
                    theme TEXT NOT NULL,
                    location TEXT NOT NULL,
                    rewards TEXT,
                    completed_by TEXT,
                    completed_at TEXT,
                    created_at TEXT NOT NULL,
                    expires_at TEXT,
                    active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Create index for location lookups
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_quests_location 
                ON quests(location)
            ''')
            
            conn.commit()

    def save(self, quest: Quest) -> int:
        """Save a quest to the database and return its ID."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO quests (
                    title, description, difficulty, theme, location,
                    rewards, completed_by, completed_at, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                quest.title,
                quest.description,
                quest.difficulty,
                quest.theme,
                json.dumps(quest.location),
                json.dumps(quest.rewards),
                quest.completed_by,
                quest.completed_at.isoformat() if quest.completed_at else None,
                datetime.now().isoformat()
            ))
            conn.commit()
            return cursor.lastrowid

    def get_quest(self, quest_id: int) -> Optional[Quest]:
        """Retrieve a specific quest by ID."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM quests WHERE quest_id = ?', (quest_id,))
            row = cursor.fetchone()

        if row:
            return self._row_to_quest(row)
        return None

    def get_quests_at_location(self, location: tuple) -> List[Quest]:
        """Get all active quests at a specific location."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM quests 
                WHERE location = ? AND active = TRUE 
                AND (completed_by IS NULL)
                AND (expires_at IS NULL OR expires_at > ?)
            ''', (
                json.dumps(location),
                datetime.now().isoformat()
            ))
            rows = cursor.fetchall()

        return [self._row_to_quest(row) for row in rows]

    def get_active_quests_for_player(self, player_id: str) -> List[Quest]:
        """Get all active quests for a specific player."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM quests 
                WHERE completed_by = ? AND active = TRUE
                AND (expires_at IS NULL OR expires_at > ?)
            ''', (
                player_id,
                datetime.now().isoformat()
            ))
            rows = cursor.fetchall()

        return [self._row_to_quest(row) for row in rows]

    def update_quest(self, quest: Quest) -> None:
        """Update an existing quest."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE quests 
                SET description = ?,
                    difficulty = ?,
                    theme = ?,
                    location = ?,
                    rewards = ?,
                    completed_by = ?,
                    completed_at = ?,
                    active = ?
                WHERE quest_id = ?
            ''', (
                quest.description,
                quest.difficulty,
                quest.theme,
                json.dumps(quest.location),
                json.dumps(quest.rewards),
                quest.completed_by,
                quest.completed_at.isoformat() if quest.completed_at else None,
                quest.active,
                quest.quest_id
            ))
            conn.commit()

    def delete_expired_quests(self) -> int:
        """Delete all expired quests and return the number of deleted quests."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM quests 
                WHERE expires_at IS NOT NULL 
                AND expires_at < ?
            ''', (datetime.now().isoformat(),))
            deleted_count = cursor.rowcount
            conn.commit()
            
        logger.info(f"Deleted {deleted_count} expired quests")
        return deleted_count

    def _row_to_quest(self, row: tuple) -> Quest:
        """Convert a database row to a Quest object."""
        return Quest(
            quest_id=row[0],
            title=row[1],
            description=row[2],
            difficulty=row[3],
            theme=row[4],
            location=tuple(json.loads(row[5])),
            rewards=json.loads(row[6]) if row[6] else [],
            completed_by=row[7],
            completed_at=datetime.fromisoformat(row[8]) if row[8] else None,
            created_at=datetime.fromisoformat(row[9]),
            expires_at=datetime.fromisoformat(row[10]) if row[10] else None,
            active=bool(row[11])
        )

    def get_quest_count_by_theme(self, theme: str) -> int:
        """Get the count of active quests for a specific theme."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM quests 
                WHERE theme = ? AND active = TRUE
            ''', (theme,))
            return cursor.fetchone()[0]

    def get_completed_quests_count(self, player_id: str) -> Dict[str, int]:
        """Get the count of completed quests by theme for a player."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT theme, COUNT(*) 
                FROM quests 
                WHERE completed_by = ? 
                GROUP BY theme
            ''', (player_id,))
            return dict(cursor.fetchall())