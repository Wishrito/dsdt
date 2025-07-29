import os
import discord
from dotenv import load_dotenv

load_dotenv()

SDT_ID = os.getenv("TEST_CHANNEL_ID")
sdt = discord.Object(id=SDT_ID, type=discord.Guild)
