import random
import sqlite3
import noise
import json
import random
from logger import setup_logger

logger = setup_logger('world_generation')

# Top-level biomes and sub-level microbiomes
TOP_LEVEL_BIOMES = {
    'forest': ['dense_forest', 'clearing', 'river', 'swamp'],
    'desert': ['dune', 'oasis', 'rocky_outcrop', 'sandstorm'],
    'mountain': ['cliffside', 'cave', 'plateau', 'snowy_peak'],
    'savanna': ['grassland', 'shrubland', 'river', 'oasis'],
    'tundra': ['frozen_lake', 'snowfield', 'permafrost', 'glacier'],
}

# Biome adjacency rules (what biomes can be next to each other)
BIOME_ADJACENCY = {
    'forest': ['mountain', 'savanna', 'river'],
    'desert': ['savanna', 'river', 'mountain'],
    'mountain': ['forest', 'desert', 'tundra'],
    'savanna': ['desert', 'forest', 'river'],
    'tundra': ['mountain'],
}

class WorldGenerator:
    def __init__(self, world_width, world_height, region_size, seed=None):
        logger.info(f"Initializing WorldGenerator with width={world_width}, height={world_height}, region_size={region_size}, seed={seed}")
        self.world_width = world_width
        self.world_height = world_height
        self.region_size = region_size  # Size of each top-level region
        self.seed = seed
        if seed:
            random.seed(seed)
        self.regions = [[None for _ in range(world_width // region_size)] for _ in range(world_height // region_size)]
        self.TOP_LEVEL_BIOMES = TOP_LEVEL_BIOMES
        self.BIOME_ADJACENCY = BIOME_ADJACENCY
    
    
    def generate_regions(self):
        """Generates top-level regions with primary biomes based on Perlin noise."""
        logger.info("Generating regions")
        scale = 5.0  # Scale of the noise function
        for y in range(len(self.regions)):
            for x in range(len(self.regions[y])):
                elevation = noise.pnoise2(x / scale, y / scale, octaves=6, persistence=0.5, lacunarity=2.0)
                biome = self.select_biome_based_on_elevation(elevation)
                self.regions[y][x] = {
                    'biome': biome,
                    'sub_regions': self.generate_sub_regions(biome, x, y)
                }
        logger.debug(f"Generated {len(self.regions)} x {len(self.regions[0])} regions")
        return self.regions
    
    def select_biome_based_on_elevation(self, elevation):
        """Selects a biome based on elevation."""
        if elevation < -0.3:
            return 'river'
        elif elevation < 0.0:
            return 'forest'
        elif elevation < 0.3:
            return 'savanna'
        elif elevation < 0.6:
            return 'mountain'
        else:
            return 'tundra'
    
    def select_sub_biome(self, microbiomes, elevation):
        """Select a sub-biome based on elevation and the parent biome's options."""
        if elevation < -0.2:
            return microbiomes[0]  # e.g., river
        elif elevation < 0.2:
            return microbiomes[1]  # e.g., clearing
        elif elevation < 0.5:
            return microbiomes[2]  # e.g., dense forest
        else:
            return microbiomes[3]  # e.g., swamp
    
    def get_random_biome(self):
        """Selects a random biome from the generated regions."""
        if not self.regions:
            logger.error("No regions available to select a biome from")
            raise ValueError("Regions must be generated before selecting a biome.")
        
        random_row = random.choice(self.regions)
        random_region = random.choice(random_row)
        logger.info(f"Selected biome: {random_region['biome']}")
        return random_region['biome']
    
    def generate_sub_regions(self, top_biome, region_x, region_y):
        """Generates microbiomes within a region with logical placement."""
        sub_region_grid = [[None for _ in range(self.region_size)] for _ in range(self.region_size)]
        microbiomes = TOP_LEVEL_BIOMES[top_biome]
        
        scale = 10.0
        
        for y in range(self.region_size):
            for x in range(self.region_size):
                # Use local elevation variation for more diverse microbiome placement
                local_elevation = noise.pnoise2(
                    (region_x * self.region_size + x) / scale,
                    (region_y * self.region_size + y) / scale,
                    octaves=2, persistence=0.5, lacunarity=2.0
                )
                sub_biome = self.select_sub_biome(microbiomes, local_elevation)
                sub_region_grid[y][x] = sub_biome
        return sub_region_grid

    def save_world_to_db(self):
        logger.info("Saving world to database")
        conn = sqlite3.connect('game_world.db')
        cursor = conn.cursor()
        
        # Drop the existing table if it exists
        cursor.execute('DROP TABLE IF EXISTS regions')
        
        # Create table with the new schema
        cursor.execute('''
        CREATE TABLE regions
        (region_x INTEGER, region_y INTEGER, biome TEXT, sub_regions TEXT)
        ''')
        
        # Insert new data
        for y, row in enumerate(self.regions):
            for x, region in enumerate(row):
                cursor.execute('''
                INSERT INTO regions (region_x, region_y, biome, sub_regions)
                VALUES (?, ?, ?, ?)
                ''', (x, y, region['biome'], json.dumps(region['sub_regions'])))
        
        conn.commit()
        conn.close()
        logger.info(f"World saved to database: {len(self.regions) * len(self.regions[0])} regions")

    def load_world_from_db(self):
        logger.info("Loading world from database")
        conn = sqlite3.connect('game_world.db')
        cursor = conn.cursor()
        
        # Check if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='regions'")
        if not cursor.fetchone():
            logger.warning("Regions table does not exist in the database")
            conn.close()
            return []

        cursor.execute("SELECT * FROM regions")
        rows = cursor.fetchall()
        logger.info(f"Number of rows retrieved: {len(rows)}")
        
        if not rows:
            logger.warning("No regions found in the database")
            conn.close()
            return []

        max_x = max(row[0] for row in rows)
        max_y = max(row[1] for row in rows)
        loaded_regions = [[None for _ in range(max_x + 1)] for _ in range(max_y + 1)]

        for row in rows:
            x, y, biome, sub_regions = row
            loaded_regions[y][x] = {
                'biome': biome,
                'sub_regions': json.loads(sub_regions)
            }

        conn.close()
        logger.info(f"World loaded from database: {len(loaded_regions) * len(loaded_regions[0])} regions")
        return loaded_regions

    def get_region(self, x, y):
        """
        Get the region at the specified coordinates.
        If the coordinates are out of bounds, wrap around to the other side of the world.
        """
        # Wrap around coordinates if they're out of bounds
        wrapped_x = x % len(self.regions[0])
        wrapped_y = y % len(self.regions)

        logger.info(f"Getting region at coordinates ({x}, {y}), wrapped to ({wrapped_x}, {wrapped_y})")

        try:
            region = self.regions[wrapped_y][wrapped_x]
            return region
        except IndexError:
            logger.error(f"Failed to get region at ({wrapped_x}, {wrapped_y})")
            raise ValueError(f"Invalid region coordinates: ({x}, {y})")

# Example usage:
#world_gen = WorldGenerator(world_width=20, world_height=20, region_size=5, seed=42)
#world_gen.generate_regions()
#world_gen.save_world_to_db()
#world_gen.load_world_from_db()
