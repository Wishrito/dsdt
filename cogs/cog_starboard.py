import discord
from discord.ext import commands
from discord import app_commands
from db.models import Starboard, engine
from modules.classes import DiscordBot
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from modules.starboard_utils import starboard_autocomplete


class StarboardGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="starboard", description="Manage starboards.")
        self.guild_only = True


    @app_commands.command(name="list", description="List all starboards.")
    async def list_starboard(self, interaction: discord.Interaction):
        with Session(engine) as session:
            stmt = select(Starboard)
            results = session.execute(stmt).scalars().all()
            emb = discord.Embed(title="Starboards", color=discord.Color.blue())
            if results:
                for sb in results:
                    starboard_channel = interaction.guild.get_channel(sb.channel_id)
                    if starboard_channel:
                        emb.add_field(name=f"{sb.id}", value=f"Channel: {starboard_channel.mention}\nEmoji: {sb.emoji_name}\nVotes requis: {sb.emoji_count}", inline=False)
            else:
                emb.description = "No starboards found."

            await interaction.response.send_message(embed=emb)

        print(f"Starboard list command executed by {interaction.user}")


    @app_commands.command(name="add", description="Add a starboard.")
    async def add_starboard(self, interaction: discord.Interaction, channel: discord.TextChannel, emoji_name: str, emoji_count: int = 3):
        with Session(engine) as session:
            new_starboard = Starboard(channel_id=channel.id, emoji_name=emoji_name, emoji_count=emoji_count)
            session.add(new_starboard)
            session.commit()
            starboard_channel = await interaction.guild.fetch_channel(new_starboard.channel_id)
            await interaction.response.send_message(f"Starboard added: {starboard_channel.mention}")
        print(f"Starboard added by {interaction.user}: {new_starboard}")


    @app_commands.command(name="remove", description="Remove a starboard.")
    @app_commands.autocomplete(starboard=starboard_autocomplete)
    async def remove_starboard(self, interaction: discord.Interaction, starboard: int):
        with Session(engine) as session:
            stmt = select(Starboard).where(Starboard.id == starboard)
            result = session.execute(stmt).scalars().first()
            if result:
                session.delete(result)
                session.commit()
                # Rafraîchir le cache après suppression
                await interaction.response.send_message(
                    f"Starboard supprimé (ID: {result.id}, Channel: {result.channel_id})"
                )
                print(f"Starboard removed by {interaction.user}: {result}")
            else:
                await interaction.response.send_message("Starboard not found.")


class CogStarboard(commands.Cog):
    def __init__(self, bot: DiscordBot):
        self.bot = bot
        self.bot.tree.add_command(StarboardGroup())



async def setup(bot: DiscordBot):
    await bot.add_cog(CogStarboard(bot))
