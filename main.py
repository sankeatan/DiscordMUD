import os
import discord
from discord.ext import commands
from services.discord.command_handler import GameCommandHandler
from services.game.character_service import CharacterService
from services.game.combat_service import CombatService
from services.game.world_service import WorldService
from data.database.db_manager import DatabaseManager
from data.database.repositories.character_repository import CharacterRepository


def setup_bot():
    # Initialize bot
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    # Initialize services
    db_manager = DatabaseManager("game_data.db")
    character_repository = CharacterRepository(db_manager)
    
    character_service = CharacterService(character_repository)
    combat_service = CombatService()
    world_service = WorldService()

    # Initialize command handler
    command_handler = GameCommandHandler(
        bot,
        character_service,
        combat_service,
        world_service
    )
    command_handler.register_commands()

    return bot

def main():
    bot = setup_bot()
    bot.run(os.getenv('DISCORD_TOKEN'))

if __name__ == "__main__":
    main()