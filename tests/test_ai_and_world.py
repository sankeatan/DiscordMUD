import pytest
from ai_game_master import AIGameMaster
from world_generation import WorldGenerator

# Unit Test: AI Game Master Quest Generation
def test_generate_quest():
    ai_gm = AIGameMaster()
    quest = ai_gm.generate_quest("Player1", "forest")
    assert "protect the forest" in quest

# Integration Test: World Generation and Persistence
def test_world_generation():
    world_gen = WorldGenerator(world_width=10, world_height=10, region_size=3, seed=123)
    original_world = world_gen.generate_regions()
    world_gen.save_world_to_db()

    # Reload world from DB to verify persistence
    loaded_world = world_gen.load_world_from_db()
    assert isinstance(loaded_world, list), f"Expected a list, but got {type(loaded_world)}"
    assert len(loaded_world) > 0, f"Expected non-empty list, but got {loaded_world}"

    # Print more details about the loaded world for debugging
    print(f"Loaded world contains {len(loaded_world)} x {len(loaded_world[0])} regions")
    if loaded_world:
        print(f"First region: {loaded_world[0][0]}")

    # Compare original and loaded worlds
    assert len(original_world) == len(loaded_world), f"Original world had {len(original_world)} rows, but loaded world has {len(loaded_world)}"
    assert len(original_world[0]) == len(loaded_world[0]), f"Original world had {len(original_world[0])} columns, but loaded world has {len(loaded_world[0])}"
    
    for y in range(len(original_world)):
        for x in range(len(original_world[0])):
            original = original_world[y][x]
            loaded = loaded_world[y][x]
            assert original['biome'] == loaded['biome'], f"Biome mismatch at ({x}, {y}): original {original['biome']}, loaded {loaded['biome']}"
            assert original['sub_regions'] == loaded['sub_regions'], f"Sub-regions mismatch at ({x}, {y})"

# test_ai_and_world.py
def test_get_random_biome():
    """Test that get_random_biome() returns a valid biome."""
    world_gen = WorldGenerator(world_width=20, world_height=20, region_size=5, seed=42)
    world_gen.generate_regions()
    biome = world_gen.get_random_biome()
    
    assert biome in ['forest', 'desert', 'mountain', 'plains', 'swamp']

