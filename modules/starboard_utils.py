import discord
from discord import app_commands
from sqlalchemy import select
from sqlalchemy.orm import Session
from db.models import Starboard, StarboardContent, engine


async def starboard_autocomplete(
    interaction: discord.Interaction, current: str = ""
) -> list[app_commands.Choice[int]]:
    output: list[app_commands.Choice[int]] = []
    with Session(engine) as session:
        stmt = select(Starboard).where(Starboard.channel_id.ilike(f"%{current}%"))
        results = session.execute(stmt).scalars().all()
        for starboard in results:
            channel = interaction.guild.get_channel(starboard.channel_id)
            output.append(app_commands.Choice(name=channel.name, value=starboard.id))

    return output[:25]


async def handle_starboard_reaction(reaction: discord.Reaction):
    with Session(engine) as session:
        res_starboard = await get_starboard_entry(session, reaction)
        if not res_starboard:
            print(f"No starboard found for emoji {reaction.emoji.name}, aborting.")
            return

        # Prevent duplicate entries for the same message and emoji
        if int(res_starboard.channel_id) == reaction.message.channel.id:
            print("Can't send a starboard message to the same channel.")
            return
        # CORRECTION : Passer aussi message_id
        res_fav = await get_starboard_content_entry(
            session, res_starboard.id, reaction.message.id
        )
        if not res_fav:
            # Créer une nouvelle entrée
            res_fav = StarboardContent(
                message_id=reaction.message.id,
                starboard_id=res_starboard.id,
                emoji_count=reaction.count,  # AJOUTÉ : Initialiser avec le count actuel
            )
            session.add(res_fav)
            # Créer et envoyer l'embed
            fav_emb = await create_fav_embed(reaction)
            starboard_channel = await reaction.message.guild.fetch_channel(
                res_starboard.channel_id
            )
            if starboard_channel and isinstance(
                starboard_channel, discord.TextChannel
            ):
                starboard_msg = await starboard_channel.send(embed=fav_emb)
                res_fav.starboard_message_id = (
                    starboard_msg.id
                )
            session.commit()
            print(f"New starboard entry created: {res_fav}")
        else:
            # update existing entry
            old_count = res_fav.emoji_count
            res_fav.emoji_count = reaction.count
            # update the starboard message if it exists
            if res_fav.starboard_message_id:
                try:
                    starboard_channel = await reaction.message.guild.fetch_channel(
                        res_starboard.channel_id
                    )
                    if starboard_channel and isinstance(
                        starboard_channel, discord.TextChannel
                    ):
                        starboard_msg = await starboard_channel.fetch_message(
                            res_fav.starboard_message_id
                        )
                        updated_embed = await create_fav_embed(reaction)
                        await starboard_msg.edit(embed=updated_embed)
                except discord.NotFound:
                    print(
                        f"Starboard message {res_fav.starboard_message_id} not found, it may have been deleted"
                    )
                    res_fav.starboard_message_id = None
            session.commit()
            print(f"Starboard entry updated: {old_count} -> {res_fav.emoji_count}")

async def get_starboard_entry(session: Session, reaction: discord.Reaction):
    stmt = select(Starboard).where(Starboard.emoji_name.like(reaction.emoji.name))
    return session.execute(stmt).scalars().first()

async def get_starboard_content_entry(
    session: Session, starboard_id: int, message_id: int
):
    stmt = select(StarboardContent).where(
        StarboardContent.starboard_id == starboard_id,
        StarboardContent.message_id == message_id,  # AJOUTÉ
    )
    return session.execute(stmt).scalars().first()

async def create_fav_embed(reaction: discord.Reaction) -> discord.Embed:
    fav_emb = discord.Embed(
        title=f"New fav : {reaction.count} {reaction.emoji}",
        description=f"{reaction.message.author.mention} - {reaction.message.channel.mention}",
        color=discord.Color.gold(),
    )
    fav_emb.set_thumbnail(url=reaction.message.author.display_avatar.url)
    fav_emb.add_field(
        name="Message", value=reaction.message.content or "No content"
    )

    fav_emb.add_field(
        name="Lien",
        value=f"[Aller au message]({reaction.message.jump_url})",
        inline=False,
    )
    if reaction.message.attachments:
        fav_emb.set_image(url=reaction.message.attachments[0].url)
        if len(reaction.message.attachments) > 1:
            fav_emb.add_field(
                name="Autres images",
                value="voir le message original pour plus d'images.",
            )
    return fav_emb
