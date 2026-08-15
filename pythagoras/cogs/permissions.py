import discord
from discord.ext import commands

from utils.command import command


class Permissions(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =========================================
    # ALLOW ROLE IN CHANNEL
    # =========================================

    @command(
        "🔐 Permissions",
        "Allow a role to access a channel"
    )
    @commands.has_guild_permissions(manage_channels=True)
    async def allow(
        self,
        ctx,
        channel: discord.TextChannel,
        role: discord.Role
    ):

        await channel.set_permissions(
            role,
            view_channel=True,
            send_messages=True,
            reason=f"Permission changed by {ctx.author}"
        )

        await ctx.send(
            f"✅ {role.mention} can now access "
            f"{channel.mention}."
        )

    # =========================================
    # DENY ROLE IN CHANNEL
    # =========================================

    @command(
        "🔐 Permissions",
        "Deny a role access to a channel"
    )
    @commands.has_guild_permissions(manage_channels=True)
    async def deny(
        self,
        ctx,
        channel: discord.TextChannel,
        role: discord.Role
    ):

        await channel.set_permissions(
            role,
            view_channel=False,
            send_messages=False,
            reason=f"Permission changed by {ctx.author}"
        )

        await ctx.send(
            f"🚫 {role.mention} can no longer access "
            f"{channel.mention}."
        )

    # =========================================
    # RESET ROLE PERMISSIONS
    # =========================================

    @command(
        "🔐 Permissions",
        "Reset a role's permissions in a channel"
    )
    @commands.has_guild_permissions(manage_channels=True)
    async def resetperm(
        self,
        ctx,
        channel: discord.TextChannel,
        role: discord.Role
    ):

        await channel.set_permissions(
            role,
            overwrite=None,
            reason=f"Permissions reset by {ctx.author}"
        )

        await ctx.send(
            f"🔄 Reset {role.mention}'s permissions "
            f"in {channel.mention}."
        )


# =========================================
# SETUP
# =========================================

async def setup(bot):
    await bot.add_cog(Permissions(bot))
