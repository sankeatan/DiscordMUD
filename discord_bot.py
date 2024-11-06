import discord
from discord.ext import commands
import os
from ai_game_master import AIGameMaster
from world_generation import WorldGenerator
from ai_npc import AINPC
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

# At the top of the file, after initializing player_data
DEFAULT_PLAYER_STATS = {
    "x": 0,
    "y": 0,
    "level": 1,
    "inventory": []
}

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
    try:
        biome = world_gen.get_random_biome()
        quest = ai_gm.generate_quest(player, biome)
        await ctx.send(f"You find yourself in a {biome}. {quest}")
        logger.info(f"{player} explored the {biome}")
    except Exception as e:
        await ctx.send("An error occurred while exploring. Please try again.")
        logger.error(f"Explore command failed: {str(e)}")

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
    
    # Get or initialize player position and stats
    if player not in player_data:
        player_data[player] = DEFAULT_PLAYER_STATS.copy()
    
    # Update player position based on direction
    if direction == "north":
        player_data[player]["y"] -= 1
    elif direction == "south":
        player_data[player]["y"] += 1
    elif direction == "east":
        player_data[player]["x"] += 1
    elif direction == "west":
        player_data[player]["x"] -= 1

    # Get the new region based on updated position
    new_x, new_y = player_data[player]["x"], player_data[player]["y"]
    try:
        new_region = world_gen.get_region(new_x, new_y)
        biome = new_region['biome']
        quest = ai_gm.react_to_player_action("move", player, biome)
        await ctx.send(f"You move {direction} and find yourself in a {biome}. {quest}")
        logger.info(f"{player} moved {direction} to ({new_x}, {new_y})")
    except Exception as e:
        await ctx.send("An error occurred while moving. Please try again.")
        logger.error(f"Move command failed: {str(e)}")

# Command to Check Player Stats
@bot.command(name="stats")
async def player_stats(ctx):
    """Display the player's stats and inventory."""
    player = ctx.author.name
    stats = player_data.get(player, {"level": 1, "inventory": []})
    await ctx.send(f"Stats for {player}: Level {stats['level']}, Inventory: {stats['inventory']}")
    logger.info(f"Displayed stats for {player}")

@bot.command(name="talk")
async def talk_to_npc(ctx, npc_name: str, *, player_message: str):
    """Allow players to talk to NPCs with AI-generated dialogue."""
    # Instantiate the NPC (you could load this from a database in a real game)
    npc = AINPC(name=npc_name, personality="friendly")

    # Generate NPC response using AI
    response = npc.generate_dialogue(player_message)

    # Send the response to the Discord channel
    await ctx.send(f"{npc_name}: {response}")
    logger.info(f"{ctx.author.name} talked to {npc_name} - {player_message}")

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
    !talk <npc_name> <message> - Initiate a conversation with an NPC.
    """
    await ctx.send(help_text)
    logger.info(f"{ctx.author.name} requested help")

# Run the Bot
if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except Exception as e:
        logger.critical(f"Failed to run bot: {e}")
