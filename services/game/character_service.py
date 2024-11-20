from typing import Optional
import logging
from ...data.models.character import Character
from ...data.database.repositories.character_repository import CharacterRepository

logger = logging.getLogger("character_service")

class CharacterService:
    def __init__(self, character_repository: CharacterRepository):
        self.repository = character_repository

    def create_character(self, discord_id: str, name: str) -> Character:
        """Create a new character."""
        if self.repository.load(discord_id):
            raise ValueError("Character already exists for this user")
        
        character = Character(name=name)
        self.repository.save(discord_id, character)
        return character

    def get_character(self, discord_id: str) -> Optional[Character]:
        """Retrieve a character."""
        return self.repository.load(discord_id)

    def update_character(self, discord_id: str, character: Character) -> None:
        """Update an existing character."""
        self.repository.save(discord_id, character)

    def allocate_stats(self, discord_id: str, hp: int = 0, attack: int = 0, 
                      defense: int = 0, magic: int = 0) -> Optional[Character]:
        """Allocate stats to a character."""
        character = self.get_character(discord_id)
        if not character:
            return None

        character.allocate_stat_points(hp, attack, defense, magic)
        self.update_character(discord_id, character)
        return character