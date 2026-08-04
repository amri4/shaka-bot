import discord
import random
from discord.ext import commands


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    welcome_titles = [
        "📜 A New Chapter Begins",
        "🌊 A New Soul Arrives",
        "⚓ A New Journey Starts",
        "🌅 A New Dawn Rises",
        "🏝️ A New Arrival Reaches The Seas",
        "✨ Another Story Unfolds",
        "📖 A New Legend Begins",
        "🚢 The Voyage Expands",
        "🌎 A New Name Enters The World",
        "⚔️ A New Path Awaits"
    ]

    welcome_messages = [
        "The world is vast, and everyone has a role to play. Your journey, your choices, and your legacy are yours to create.",
        
        "Every island holds mysteries, every person has a dream. The path you choose will shape the story you leave behind.",
        
        "From the East Blue to the New World, countless stories are waiting to be written. Yours begins now.",
        
        "The seas are filled with opportunities, dangers, and unforgettable encounters. What will your future hold?",
        
        "A new name has entered the world. Whether you seek adventure, justice, freedom, or something else, your journey is yours.",
        
        "The world is constantly changing. New alliances will form, rivalries will rise, and legends will be born.",
        
        "Every great story starts with a single step. Take yours and discover where the waves will lead you.",
        
        "Beyond the horizon lies a world full of possibilities. Your actions will decide the path you follow.",
        
        "The Grand Line welcomes another soul. Your dreams, goals, and decisions will define your adventure.",
        
        "No matter where your path leads, every choice creates a new chapter in this endless sea of stories."
    ]

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = discord.utils.get(member.guild.channels, name="🏯-〘𝗘𝗡𝗧𝗥𝗔𝗡𝗖𝗘-𝗚𝗔𝗧𝗘〙")

        if channel is None:
            return

        embed = discord.Embed(
            title=random.choice(self.welcome_titles),
            description=f"""
Welcome {member.mention}!

{random.choice(self.welcome_messages)}

🌊 The seas await your arrival.
""",
            color=discord.Color.blue()
        )

        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Welcome to {member.guild.name}")

        await channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Welcome(bot))
