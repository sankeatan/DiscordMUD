from typing import List, Dict, Optional, Tuple
from ...data.models.combat import CombatState, CombatAction, Enemy
from ...data.models.character import Character
from ..ai.narrative_service import NarrativeService
import random
import logging

logger = logging.getLogger(__name__)

class CombatService:
    """Manages combat encounters and resolution."""
    
    def __init__(self, narrative_service: NarrativeService):
        self.narrative_service = narrative_service
        self.current_combat: Optional[CombatState] = None

    def generate_enemies(self, player_levels: List[int], count: int = 2) -> List[Enemy]:
        """Generate appropriate enemies based on player levels."""
        avg_level = sum(player_levels) / len(player_levels)
        enemies = []
        
        enemy_types = [
            ("Goblin", 0.8),
            ("Orc", 1.0),
            ("Troll", 1.2),
            ("Dragon", 1.5)
        ]
        
        for _ in range(count):
            enemy_type, multiplier = random.choice(enemy_types)
            level = max(1, int(avg_level * multiplier))
            
            enemy = Enemy(
                name=f"Level {level} {enemy_type}",
                level=level,
                hp=50 + (level * 10),
                max_hp=50 + (level * 10),
                attack=5 + (level * 2),
                defense=3 + (level * 1)
            )
            enemies.append(enemy)
            
        return enemies

    def start_combat(self, players: List[Character]) -> Tuple[str, CombatState]:
        """Initialize a new combat encounter."""
        if self.current_combat and self.current_combat.is_active:
            raise ValueError("Combat is already in progress")

        player_levels = [player.level for player in players]
        enemies = self.generate_enemies(player_levels)
        
        self.current_combat = CombatState(
            players=players,
            enemies=enemies
        )
        
        return "Combat begins! Prepare for battle!", self.current_combat

    def add_action(self, player: Character, action_text: str) -> None:
        """Record a player's action for the current combat round."""
        if not self.current_combat or not self.current_combat.is_active:
            raise ValueError("No active combat session")

        action_type = "standard"
        target = None
        details = action_text

        if action_text.lower().startswith("creative:"):
            action_type = "creative"
            details = action_text[len("creative:"):].strip()
        elif action_text.lower().startswith("attack"):
            action_type = "attack"
            parts = action_text.split(" ", 1)
            target = parts[1] if len(parts) > 1 else None

        action = CombatAction(
            player=player,
            action_type=action_type,
            target=target,
            details=details
        )
        
        self.current_combat.actions.append(action)

    async def resolve_round(self) -> str:
        """Resolve the current combat round and generate narrative."""
        if not self.current_combat or not self.current_combat.is_active:
            raise ValueError("No active combat session")

        # Process player actions
        results = []
        for action in self.current_combat.actions:
            result = self._process_action(action)
            results.append(result)

        # Process enemy actions
        enemy_results = self._process_enemy_actions()
        results.extend(enemy_results)

        # Generate narrative
        narrative = await self.narrative_service.generate_combat_narrative(
            self.current_combat.actions,
            results
        )

        # Clean up round
        self.current_combat.round += 1
        self.current_combat.actions = []

        # Check if combat is over
        if self.current_combat.is_combat_over():
            self.current_combat.is_active = False
            narrative += "\nCombat has ended!"

        return narrative

    def _process_action(self, action: CombatAction) -> str:
        """Process a single combat action."""
        if action.action_type == "attack":
            return self._process_attack(action)
        elif action.action_type == "creative":
            return self._process_creative_action(action)
        else:
            return f"{action.player.name} takes a defensive stance."

    def _process_attack(self, action: CombatAction) -> str:
        """Process an attack action."""
        player = action.player
        target = None

        # Find target
        if action.target:
            target = next(
                (e for e in self.current_combat.enemies if action.target.lower() in e.name.lower()),
                None
            )
        if not target:
            target = random.choice([e for e in self.current_combat.enemies if e.is_alive])

        # Calculate damage
        base_damage = player.stats["Attack"]
        defense = target.defense
        damage = max(1, base_damage - defense)
        
        # Apply damage
        target.take_damage(damage)
        
        return f"{player.name} attacks {target.name} for {damage} damage!"

    def _process_creative_action(self, action: CombatAction) -> str:
        """Process a creative action."""
        # This could be expanded with more complex logic or AI evaluation
        success_chance = random.random()
        if success_chance > 0.7:  # 30% chance of great success
            damage = random.randint(15, 25)
            target = random.choice([e for e in self.current_combat.enemies if e.is_alive])
            target.take_damage(damage)
            return f"{action.player.name}'s creative action succeeds brilliantly! {action.details} deals {damage} damage!"
        elif success_chance > 0.3:  # 40% chance of moderate success
            damage = random.randint(5, 15)
            target = random.choice([e for e in self.current_combat.enemies if e.is_alive])
            target.take_damage(damage)
            return f"{action.player.name}'s creative action succeeds! {action.details} deals {damage} damage!"
        else:  # 30% chance of failure
            return f"{action.player.name}'s creative action fails! {action.details} has no effect!"

    def _process_enemy_actions(self) -> List[str]:
        """Process actions for all active enemies."""
        results = []
        for enemy in self.current_combat.enemies:
            if not enemy.is_alive:
                continue

            target = random.choice(self.current_combat.players)
            damage = max(1, enemy.attack - target.stats["Defense"])
            target.stats["HP"] -= damage
            results.append(f"{enemy.name} attacks {target.name} for {damage} damage!")

        return results