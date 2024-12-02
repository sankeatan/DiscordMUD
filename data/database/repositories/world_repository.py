from typing import List, Dict, Optional, Tuple
import json
import random
import logging
from ...models.world import Region, Location
from ..db_manager import DatabaseManager

logger = logging.getLogger(__name__)

class WorldRepository:
    """Repository for managing world data in the database."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self._initialize_tables()

    def _initialize_tables(self) -> None:
        """Create the necessary tables if they don't exist."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Regions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS regions (
                    x INTEGER,
                    y INTEGER,
                    biome TEXT NOT NULL,
                    features TEXT,
                    description TEXT,
                    has_water BOOLEAN,
                    has_resources BOOLEAN,
                    has_structure BOOLEAN,
                    PRIMARY KEY (x, y)
                )
            ''')
            
            # Locations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS locations (
                    x INTEGER,
                    y INTEGER,
                    region_x INTEGER,
                    region_y INTEGER,
                    features TEXT,
                    description TEXT,
                    FOREIGN KEY (region_x, region_y) REFERENCES regions(x, y),
                    PRIMARY KEY (x, y)
                )
            ''')
            
            conn.commit()

    async def generate_world(self, width: int, height: int, region_size: int, seed: Optional[int] = None) -> Dict[Tuple[int, int], Region]:
        """Generate a new world with regions."""
        if seed:
            random.seed(seed)

        biomes = ["Forest", "Desert", "Mountains", "Plains", "Swamp", "Tundra"]
        regions = {}

        for y in range(height):
            for x in range(width):
                biome = random.choice(biomes)
                region = Region(
                    biome=biome,
                    locations={},
                    has_water=random.random() > 0.7,
                    has_resources=random.random() > 0.6,
                    has_structure=random.random() > 0.8
                )
                regions[(x, y)] = region
                self.save_region(x, y, region)

        return regions

    def save_region(self, x: int, y: int, region: Region) -> None:
        """Save a region to the database."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO regions 
                (x, y, biome, features, description, has_water, has_resources, has_structure)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                x, y,
                region.biome,
                json.dumps([loc.features for loc in region.locations.values()]),
                region.description,
                region.has_water,
                region.has_resources,
                region.has_structure
            ))
            
            # Save associated locations
            for (loc_x, loc_y), location in region.locations.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO locations
                    (x, y, region_x, region_y, features, description)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    loc_x, loc_y,
                    x, y,
                    json.dumps(location.features),
                    location.description
                ))
            
            conn.commit()

    def get_region(self, x: int, y: int) -> Optional[Region]:
        """Retrieve a region from the database."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM regions WHERE x = ? AND y = ?', (x, y))
            row = cursor.fetchone()
            
            if not row:
                return None
                
            # Get associated locations
            cursor.execute('SELECT * FROM locations WHERE region_x = ? AND region_y = ?', (x, y))
            location_rows = cursor.fetchall()
            
            locations = {}
            for loc in location_rows:
                locations[(loc[0], loc[1])] = Location(
                    x=loc[0],
                    y=loc[1],
                    features=json.loads(loc[4]) if loc[4] else [],
                    description=loc[5]
                )
            
            return Region(
                biome=row[2],
                locations=locations,
                has_water=bool(row[5]),
                has_resources=bool(row[6]),
                has_structure=bool(row[7]),
                description=row[4]
            )

    def get_location(self, x: int, y: int) -> Optional[Location]:
        """Retrieve a specific location from the database."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM locations WHERE x = ? AND y = ?', (x, y))
            row = cursor.fetchone()
            
            if not row:
                return None
                
            return Location(
                x=row[0],
                y=row[1],
                features=json.loads(row[4]) if row[4] else [],
                description=row[5]
            )

    def clear_world(self) -> None:
        """Clear all world data from the database."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM locations')
            cursor.execute('DELETE FROM regions')
            conn.commit()

    def load_world(self) -> Dict[Tuple[int, int], Region]:
        """Load the world data from the database."""
        regions = {}
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM regions')
            rows = cursor.fetchall()

            for row in rows:
                x, y, biome, features, description, has_water, has_resources, has_structure = row
                region = Region(
                    biome=biome,
                    locations={},  # Assuming you will load locations separately
                    has_water=bool(has_water),
                    has_resources=bool(has_resources),
                    has_structure=bool(has_structure),
                    description=description
                )
                regions[(x, y)] = region

                # Load associated locations for this region
                cursor.execute('SELECT * FROM locations WHERE region_x = ? AND region_y = ?', (x, y))
                location_rows = cursor.fetchall()
                for loc in location_rows:
                    loc_x, loc_y, _, _, loc_features, loc_description = loc
                    region.locations[(loc_x, loc_y)] = Location(
                        x=loc_x,
                        y=loc_y,
                        features=json.loads(loc_features) if loc_features else [],
                        description=loc_description
                    )

        logger.info("World loaded successfully.")
        return regions