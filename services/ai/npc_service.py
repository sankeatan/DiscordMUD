from typing import Optional
from .openai_service import OpenAIService
import logging

logger = logging.getLogger(__name__)

class NPCService:
    """Handles NPC interactions and dialogue."""
    
    def __init__(self, openai_service: OpenAIService):
        self.ai = openai_service

    async def generate_dialogue(self, 
                              npc_name: str, 
                              personality: str,
                              player_message: str,
                              context: Optional[str] = None) -> str:
        """Generate NPC dialogue response."""
        system_prompt = (
            f"You are {npc_name}, a character with a {personality} personality. "
            "Respond in character, keeping responses concise and natural."
        )
        
        prompt = player_message
        if context:
            prompt = f"Context: {context}\nPlayer says: {player_message}"

        return await self.ai.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.8
        )

    async def generate_merchant_interaction(self, 
                                          inventory: list,
                                          player_request: str) -> str:
        """Generate merchant-specific dialogue and offers."""
        prompt = (
            f"As a merchant with the following inventory: {inventory}\n"
            f"Respond to the player's request: {player_request}"
        )
        return await self.ai.generate_response(prompt)