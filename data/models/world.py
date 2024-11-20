from dataclasses import dataclass
from typing import List, Optional, Dict

@dataclass
class Location:
    x: int
    y: int
    features: List[str] = None
    description: Optional[str] = None

@dataclass
class Region:
    biome: str
    locations: Dict[tuple, Location]
    has_water: bool = False
    has_resources: bool = False
    has_structure: bool = False
    description: Optional[str] = None

    def __post_init__(self):
        if self.locations is None:
            self.locations = {}