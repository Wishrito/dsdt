from pathlib import Path


from .classes import DiscordBot

# Global cache {guild_id: List[Tuple[channel_name, starboard_id]]}
starboard_cache: dict[int, list[tuple[str, int]]] = {}




async def load_cogs(bot: DiscordBot):
    """
    Load all cogs from the 'cogs' directory.
    """
    for cog in Path("cogs").iterdir():
        if all([cog.is_file(), cog.suffix == ".py", cog.name != "__init__.py"]):
            await bot.load_extension(f"cogs.{cog.stem}")
            print(f"Loaded cog: {cog.stem}")
        else:
            print(f"Skipping non-Python file: {cog.name}")
