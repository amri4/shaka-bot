import discord
from discord.ext import commands
import mycord

db = mycord.Bot()

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = discord.utils.get(member.guild.channels, name="🏯-〘𝗘𝗡𝗧𝗥𝗔𝗡𝗖𝗘-𝗚𝗔𝗧𝗘")
        if channel is None:
            return

        embed = discord.Embed(title="🌊 The Waves Carry a New Arrival", description=f"""**Welcome to [guild.name]**\n\n 
