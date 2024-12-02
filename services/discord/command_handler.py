from discord.ext import commands
from .character_commands import CharacterCommands
from .combat_commands import CombatCommands
from .exploration_commands import ExplorationCommands
import logging

logger = logging.getLogger(__name__)

class GameCommandHandler:
    """Main command handler that coordinates all game commands."""
    
    def __init__(self, bot: commands.Bot, 
                 character_service, 
                 combat_service,
                 world_service,):
        self.bot = bot
        self.character_commands = CharacterCommands(bot, character_service)
        self.combat_commands = CombatCommands(bot, combat_service, character_service)
        self.exploration_commands = ExplorationCommands(bot, world_service, character_service)

    def register_commands(self):
        """Register all commands with the bot."""
        
        # Character Commands
        @self.bot.command(name="create")
        async def create(ctx, *, character_name: str):
            await self.character_commands.create(ctx, character_name=character_name)

        @self.bot.command(name="view")
        async def view(ctx):
            await self.character_commands.view(ctx)

        @self.bot.command(name="allocate")
        async def allocate(ctx, hp: int = 0, attack: int = 0, defense: int = 0, magic: int = 0):
            await self.character_commands.allocate(ctx, hp, attack, defense, magic)

        # Combat Commands
        @self.bot.command(name="combat")
        async def combat(ctx):
            await self.combat_commands.start_combat(ctx)

        @self.bot.command(name="action")
        async def action(ctx, *, action: str):
            await self.combat_commands.action(ctx, action=action)

        @self.bot.command(name="resolve")
        async def resolve(ctx):
            await self.combat_commands.resolve(ctx)

        # Exploration Commands
        @self.bot.command(name="explore")
        async def explore(ctx):
            await self.exploration_commands.explore(ctx)

        @self.bot.command(name="move")
        async def move(ctx, direction: str):
            await self.exploration_commands.move(ctx, direction)

        # Error Handler
        @self.bot.event
        async def on_command_error(ctx, error):
            if isinstance(error, commands.CommandNotFound):
                await ctx.send("Unknown command! Type `!help` for a list of commands.")
            elif isinstance(error, commands.MissingRequiredArgument):
                await ctx.send("Missing required argument! Check the command format with `!help`.")
            else:
                logger.error(f"Unhandled error: {error}")
                await ctx.send("An error occurred while processing your command.")