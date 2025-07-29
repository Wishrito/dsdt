import asyncio
import os

import discord
from dotenv import load_dotenv

from modules.classes import DiscordBot
from modules.misc_utils import load_cogs

# Load environment variables from .env file
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = DiscordBot(intents=intents)


async def main():
    await load_cogs(bot)
    if DISCORD_TOKEN is None:
        raise ValueError("\"DISCORD_TOKEN\" environment variable is not set.")
    await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
