from typing import Dict, Optional
from ..data.models.character import Character
from ..data.models.combat import CombatState
import logging

logger = logging.getLogger(__name__)

class GameState:
    """
    Manages global game state and active sessions.
    Implemented as a singleton to ensure consistent state across the application.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameState, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the game state."""
        self.active_players: Dict[str, Character] = {}
        self.combat_sessions: Dict[str, CombatState] = {}  # guild_id -> CombatState
        self.player_sessions: Dict[str, str] = {}  # player_id -> session_id
        self.initialized = False

    def register_player(self, discord_id: str, character: Character) -> None:
        """Register an active player."""
        self.active_players[discord_id] = character
        logger.info(f"Player {discord_id} registered with character {character.name}")

    def unregister_player(self, discord_id: str) -> None:
        """Remove a player from active sessions."""
        if discord_id in self.active_players:
            del self.active_players[discord_id]
            logger.info(f"Player {discord_id} unregistered")

    def get_active_character(self, discord_id: str) -> Optional[Character]:
        """Get the active character for a player."""
        return self.active_players.get(discord_id)

    def start_combat_session(self, guild_id: str, combat_state: CombatState) -> None:
        """Start a new combat session for a guild."""
        self.combat_sessions[guild_id] = combat_state
        logger.info(f"Combat session started in guild {guild_id}")

    def end_combat_session(self, guild_id: str) -> None:
        """End a combat session for a guild."""
        if guild_id in self.combat_sessions:
            del self.combat_sessions[guild_id]
            logger.info(f"Combat session ended in guild {guild_id}")

    def get_combat_session(self, guild_id: str) -> Optional[CombatState]:
        """Get the active combat session for a guild."""
        return self.combat_sessions.get(guild_id)

    def is_player_in_combat(self, discord_id: str) -> bool:
        """Check if a player is in an active combat session."""
        return any(
            discord_id in [p.discord_id for p in session.players]
            for session in self.combat_sessions.values()
        )