from discord.ext import commands
from .base_handler import BaseCommandHandler
from services.game.world_service import WorldService
from services.game.character_service import CharacterService
import logging

logger = logging.getLogger(__name__)

class ExplorationCommands(BaseCommandHandler):
    def __init__(self, bot: commands.Bot, world_service: WorldService, character_service: CharacterService):
        super().__init__(bot)
        self.world_service = world_service
        self.character_service = character_service

    async def explore(self, ctx: commands.Context):
        """Explore the current location."""
        character = await self.check_character_exists(ctx)
        if not character:
            return

        description = self.world_service.get_location_description(character.location)
        await ctx.send(description)
        logger.info(f"{character.name} explored the location: {description}")

    async def move(self, ctx: commands.Context, direction: str):
        """Move in a direction."""
        character = await self.check_character_exists(ctx)
        if not character:
            return

        try:
            current_location = character.location
            new_location, description = await self.world_service.move_character(current_location, direction.lower())
            
            # Update the character's location if necessary
            character.location = new_location
            
            await ctx.send(description)  # Send the description of the new location
            logger.info(f"{character.name} moved {direction} to {new_location}: {description}")
        except ValueError as e:
            await ctx.send(str(e))
            logger.error(f"Error moving character {character.name}: {e}")