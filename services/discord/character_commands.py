from discord.ext import commands
from .base_handler import BaseCommandHandler
from ...services.game.character_service import CharacterService
import logging

logger = logging.getLogger("character_commands")

class CharacterCommands(BaseCommandHandler):
    def __init__(self, bot: commands.Bot, character_service: CharacterService):
        super().__init__(bot)
        self.character_service = character_service

    async def create(self, ctx: commands.Context, *, character_name: str):
        """Create a new character."""
        try:
            character = self.character_service.create_character(
                str(ctx.author.id), 
                character_name
            )
            await ctx.send(f"Character '{character.name}' created! Use `!allocate` to customize your stats.")
            logger.info(f"Player {ctx.author.name} created character '{character_name}'")
        except ValueError as e:
            await ctx.send(str(e))

    async def view(self, ctx: commands.Context):
        """View character stats."""
        character = await self.check_character_exists(ctx)
        if not character:
            return

        stats = "\n".join([f"{stat}: {value}" for stat, value in character.stats.items()])
        await ctx.send(
            f"**{character.name}'s Stats:**\n"
            f"Class: {character.player_class}\n"
            f"Level: {character.level}\n"
            f"{stats}\n"
            f"Location: {character.location}"
        )

    async def allocate(self, ctx: commands.Context, hp: int = 0, attack: int = 0, 
                      defense: int = 0, magic: int = 0):
        """Allocate stat points."""
        try:
            character = self.character_service.allocate_stats(
                str(ctx.author.id),
                hp, attack, defense, magic
            )
            if character:
                await ctx.send(f"Stats updated for '{character.name}'! Use `!view` to see your character stats.")
            else:
                await ctx.send("You don't have a character yet! Use `!create` to start.")
        except ValueError as e:
            await ctx.send(str(e))