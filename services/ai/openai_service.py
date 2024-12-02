from typing import Dict, Optional
import openai
import logging
from core.config import Config

logger = logging.getLogger("openai_service")

class OpenAIService:
    """Base service for OpenAI API interactions."""
    
    def __init__(self, config: Config):
        self.api_key = config.openai_api_key
        openai.api_key = self.api_key

    async def generate_response(self, 
                              prompt: str, 
                              system_prompt: Optional[str] = None,
                              temperature: float = 0.7,
                              max_tokens: int = 150) -> str:
        """Generate a response using OpenAI's API."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = openai.beta.chat.completions.parse(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            logger.debug(f"OpenAI response: {response}")
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}")
            raise