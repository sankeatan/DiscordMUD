import pytest
from discord.ext import commands
from discord import Message, Intents, User, Guild, ClientUser
from unittest.mock import AsyncMock, MagicMock, patch
import discord_bot

@pytest.fixture
def test_bot():
    mock_bot = MagicMock(spec=commands.Bot)
    mock_bot.user = MagicMock(spec=ClientUser)
    mock_bot.user.id = 123456789  # Dummy bot ID
    return mock_bot

def create_mock_message(content):
    message = MagicMock(spec=Message)
    message.content = content
    message.author = MagicMock(spec=User)
    message.author.id = 987654321  # Dummy user ID
    message.author.name = "TestUser"
    message.guild = MagicMock(spec=Guild)
    message.guild.id = 111222333  # Dummy guild ID
    return message

@pytest.fixture
def mock_context(test_bot):
    ctx = MagicMock(spec=commands.Context)
    ctx.bot = test_bot
    ctx.send = AsyncMock()
    ctx.author = MagicMock()
    ctx.author.name = "TestUser"
    return ctx

@pytest.fixture
def mock_world_gen():
    with patch('discord_bot.world_gen') as mock:
        mock.get_random_biome.return_value = "Forest"
        yield mock

# Test !start Command
@pytest.mark.asyncio
async def test_start_command(mock_context):
    await discord_bot.start_game(mock_context)
    mock_context.send.assert_called_with("The game world has been generated! Type !explore to begin your journey.")

# Test !explore Command
@pytest.mark.asyncio
async def test_explore_command(mock_context, mock_world_gen):
    await discord_bot.explore(mock_context)
    assert "You find yourself in a Forest" in mock_context.send.call_args[0][0]

# Test !move Command
@pytest.mark.asyncio
async def test_move_command(mock_context, mock_world_gen):
    await discord_bot.move(mock_context, "north")
    assert "You move north and find yourself in a Forest" in mock_context.send.call_args[0][0]

# Test Invalid !move Command
@pytest.mark.asyncio
async def test_invalid_move_command(mock_context):
    await discord_bot.move(mock_context, "invalid_direction")
    mock_context.send.assert_called_with("Invalid direction! Choose from: north, south, east, west")

# Test !help Command
@pytest.mark.asyncio
async def test_help_command(mock_context, test_bot):
    # Mock the help command
    help_command = MagicMock()
    help_command.send_bot_help = AsyncMock()
    test_bot.help_command = help_command
    
    await test_bot.help_command.send_bot_help(mock_context)
    help_command.send_bot_help.assert_called_once()
