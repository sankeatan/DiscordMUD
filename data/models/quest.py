from dataclasses import dataclass
from typing import Optional, List, Tuple
from datetime import datetime

@dataclass
class Quest:
    title: str
    description: str
    difficulty: int
    theme: str
    location: Tuple[int, int]
    rewards: List[str] = None
    quest_id: Optional[int] = None
    completed_by: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    active: bool = True

    def __post_init__(self):
        if self.rewards is None:
            self.rewards = []
        if self.created_at is None:
            self.created_at = datetime.now()

    def complete(self, character_id: str) -> None:
        """Mark the quest as completed by a character."""
        self.completed_by = character_id
        self.completed_at = datetime.now()

    def is_expired(self) -> bool:
        """Check if the quest has expired."""
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at

    def is_completed(self) -> bool:
        """Check if the quest has been completed."""
        return self.completed_by is not None

    def is_available(self) -> bool:
        """Check if the quest is available to take."""
        return (
            self.active and
            not self.is_completed() and
            not self.is_expired()
        )