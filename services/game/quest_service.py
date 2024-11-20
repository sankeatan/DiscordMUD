from typing import List, Dict, Optional
from ...data.models.quest import Quest
from ...data.database.repositories.quest_repository import QuestRepository
from ..ai.narrative_service import NarrativeService
import logging

logger = logging.getLogger(__name__)

class QuestService:
    """Manages quest generation, tracking, and completion."""
    
    def __init__(self, 
                 quest_repository: QuestRepository,
                 narrative_service: NarrativeService):
        self.repository = quest_repository
        self.narrative_service = narrative_service

    async def generate_quests(self, 
                            location: tuple,
                            count: int = 3) -> List[Quest]:
        """Generate new quests for a location."""
        quests = []
        themes = ["exploration", "combat", "collection", "rescue", "mystery"]
        
        for i in range(count):
            difficulty = (abs(location[0]) + abs(location[1])) // 2 + 1
            theme = themes[i % len(themes)]
            
            description = await self.narrative_service.generate_quest_description(
                location,
                difficulty,
                theme
            )
            
            quest = Quest(
                location=location,
                description=description,
                difficulty=difficulty,
                theme=theme
            )
            quests.append(quest)
            
        return quests

    def get_available_quests(self, location: tuple) -> List[Quest]:
        """Get all available quests at a location."""
        return self.repository.get_quests_at_location(location)

    def complete_quest(self, quest_id: int, character_id: str) -> bool:
        """Mark a quest as completed and grant rewards."""
        quest = self.repository.get_quest(quest_id)
        if not quest:
            return False
            
        # Add completion logic here
        quest.complete(character_id)
        self.repository.update_quest(quest)
        return True