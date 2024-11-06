# test_ai_npc.py

import pytest
from unittest.mock import patch, MagicMock
from ai_npc import AINPC

@pytest.fixture
def npc():
    """Create an NPC with a friendly personality."""
    return AINPC(name="Blacksmith", personality="friendly")

@patch("openai.ChatCompletion.create")
def test_generate_dialogue(mock_openai, npc):
    """Test if AI dialogue is generated successfully."""
    mock_openai.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="Sure, I can help you with that!"))]
    )

    player_input = "Can you repair my sword?"
    response = npc.generate_dialogue(player_input)
    assert response == "Sure, I can help you with that!"
    mock_openai.assert_called_once()

def test_personality_impact(npc):
    """Test if the NPC personality impacts the dialogue prompt."""
    npc.personality = "hostile"
    prompt = npc.build_prompt("What do you want?")
    
    assert "hostile personality" in prompt[0]["content"]

def test_conversation_history(npc):
    """Test if conversation history affects the dialogue."""
    # Simulate a prior conversation
    npc.conversation_history = [
        {"player": "Do you have any weapons?", "npc": "Only the best ones!"},
    ]

    player_input = "Can I buy a sword?"
    prompt = npc.build_prompt(player_input)

    assert "Do you have any weapons?" in prompt[2]["content"]

@patch("openai.ChatCompletion.create", side_effect=Exception("API Error"))
def test_error_handling(mock_openai, npc):
    """Test how the NPC handles API errors."""
    player_input = "Hello!"
    response = npc.generate_dialogue(player_input)
    assert response == "I'm sorry, I'm having trouble understanding right now."
