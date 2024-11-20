class GameError(Exception):
    """Base exception for game-related errors."""
    pass

class CharacterError(GameError):
    """Raised when there's an error with character operations."""
    pass

class CombatError(GameError):
    """Raised when there's an error in combat operations."""
    pass

class WorldError(GameError):
    """Raised when there's an error with world operations."""
    pass

class InvalidActionError(GameError):
    """Raised when a player attempts an invalid action."""
    pass

class ResourceError(GameError):
    """Raised when there's an error with game resources."""
    pass

class DatabaseError(GameError):
    """Raised when there's a database-related error."""
    pass

class AIServiceError(GameError):
    """Raised when there's an error with AI services."""
    pass

class ConfigurationError(GameError):
    """Raised when there's a configuration error."""
    pass