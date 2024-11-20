import os
import discord
from discord.ext import commands
from core.config import Config
from services.discord.command_handler import GameCommandHandler
from services.game.character_service import CharacterService
from services.game.combat_service import CombatService
from services.game.world_service import WorldService
from services.game.quest_service import QuestService
from services.ai.openai_service import OpenAIService
from services.ai.narrative_service import NarrativeService
from data.database.db_manager import DatabaseManager
from data.database.repositories.character_repository import CharacterRepository
from data.database.repositories.quest_repository import QuestRepository

def setup_bot(config: Config):
    
    # Initialize bot
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix=config.command_prefix, intents=intents)

    # Initialize database and repositories
    db_manager = DatabaseManager(config.database_path)
    character_repository = CharacterRepository(db_manager)
    quest_repository = QuestRepository(db_manager)
    
    # Initialize AI services
    openai_service = OpenAIService(config)
    narrative_service = NarrativeService(openai_service)
    
    # Initialize game services
    character_service = CharacterService(character_repository)
    combat_service = CombatService(narrative_service)
    world_service = WorldService(quest_repository, narrative_service)
    quest_service = QuestService(quest_repository, narrative_service)

    # Initialize command handler
    command_handler = GameCommandHandler(
        bot,
        character_service,
        combat_service,
        world_service,
        quest_service
    )
    command_handler.register_commands()

    return bot

def main():
    config = Config.load_from_yaml()
    
    bot = setup_bot(config)
    bot.run(config.discord_token)

if __name__ == "__main__":
    main()