from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
from .character import Character

@dataclass
class CombatAction:
    player: Character
    action_type: str
    target: Optional[str] = None
    details: Optional[str] = None
    timestamp: datetime = datetime.now()

@dataclass
class Enemy:
    name: str
    level: int
    hp: int
    max_hp: int
    attack: int
    defense: int
    is_alive: bool = True
    
    def take_damage(self, amount: int) -> bool:
        """Apply damage and return whether enemy is still alive."""
        self.hp = max(0, self.hp - amount)
        self.is_alive = self.hp > 0
        return self.is_alive

@dataclass
class CombatState:
    players: List[Character]
    enemies: List[Enemy]
    round: int = 1
    actions: List[CombatAction] = None
    is_active: bool = True
    
    def __post_init__(self):
        if self.actions is None:
            self.actions = []

    def is_combat_over(self) -> bool:
        """Check if combat should end."""
        return (
            not any(enemy.is_alive for enemy in self.enemies) or
            not any(player.stats["HP"] > 0 for player in self.players)
        )