from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class Character:
    name: str
    player_class: str = "Adventurer"
    level: int = 1
    xp: int = 0
    location: Tuple[int, int] = (0, 0)
    inventory: List[str] = None
    stats: Dict[str, int] = None

    BASE_STATS = {
        "HP": 100,
        "Attack": 10,
        "Defense": 5,
        "Magic": 10,
    }

    def __post_init__(self):
        if self.inventory is None:
            self.inventory = []
        if self.stats is None:
            self.stats = self.BASE_STATS.copy()

    def allocate_stat_points(self, hp: int = 0, attack: int = 0, defense: int = 0, magic: int = 0) -> None:
        """Allocate stat points to customize the character."""
        self.stats["HP"] += hp
        self.stats["Attack"] += attack
        self.stats["Defense"] += defense
        self.stats["Magic"] += magic

    def level_up(self) -> int:
        """Increase level and grant stat points."""
        self.level += 1
        self.xp = 0
        return 5  # Number of points to allocate