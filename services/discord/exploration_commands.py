from discord.ext import commands
from .base_handler import BaseCommandHandler
from ...services.game.world_service import WorldService
import logging

logger = logging.getLogger(__name__)

class ExplorationCommands(BaseCommandHandler):
    def __init__(self, bot: commands.Bot, world_service: WorldService):
        super().__init__(bot)
        self.world_service = world_service

    async def explore(self, ctx: commands.Context):
        """Explore the current location."""
        character = await self.check_character_exists(ctx)
        if not character:
            return

        description = self.world_service.get_location_description(character.location)
        await ctx.send(description)

    async def move(self, ctx: commands.Context, direction: str):
        """Move in a direction."""
        character = await self.check_character_exists(ctx)
        if not character:
            return

        try:
            result = self.world_service.move_character(character, direction.lower())
            await ctx.send(result)
        except ValueError as e:
            await ctx.send(str(e))