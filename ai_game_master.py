from logger import setup_logger
import logging

logger = setup_logger('ai_game_master')

class AIGameMaster:
    def __init__(self):
        logger.info("Initializing AIGameMaster")
        # Quest templates or response handling could be loaded here.
        self.quests = []

    def generate_quest(self, player, biome):
        logger.info(f"Generating quest for player {player} in biome {biome}")
        # Generate a simple quest based on the biome the player is in
        if biome.lower() == 'forest':
            quest = f"{player}, protect the forest from an invasive species!"
        elif biome.lower() == 'mountain':
            quest = f"{player}, find the hidden treasure in the mountains!"
        elif biome.lower() == 'desert':
            quest = f"{player}, survive the desert storm!"
        else:
            quest = f"{player}, explore the mysterious {biome}!"

        logger.debug(f"Generated quest: {quest}")
        return quest

    def react_to_player_action(self, action, player, biome):
        logger.info(f"Reacting to player action: {action} by {player} in {biome}")
        # Handle different player actions
        if action == 'move':
            # Check if the player triggers a new quest
            #return self.generate_quest(player, biome)
            return "Find the quest!"
