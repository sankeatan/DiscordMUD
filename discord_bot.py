import discord
from discord.ext import commands
import os
from ai_game_master import AIGameMaster
from world_generation import WorldGenerator
from logger import setup_logger
from dotenv import load_dotenv
load_dotenv()

# Initialize Logger
logger = setup_logger('discord_bot')

# Load Discord Token from Environment Variables
TOKEN = os.getenv('DISCORD_TOKEN')
if TOKEN is None:
    logger.error("DISCORD_TOKEN environment variable is not set")
    raise ValueError("DISCORD_TOKEN environment variable is not set")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

world_gen = WorldGenerator(world_width=20, world_height=20, region_size=5, seed=42)
world_gen.generate_regions()
world_gen.save_world_to_db()

ai_gm = AIGameMaster()

# Store player positions and stats
player_data = {}

# Command to Start or Reset the Game
@bot.command(name="start")
async def start_game(ctx):
    """Start a new game or reset the current game."""
    world_gen.generate_regions()
    world_gen.save_world_to_db()
    player_data.clear()
    await ctx.send("The game world has been generated! Type !explore to begin your journey.")
    logger.info(f"Game started by {ctx.author.name}")

# Command to Explore the World
@bot.command(name="explore")
async def explore(ctx):
    """Explore the current region and receive quests."""
    player = ctx.author.name
    biome = world_gen.get_random_biome()
    quest = ai_gm.generate_quest(player, biome)
    await ctx.send(f"You find yourself in a {biome}. {quest}")
    logger.info(f"{player} explored the {biome}")

# Command to Move Player in a Direction
@bot.command(name="move")
async def move(ctx, direction: str):
    """Move the player in a specific direction."""
    valid_directions = ["north", "south", "east", "west"]
    if direction.lower() not in valid_directions:
        await ctx.send(f"Invalid direction! Choose from: {', '.join(valid_directions)}")
        logger.warning(f"{ctx.author.name} attempted an invalid move: {direction}")
        return

    player = ctx.author.name
    # Placeholder logic for moving and triggering events
    biome = world_gen.get_random_biome()
    quest = ai_gm.react_to_player_action("move", player, biome)
    await ctx.send(f"You move {direction} and find yourself in a {biome}. {quest}")
    logger.info(f"{player} moved {direction}")

# Command to Check Player Stats
@bot.command(name="stats")
async def player_stats(ctx):
    """Display the player's stats and inventory."""
    player = ctx.author.name
    stats = player_data.get(player, {"level": 1, "inventory": []})
    await ctx.send(f"Stats for {player}: Level {stats['level']}, Inventory: {stats['inventory']}")
    logger.info(f"Displayed stats for {player}")

# Custom Error Handler for Commands
@bot.event
async def on_command_error(ctx, error):
    """Handle command errors gracefully."""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Unknown command! Type !help for a list of commands.")
        logger.warning(f"Command not found: {ctx.message.content}")
    else:
        await ctx.send("An error occurred while processing the command.")
        logger.error(f"Error in command {ctx.command}: {error}")

# Help Command to List Available Commands
@bot.command(name="help")
async def help_command(ctx):
    """Display a list of available commands."""
    help_text = """
    **Available Commands:**
    !start - Start a new game or reset the current game.
    !explore - Explore the current region and receive quests.
    !move <direction> - Move in a direction (north, south, east, west).
    !stats - Check your current stats and inventory.
    """
    await ctx.send(help_text)
    logger.info(f"{ctx.author.name} requested help")

# Run the Bot
if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except Exception as e:
        logger.critical(f"Failed to run bot: {e}")
