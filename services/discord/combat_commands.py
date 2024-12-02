from discord.ext import commands
from .base_handler import BaseCommandHandler
from services.game.combat_service import CombatService
from services.game.character_service import CharacterService
import logging

logger = logging.getLogger("combat_commands")

class CombatCommands(BaseCommandHandler):
    def __init__(self, bot: commands.Bot, combat_service: CombatService, character_service: CharacterService):
        super().__init__(bot)
        self.combat_service = combat_service
        self.character_service = character_service

    async def start_combat(self, ctx: commands.Context):
        """Start a combat session."""
        character = await self.check_character_exists(ctx)
        if not character:
            return

        result = self.combat_service.start_combat([character])
        await ctx.send(result)
        logger.info(f"{character.name} started a combat session.")

    async def action(self, ctx: commands.Context, *, action: str):
        """Submit a combat action."""
        character = await self.check_character_exists(ctx)
        if not character:
            return

        try:
            result = self.combat_service.add_action(character, action)
            await ctx.send(f"{character.name}, your action '{action}' has been recorded.")
            logger.info(f"{character.name} performed action: {action}")
        except ValueError as e:
            await ctx.send(str(e))
            logger.error(f"Error recording action for {character.name}: {e}")

    async def resolve(self, ctx: commands.Context):
        """Resolve the current combat round."""
        try:
            narrative = await self.combat_service.resolve_round()
            await ctx.send(f"**Combat Round Results:**\n{narrative}")
            logger.info("Combat round resolved successfully.")
        except ValueError as e:
            await ctx.send(str(e))
            logger.error(f"Error resolving combat round: {e}")