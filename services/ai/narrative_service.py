from typing import List, Dict
from .openai_service import OpenAIService
import logging

logger = logging.getLogger(__name__)

class NarrativeService:
    """Handles narrative generation for various game aspects."""
    
    def __init__(self, openai_service: OpenAIService):
        self.ai = openai_service

    async def generate_combat_narrative(self, 
                                      actions: List[Dict], 
                                      outcomes: List[str]) -> str:
        """Generate a narrative description of combat events."""
        prompt = (
            "Create an engaging narrative description of the following combat:\n"
            f"Actions taken: {actions}\n"
            f"Outcomes: {outcomes}\n"
            "Make it concise but dramatic."
        )
        return await self.ai.generate_response(prompt)

    async def generate_location_description(self, 
                                          biome: str, 
                                          features: List[str]) -> str:
        """Generate a description of a location."""
        prompt = (
            f"Describe a location in a {biome} with the following features:\n"
            f"{', '.join(features)}\n"
            "Keep it concise but atmospheric."
        )
        return await self.ai.generate_response(prompt)

    async def generate_quest_description(self, 
                                       location: tuple, 
                                       difficulty: int,
                                       theme: str) -> str:
        """Generate a quest description."""
        prompt = (
            f"Create a quest for a location at {location} with "
            f"difficulty level {difficulty} and theme: {theme}"
        )
        return await self.ai.generate_response(prompt)