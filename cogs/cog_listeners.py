import discord
from discord.ext import commands
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import Starboard, StarboardContent, engine
from modules.classes import DiscordBot
from modules.starboard_utils import handle_starboard_reaction


class CogListeners(commands.Cog):
    def __init__(self, bot: DiscordBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {self.bot.user} (ID: {self.bot.user.id})")
        test_channel = self.bot.get_channel(1397405663428219085)
        if isinstance(test_channel, discord.TextChannel) and test_channel.guild:
            await test_channel.send(f"Bot is online and ready! {test_channel.guild.name}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
        """
        Handles the event when a reaction is added to a message, updating the starboard and favorites in the database.
        """
        print(f"user == {self.bot.user.name} : {user == self.bot.user}")
        if user == self.bot.user:
            return
        print(
            f'{user} reacted with {reaction.emoji} on message {reaction.message.id}. content = "{reaction.message.content}"'
        )
        await handle_starboard_reaction(reaction)

    @commands.Cog.listener()
    async def on_reaction_remove(
        self, reaction: discord.Reaction, user: discord.Member
    ):
        """
        Handles the event when a reaction is removed from a message.
        """
        if user == self.bot.user:
            return
        print(
            f"{user} removed reaction {reaction.emoji} from message {reaction.message.id}"
        )
        await handle_starboard_reaction(reaction)

async def setup(bot: DiscordBot):
    await bot.add_cog(CogListeners(bot))
