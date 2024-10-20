import random
import sqlite3
import noise
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
        """Saves regions and sub-regions to the database."""
        logger.info("Saving world to database")
        conn = sqlite3.connect('game_world.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS regions (region_x INT, region_y INT, biome TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS sub_regions (region_x INT, region_y INT, sub_x INT, sub_y INT, sub_biome TEXT)''')
        cursor.execute('''DELETE FROM regions''')
        cursor.execute('''DELETE FROM sub_regions''')
        
        # Save regions and sub-regions
        for region_y in range(len(self.regions)):
            for region_x in range(len(self.regions[region_y])):
                region = self.regions[region_y][region_x]
                biome = region['biome']
                cursor.execute('INSERT INTO regions (region_x, region_y, biome) VALUES (?, ?, ?)', (region_x, region_y, biome))
                
                # Save sub-regions (microbiomes)
                for sub_y in range(self.region_size):
                    for sub_x in range(self.region_size):
                        sub_biome = region['sub_regions'][sub_y][sub_x]
                        cursor.execute('INSERT INTO sub_regions (region_x, region_y, sub_x, sub_y, sub_biome) VALUES (?, ?, ?, ?, ?)', 
                                       (region_x, region_y, sub_x, sub_y, sub_biome))

        conn.commit()
        conn.close()
        logger.info("World saved to database")

    def load_world_from_db(self):
        """Loads regions and sub-regions from the database."""
        logger.info("Loading world from database")
        conn = sqlite3.connect('game_world.db')
        cursor = conn.cursor()
        
        # Load regions
        cursor.execute('SELECT * FROM regions')
        data = cursor.fetchall()
        for row in data:
            region_x, region_y, biome = row
            self.regions[region_y][region_x] = {'biome': biome, 'sub_regions': [[None for _ in range(self.region_size)] for _ in range(self.region_size)]}
        
        # Load sub-regions
        cursor.execute('SELECT * FROM sub_regions')
        data = cursor.fetchall()
        for row in data:
            region_x, region_y, sub_x, sub_y, sub_biome = row
            self.regions[region_y][region_x]['sub_regions'][sub_y][sub_x] = sub_biome

        conn.close()
        logger.info("World loaded from database")

# Example usage:
#world_gen = WorldGenerator(world_width=20, world_height=20, region_size=5, seed=42)
#world_gen.generate_regions()
#world_gen.save_world_to_db()
#world_gen.load_world_from_db()
