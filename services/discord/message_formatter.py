import discord
from typing import List, Dict, Any, Optional
from ...data.models.character import Character
from ...data.models.combat import CombatState

class MessageFormatter:
    """Handles formatting of Discord messages and embeds."""

    @staticmethod
    def character_info(character: Character) -> discord.Embed:
        """Format character information as an embed."""
        embed = discord.Embed(
            title=f"{character.name}'s Character Sheet",
            color=discord.Color.blue()
        )
        
        # Basic Info
        embed.add_field(
            name="Basic Info",
            value=f"Class: {character.player_class}\nLevel: {character.level}\nXP: {character.xp}",
            inline=False
        )
        
        # Stats
        stats_text = "\n".join(f"{stat}: {value}" for stat, value in character.stats.items())
        embed.add_field(name="Stats", value=stats_text, inline=True)
        
        # Inventory
        inventory_text = ", ".join(character.inventory) if character.inventory else "Empty"
        embed.add_field(name="Inventory", value=inventory_text, inline=True)
        
        # Location
        embed.add_field(name="Location", value=f"({character.location[0]}, {character.location[1]})", inline=True)
        
        return embed

    @staticmethod
    def combat_status(combat_state: CombatState) -> discord.Embed:
        """Format combat status as an embed."""
        embed = discord.Embed(
            title=f"Combat Round {combat_state.round}",
            color=discord.Color.red()
        )
        
        # Players
        players_text = ""
        for player in combat_state.players:
            hp_percent = (player.stats["HP"] / player.BASE_STATS["HP"]) * 100
            players_text += f"{player.name}: {player.stats['HP']} HP ({hp_percent:.0f}%)\n"
        embed.add_field(name="Players", value=players_text or "No players", inline=False)
        
        # Enemies
        enemies_text = ""
        for enemy in combat_state.enemies:
            hp_percent = (enemy.hp / enemy.max_hp) * 100
            enemies_text += f"{enemy.name}: {enemy.hp} HP ({hp_percent:.0f}%)\n"
        embed.add_field(name="Enemies", value=enemies_text or "No enemies", inline=False)
        
        return embed

    @staticmethod
    def quest_info(quest: Dict[str, Any]) -> discord.Embed:
        """Format quest information as an embed."""
        embed = discord.Embed(
            title=quest.get("title", "Quest"),
            description=quest.get("description", "No description available."),
            color=discord.Color.gold()
        )
        
        # Difficulty
        embed.add_field(name="Difficulty", value=f"Level {quest.get('difficulty', '???')}", inline=True)
        
        # Rewards
        rewards = quest.get("rewards", [])
        rewards_text = "\n".join(rewards) if rewards else "No rewards listed"
        embed.add_field(name="Rewards", value=rewards_text, inline=True)
        
        # Location
        if "location" in quest:
            embed.add_field(name="Location", value=f"({quest['location'][0]}, {quest['location'][1]})", inline=True)
        
        return embed

    @staticmethod
    def error_message(error: str) -> str:
        """Format error messages."""
        return f"❌ Error: {error}"

    @staticmethod
    def success_message(message: str) -> str:
        """Format success messages."""
        return f"✅ {message}"

    @staticmethod
    def help_command(commands: List[Dict[str, str]]) -> discord.Embed:
        """Format help information as an embed."""
        embed = discord.Embed(
            title="Game Commands",
            description="Here are all available commands:",
            color=discord.Color.blue()
        )
        
        for cmd in commands:
            embed.add_field(
                name=f"{cmd['name']} {cmd.get('usage', '')}",
                value=cmd.get('description', 'No description available.'),
                inline=False
            )
            
        return embed