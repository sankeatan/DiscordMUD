from logger import setup_logger
import random
from ai_npc import AINPC
from world_generation import WorldGenerator

logger = setup_logger('ai_game_master')

class AIGameMaster:
    def __init__(self):
        logger.info("Initializing AIGameMaster")
        # Quest templates or response handling could be loaded here.
        self.quests = []
    
    def evaluate_creative_move(self, player, action_text, enemies):
        """
        Use AI to evaluate a creative move and determine its outcome.
        """
        npc = AINPC(name="GameMaster", personality="impartial")
        prompt = f"""
        You are the GameMaster of a turn-based RPG. A player named {player} is attempting this creative move: 
        "{action_text}". Evaluate the move and provide:
        1. A feasibility score (0-100) indicating the likelihood of success.
        2. A description of the outcome in the context of a battle with enemies: {', '.join(e['name'] for e in enemies)}.
        """
        try:
            response = npc.generate_dialogue(prompt)
            return response
        except Exception as e:
            logger.error(f"Error evaluating creative move: {str(e)}")
            return "The move's outcome is unclear, but it seems intriguing!"
    
    def process_actions(self, actions, enemies):
        results = []
        for action in actions:
            player = str(action['player'])
            action_type = action['action'].lower()
            
            if action_type.startswith("creative:"):
                # Extract creative action text
                action_text = action['action'][len("creative:"):].strip()
                creative_result = self.evaluate_creative_move(player, action_text, enemies)
                results.append(f"{player}'s creative move result: {creative_result}")

            elif action_type == 'attack':
                target = random.choice(enemies)
                damage = random.randint(10, 20)
                target['hp'] -= damage
                crit = random.random() < 0.2  # 20% chance for a critical hit
                if crit:
                    damage *= 2
                    results.append(f"Critical Hit! {player} attacked {target['name']} for {damage} damage!")
                else:
                    results.append(f"{player} attacked {target['name']} for {damage} damage!")

                if target['hp'] <= 0:
                    results.append(f"{target['name']} has been defeated!")

            elif action_type == 'defend':
                results.append(f"{player} takes a defensive stance, reducing incoming damage.")

            elif action_type == 'cast spell':
                spell_type = random.choice(['fireball', 'lightning bolt', 'healing aura'])
                spell_effect = random.randint(15, 30) if spell_type != 'healing aura' else random.randint(20, 40)
                if spell_type == 'healing aura':
                    results.append(f"{player} casts a {spell_type}, healing the party for {spell_effect} HP!")
                else:
                    target = random.choice(enemies)
                    target['hp'] -= spell_effect
                    results.append(f"{player} casts {spell_type}, dealing {spell_effect} damage to {target['name']}!")

            elif action_type == 'use item':
                item_used = "Health Potion"
                heal_amount = random.randint(20, 30)
                results.append(f"{player} uses a {item_used}, recovering {heal_amount} HP!")

            else:
                results.append(f"{player} attempts a creative move: {action_type}. The results are unpredictable!")

        # Enemy responses
        for enemy in enemies:
            if enemy['hp'] > 0:
                target_player = random.choice(actions)['player']
                damage = random.randint(5, 15)
                results.append(f"{enemy['name']} attacks {target_player}, dealing {damage} damage!")

        return results
    
    def generate_combat_narrative(self, actions, outcomes):
        """
        Create a cohesive narrative including creative move outcomes.
        """
        narrative = ["The battle unfolds with the following actions:"]
        for action in actions:
            if action['action'].startswith("creative:"):
                narrative.append(f"{action['player']} attempted a creative move: {action['action'][len('creative:'):].strip()}.")
            else:
                narrative.append(f"{action['player']} chose to {action['action']}.")

        narrative.append("\nThe results of the round are as follows:")
        for outcome in outcomes:
            narrative.append(outcome)

        narrative.append("\nThe enemies seem to adjust to the players' strategies.")
        return "\n".join(narrative)

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

    def generate_encounter(self, biome):
        """Generate an encounter based on the biome."""
        if biome == "forest":
            return "You hear rustling in the bushes. A pack of wolves appears!"
        elif biome == "desert":
            return "A sandstorm brews, obscuring your vision. Out of the haze, bandits approach!"
        # Add more biome-specific encounters...
        else:
            return f"You encounter a unique challenge in the {biome}."
        
    def generate_quest_board(self, town_location, world_gen):
        """Generate quests for the town based on surrounding regions."""
        quests = []
        x, y = town_location
        surrounding_regions = [
            world_gen.get_region(x+dx, y+dy)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
            if world_gen.get_region(x+dx, y+dy)
        ]
        for region in surrounding_regions:
            biome = region["biome"]
            quests.append(f"Explore the {biome} and report back.")
        return quests