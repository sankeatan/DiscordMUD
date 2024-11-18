class Character:
    BASE_STATS = {
        "HP": 100,
        "Attack": 10,
        "Defense": 5,
        "Magic": 10,
    }

    def __init__(self, name, player_class="Adventurer"):
        self.name = name
        self.player_class = player_class
        self.stats = self.BASE_STATS.copy()
        self.level = 1
        self.xp = 0
        self.inventory = []
    
    def __str__(self):
        return self.name

    def allocate_stat_points(self, hp=0, attack=0, defense=0, magic=0):
        """Allocate stat points to customize the character."""
        self.stats["HP"] += hp
        self.stats["Attack"] += attack
        self.stats["Defense"] += defense
        self.stats["Magic"] += magic

    def level_up(self):
        """Increase level and grant stat points."""
        self.level += 1
        self.xp = 0
        return 5  # Number of points to allocate
