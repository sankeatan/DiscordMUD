from dataclasses import dataclass
import os
from typing import Optional
import yaml
import logging

logger = logging.getLogger(__name__)

@dataclass
class Config:
    """Configuration settings for the application."""
    discord_token: str
    openai_api_key: str
    database_path: str
    command_prefix: str = "!"
    debug_mode: bool = False
    max_players_per_combat: int = 4
    world_size: tuple = (20, 20)
    region_size: int = 5

    @classmethod
    def load_from_yaml(cls, path: str = "config.yaml") -> "Config":
        """Load configuration from a YAML file."""
        try:
            with open(path, 'r') as f:
                config_data = yaml.safe_load(f)
            return cls(**config_data)
        except Exception as e:
            logger.error(f"Error loading config from {path}: {e}")
            raise

    @classmethod
    def load_from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            discord_token=os.getenv("DISCORD_TOKEN"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            database_path=os.getenv("DATABASE_PATH", "game_data.db"),
            debug_mode=os.getenv("DEBUG_MODE", "false").lower() == "true",
            command_prefix=os.getenv("COMMAND_PREFIX", "!"),
            max_players_per_combat=int(os.getenv("MAX_PLAYERS_PER_COMBAT", "4")),
            world_size=(
                int(os.getenv("WORLD_WIDTH", "20")),
                int(os.getenv("WORLD_HEIGHT", "20"))
            ),
            region_size=int(os.getenv("REGION_SIZE", "5"))
        )