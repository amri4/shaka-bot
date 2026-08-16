import discord
from discord.ext import commands

from utils.command import command


class ReactionRoles(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =========================================
    # CREATE
    # =========================================

    @command(
        "🔵 Reaction Roles",
        "Create a reaction-role panel"
    )
    async def rrcreate(self, ctx):

        await ctx.send(
            "✅ **rrcreate is working!**"
        )

    # =========================================
    # LIST
    # =========================================

    @command(
        "🔵 Reaction Roles",
        "Show reaction-role panels"
    )
    async def rrlist(self, ctx):

        await ctx.send(
            "✅ **rrlist is working!**"
        )

    # =========================================
    # DELETE
    # =========================================

    @command(
        "🔵 Reaction Roles",
        "Delete a reaction-role panel"
    )
    async def rrdelete(self, ctx):

        await ctx.send(
            "✅ **rrdelete is working!**"
        )


# =========================================
# SETUP
# =========================================

async def setup(bot):

    await bot.add_cog(
        ReactionRoles(bot)
    )
