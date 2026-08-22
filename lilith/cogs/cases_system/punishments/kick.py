import discord
from utils.discord_setup import *

NAME = "kick"
EMOJI = "👢"
REQUIRES_INPUT = False

async def apply(guild, member):
  await member.kick()
  return True
