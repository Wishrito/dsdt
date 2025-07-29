import discord
from discord import app_commands
from discord.ext import commands

from db.models import Base, engine

class DiscordBot(commands.Bot):
    def __init__(self, intents: discord.Intents):
        super().__init__(command_prefix="!",intents=intents)

    async def setup_hook(self):
        Base.metadata.create_all(engine)

        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} global slash commands.")
        except Exception as e:
            print(f"Error syncing global slash commands: {e}")
