from logger import setup_logger
import random

logger = setup_logger('combat_system')

player_characters = {}

class CombatState:
    def __init__(self, players, enemies):
        self.players = players
        self.enemies = enemies
        self.actions = []
        self.round = 1
    
    def is_combat_over(self):
        # Check if all enemies are defeated
        enemies_defeated = all(enemy["hp"] <= 0 for enemy in self.enemies)
        # Check if all players are defeated
        players_defeated = all(player["hp"] <= 0 for player in self.players)
        
        # Combat ends only if one side is fully defeated
        return enemies_defeated or players_defeated

class CombatManager:
    def __init__(self):
        self.current_combat = None

    def start_combat(self, players):
        """Initialize combat using player characters."""
        # Create enemy stats
        enemies = [{"name": "Goblin", "hp": 30, "attack": 5}, {"name": "Orc", "hp": 50, "attack": 10}]
        
        # Get player stats
        player_list = []
        for player_name in players:
            if player_name not in player_characters:
                logger.warning(f"Player {player_name} does not have a character!")
                continue
            character = player_characters[player_name]
            player_list.append({
                "name": character.name,
                "hp": character.stats["HP"],
                "attack": character.stats["Attack"],
                "defense": character.stats["Defense"]
            })

        self.current_combat = CombatState(player_list, enemies)
        logger.info("Combat started with players and enemies")
        return "Combat begins! Prepare for battle."

    def add_action(self, player, action):
        self.current_combat.actions.append({"player": player, "action": action})
        logger.info(f"Action received: {player} -> {action}")

    def resolve_round(self):
        """Resolve a combat round using player stats."""
        results = []
        for action in self.current_combat.actions:
            player = action['player']
            player_stats = next((p for p in self.current_combat.players if p["name"] == player), None)
            if not player_stats:
                continue

            # Resolve action (attack example)
            if action['action'].lower() == "attack":
                target = random.choice(self.current_combat.enemies)
                damage = max(1, player_stats["attack"] - target["attack"])  # Simple stat-based calculation
                target["hp"] -= damage
                results.append(f"{player} attacked {target['name']} for {damage} damage!")
                if target["hp"] <= 0:
                    results.append(f"{target['name']} has been defeated!")

        # Handle enemy actions (similar logic)
        return results
