from typing import Optional
from discord.ext import commands
from ...core.exceptions import GameError
import logging

logger = logging.getLogger("base_handler")

class BaseCommandHandler:
    """Base class for command handlers with common utilities."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def handle_error(self, ctx: commands.Context, error: Exception) -> None:
        """Handle command errors uniformly."""
        if isinstance(error, GameError):
            await ctx.send(str(error))
        else:
            logger.error(f"Error in command {ctx.command}: {error}", exc_info=True)
            await ctx.send("An unexpected error occurred. Please try again later.")

    async def check_character_exists(self, ctx: commands.Context) -> Optional[dict]:
        """Common check for character existence."""
        character = await self.character_service.get_character(str(ctx.author.id))
        if not character:
            await ctx.send("You don't have a character yet! Use `!create` to start.")
            return None
        return character