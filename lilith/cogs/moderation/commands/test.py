import discord
from discord.ext import commands
from ..punishments import *
punishments = {"👢": kick, "🔇": timeout}

def get_punishment(emoji):
    if emoji in punishments:
        return punishments[emoji]
    else:
        return None

selected = set()

@commands.Cog.listener()
async def on_reaction_add(reaction, user):
    punishment = get_punishment(reaction.emoji)
    if punishment is None:
        return
    if punishment in selected:
        selected.remove(punishment)
    else:
        selected.add(punishment)
