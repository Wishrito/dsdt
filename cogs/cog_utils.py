from typing import Optional
import discord
from discord.ext import commands
from discord import app_commands

from modules.classes import DiscordBot


class CogUtils(commands.Cog):
    def __init__(self, bot: DiscordBot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check the bot's latency.")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Pong! Latency: {self.bot.latency * 1000:.2f}ms")

    @app_commands.command(name="refresh", description="Refresh the commands.")
    async def refresh(self, interaction: discord.Interaction):
        await self.bot.tree.sync()
        await interaction.response.send_message("Commands refreshed successfully!")

    @app_commands.command(name="nuke", description="Nuke a channel.")
    async def nuke(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
        if channel is None:
            channel = interaction.channel
        await interaction.response.send_message(f"Nuking channel {channel.name}...")
        await channel.clone(reason="Channel nuked by command.")
        await channel.delete()

async def setup(bot: DiscordBot):
    await bot.add_cog(CogUtils(bot))
