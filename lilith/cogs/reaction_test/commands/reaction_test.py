import discord
from discord.ext import commands


class ReactionTest(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(
        self,
        payload
    ):

        print(
            "🔥 REACTION DETECTED:",
            payload.emoji,
            payload.user_id,
            payload.message_id
        )


async def setup(bot):

    await bot.add_cog(
        ReactionTest(bot)
    )
