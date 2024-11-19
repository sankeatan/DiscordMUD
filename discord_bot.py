import discord
from discord.ext import commands
import os
from ai_game_master import AIGameMaster
from world_generation import WorldGenerator
from combat_manager import CombatManager
from character import Character
from ai_npc import AINPC
from db_helper import initialize_database, save_character, load_character
from logger import setup_logger
from dotenv import load_dotenv
load_dotenv()

# Initialize the database at startup
initialize_database()

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

combat_manager = CombatManager()

player_characters = {}

@bot.command(name="questboard")
async def quest_board(ctx):
    """View the quest board in town."""
    player_discord_id = str(ctx.author.id)
    char_data = load_character(player_discord_id)
    if not char_data:
        await ctx.send("You don't have a character yet! Use `!create` to start.")
        return

    location = char_data["location"]
    if location != (0, 0):
        await ctx.send("You must be in the Town to view the quest board.")
        return

    quests = ai_gm.generate_quest_board((0, 0), world_gen)
    await ctx.send(f"**Quest Board:**\n" + "\n".join(f"- {quest}" for quest in quests))

@bot.command(name="create")
async def create_character(ctx, *, character_name: str):
    """Create a character and save it to the database."""
    player_discord_id = str(ctx.author.id)
    if load_character(player_discord_id):
        logger.warning(f"Player {ctx.author.name} tried to create a character but already has one.")
        await ctx.send("You already have a character! Use `!view` to check your stats.")
        return

    # Create and save the character
    starting_location = (0,0)
    character = Character(name=character_name, starting_location=starting_location)
    save_character(player_discord_id, character)
    player_characters[player_discord_id] = character
    logger.info(f"Player {ctx.author.name} created a character named '{character_name}'.")
    await ctx.send(f"Character '{character_name}' created! Use `!allocate` to customize your stats.")

@bot.command(name="allocate")
async def allocate_stats(ctx, hp: int = 0, attack: int = 0, defense: int = 0, magic: int = 0):
    """Allocate stat points to a character."""
    player_discord_id = str(ctx.author.id)
    char_data = load_character(player_discord_id)
    if not char_data:
        logger.warning(f"Player {ctx.author.name} tried to allocate stats but no character exists.")
        await ctx.send("You don't have a character yet! Use `!create` to start.")
        return

    # Update stats
    logger.info(f"Player {ctx.author.name} is allocating stats: HP={hp}, Attack={attack}, Defense={defense}, Magic={magic}.")
    char_data["stats"]["HP"] += hp
    char_data["stats"]["Attack"] += attack
    char_data["stats"]["Defense"] += defense
    char_data["stats"]["Magic"] += magic

    # Save updates
    updated_character = Character(
        name=char_data["name"],
        player_class=char_data["class"]
    )
    updated_character.stats = char_data["stats"]
    save_character(player_discord_id, updated_character)
    logger.info(f"Player {ctx.author.name} updated stats for '{char_data['name']}'.")
    await ctx.send(f"Stats updated for '{char_data['name']}'! Use `!view` to see your character stats.")

@bot.command(name="view")
async def view_character(ctx):
    """View character stats."""
    player_discord_id = str(ctx.author.id)
    char_data = load_character(player_discord_id)
    if not char_data:
        logger.warning(f"Player {ctx.author.name} tried to view a character but none exists.")
        await ctx.send("You don't have a character yet! Use `!create` to start.")
        return
    
    location = char_data["location"]
    logger.info(f"Player {ctx.author.name} viewed their character '{char_data['name']}'.")
    stats = "\n".join([f"{stat}: {value}" for stat, value in char_data["stats"].items()])
    await ctx.send(
        f"**{char_data['name']}'s Stats:**\nClass: {char_data['class']}\nLevel: {char_data['level']}\n{stats}\nLocation: {location}\n{stats}"
    )

@bot.command(name="combat")
async def start_combat(ctx):
    """
    Start a new combat session.
    """
    player_discord_id = str(ctx.author.id)
    
    if player_discord_id not in player_characters:
        char_data = load_character(player_discord_id)
        if not char_data:
            logger.warning(f"Player {ctx.author.name} tried to start combat without a character.")
            await ctx.send("You need to create a character first! Use `!create` to start.")
            return
        
        character = Character(
            name=char_data["name"],
            player_class=char_data["class"]
        )
        character.stats = char_data["stats"]
        character.level = char_data["level"]
        character.inventory = char_data["inventory"]
        player_characters[player_discord_id] = character

    character = player_characters[player_discord_id]
    logger.info(f"Player {ctx.author.name} ({character.name}) started a combat session.")
    await ctx.send(combat_manager.start_combat([character]))

@bot.command(name="action")
async def take_action(ctx, *, action: str):
    """
    Submit an action for the current round. Supports standard or creative moves.
    Creative moves should start with 'creative:' followed by the action text.
    """
    player_discord_id = str(ctx.author.id)
    
    if player_discord_id not in player_characters:
        logger.warning(f"Player {ctx.author.name} tried to take an action without a character.")
        await ctx.send("You need to create a character first! Use `!create` to start.")
        return
    
    if not combat_manager.current_combat:
        logger.warning(f"Player {ctx.author.name} tried to take an action without an active combat session.")
        await ctx.send("No active combat session! Use `!combat` to start one.")
        return

    character = player_characters[player_discord_id]
    combat_manager.add_action(character, action)
    logger.info(f"Player {ctx.author.name} ({character.name}) submitted action: {action}")
    await ctx.send(f"{character.name}, your action '{action}' has been recorded.")

@bot.command(name="resolve")
async def resolve_combat(ctx):
    """Resolve the current combat round with expanded AI narration."""
    if not combat_manager.current_combat:
        await ctx.send("No active combat to resolve!")
        return

    # Process actions and resolve round
    gm = AIGameMaster()
    actions = combat_manager.current_combat.actions
    enemies = combat_manager.current_combat.enemies
    outcomes = gm.process_actions(actions, enemies)

    # Generate combat narrative
    npc = AINPC(name="Narrator", personality="neutral")
    narrative = npc.generate_combat_narrative(actions, outcomes)

    # Update combat state
    combat_manager.current_combat.round += 1
    combat_manager.current_combat.actions.clear()

    # Send narrative to the channel
    await ctx.send(f"**Round {combat_manager.current_combat.round} Results:**\n{narrative}")

    # Check for combat end
    if combat_manager.current_combat.is_combat_over():
        await ctx.send("Combat has ended!")
        combat_manager.current_combat = None

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
    """Explore the current location."""
    player_discord_id = str(ctx.author.id)
    char_data = load_character(player_discord_id)
    if not char_data:
        await ctx.send("You don't have a character yet! Use `!create` to start.")
        return
    
    location = char_data["location"]
    if location == (0, 0):  # Town location
        town = world_gen.regions[0][0]["town"]
        await ctx.send(f"You are in {town['name']}. {town['description']}.")
    else:
        region = world_gen.get_region(*location)
        biome = region["biome"]
        encounter = ai_gm.generate_encounter(biome)
        await ctx.send(f"You are in the {biome}. {encounter}")

# Command to Move Player in a Direction
@bot.command(name="move")
async def move(ctx, direction: str):
    """Move the character in a specific direction."""
    player_discord_id = str(ctx.author.id)
    char_data = load_character(player_discord_id)
    if not char_data:
        await ctx.send("You don't have a character yet! Use `!create` to start.")
        return
    valid_directions = ["north", "south", "east", "west"]
    if direction.lower() not in valid_directions:
        await ctx.send(f"Invalid direction! Choose from: {', '.join(valid_directions)}")
        logger.warning(f"{ctx.author.name} attempted an invalid move: {direction}")
        return
    
     # Calculate new location
    location = char_data["location"]
    if direction == "north":
        location[1] -= 1
    elif direction == "south":
        location[1] += 1
    elif direction == "east":
        location[0] += 1
    elif direction == "west":
        location[0] -= 1

    # Wrap around the map if necessary
    try:
        region = world_gen.get_region(location[0], location[1])
    except ValueError:
        await ctx.send("You can't move further in that direction.")
        return

    # Update location and save
    char_data["location"] = location
    updated_character = Character(
        name=char_data["name"],
        player_class=char_data["class"],
        starting_location=location
    )
    updated_character.stats = char_data["stats"]
    updated_character.level = char_data["level"]
    updated_character.inventory = char_data["inventory"]
    save_character(player_discord_id, updated_character)

    # Narrate the new location
    biome = region["biome"]
    await ctx.send(f"You move {direction} and arrive in a {biome}. {region.get('description', '')}")

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
        logger.warning(f"Unknown command attempted: {ctx.message.content}")
        await ctx.send("Unknown command! Type `!help` for a list of commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        logger.warning(f"Missing argument in command: {ctx.message.content}")
        await ctx.send("Missing required argument! Check the command format with `!help`.")
    else:
        logger.error(f"Unhandled error: {error}")
        await ctx.send("An error occurred while processing your command. Please try again.")

# Help Command to List Available Commands
@bot.command(name="help")
async def help_command(ctx):
    """
    Display a list of available commands with updated descriptions.
    """
    help_text = """
    **Available Commands:**

    **Character Management**
    - `!create <character_name>`: Create a new character with the specified name.
    - `!view`: View the stats and details of your character.
    - `!allocate <hp> <attack> <defense> <magic>`: Allocate stat points to your character.
    
    **Exploration**
    - `!start`: Start or reset the game world.
    - `!explore`: Explore the current region and receive quests.
    - `!move <direction>`: Move in a specified direction (north, south, east, or west).
    
    **Combat**
    - `!combat`: Start a new combat session if one is not active.
    - `!action <action>`: Submit your action for the current combat round (e.g., attack, defend, cast spell, or use a creative move).
      - Use `creative: <description>` for custom actions.
    - `!resolve`: Resolve the current combat round and display the results.
    
    **NPC Interaction**
    - `!talk <npc_name> <message>`: Talk to an NPC using AI-generated dialogue.
    
    **General**
    - `!help`: Display this help message.

    **Note**: For any issues or suggestions, please contact the admin.
    """
    await ctx.send(help_text)
    logger.info(f"{ctx.author.name} requested help")

# Run the Bot
if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except Exception as e:
        logger.critical(f"Failed to run bot: {e}")
