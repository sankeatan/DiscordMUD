from typing import Dict, List, Tuple, Optional
from data.models.world import Region, Location
from data.database.repositories.world_repository import WorldRepository
from ..ai.narrative_service import NarrativeService
import logging

logger = logging.getLogger(__name__)

class WorldService:
    """Manages world generation, state, and interactions."""
    
    def __init__(self, 
                 world_repository: WorldRepository,
                 narrative_service: NarrativeService,
                 world_width: int = 20,
                 world_height: int = 20,
                 region_size: int = 5):
        self.repository = world_repository
        self.narrative_service = narrative_service
        self.width = world_width
        self.height = world_height
        self.region_size = region_size
        self.current_world = None

    async def generate_world(self, seed: Optional[int] = None) -> None:
        """Generate a new world with regions."""
        self.current_world = await self.repository.generate_world(
            self.width, 
            self.height, 
            self.region_size, 
            seed
        )
        logger.info("World generated successfully.")

    async def get_location_description(self, location: Tuple[int, int]) -> str:
        """Get or generate a description for a location."""
        region = self.get_region_at_location(location)
        if not region:
            raise ValueError("Invalid location")

        features = self.get_location_features(location)
        description = await self.narrative_service.generate_location_description(
            region.biome,
            features
        )
        logger.info(f"Location description retrieved for {location}: {description}")
        return description

    def get_region_at_location(self, location: Tuple[int, int]) -> Optional[Region]:
        """Get the region data for a specific location."""
        x, y = location
        if not self.current_world:
            self.current_world = self.repository.load_world()
        
        region_x = x // self.region_size
        region_y = y // self.region_size
        
        try:
            return self.current_world[(region_x, region_y)]
        except KeyError:
            return None

    def get_location_features(self, location: Tuple[int, int]) -> List[str]:
        """Get special features at a location."""
        region = self.get_region_at_location(location)
        if not region:
            return []
        
        features = []
        if region.has_water:
            features.append("water source")
        if region.has_resources:
            features.append("natural resources")
        if region.has_structure:
            features.append("mysterious structure")
        return features

    async def move_character(self, 
                             current_location: Tuple[int, int], 
                             direction: str) -> Tuple[Tuple[int, int], str]:
        """Move character in a direction and get new location description."""
        x, y = current_location
        
        if direction == "north":
            y -= 1
        elif direction == "south":
            y += 1
        elif direction == "east":
            x += 1
        elif direction == "west":
            x -= 1
        else:
            raise ValueError("Invalid direction")
        
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise ValueError("Cannot move beyond world boundaries")
        
        new_location = (x, y)
        
        description = await self.get_location_description(new_location)
        
        logger.info(f"Character moved from {current_location} to {new_location} in direction {direction}")
        return new_location, description