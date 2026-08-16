import discord
from discord.ext import commands

import mycord
from utils.command import command


db = mycord.PunksDB()


class Config(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =====================================
    # SET REACTION ROLE CHANNEL
    # =====================================

    @command(
        "⚙️ Configuration",
        "Set the channel used for reaction-role panels"
    )
    async def setrrchannel(
        self,
        ctx,
        channel: discord.TextChannel
    ):

        try:

            await ctx.send(
                "🔧 `setrrchannel` started..."
            )

            data = db.fetchone(
                "server_config",
                "guild_id = ?",
                (ctx.guild.id,)
            )

            if not data:

                await ctx.send(
                    "❌ No `server_config` row exists "
                    "for this server."
                )

                return

            await ctx.send(
                "✅ Found server configuration.\n"
                f"Current data: `{data}`"
            )

            await ctx.send(
                "🔧 Trying to update the database..."
            )

            db.update(
                "server_config",
                "reaction_role_channel_id = ?",
                "guild_id = ?",
                (
                    channel.id,
                    ctx.guild.id
                )
            )

            await ctx.send(
                f"✅ Reaction-role channel set to "
                f"{channel.mention}."
            )

        except Exception as error:

            await ctx.send(
                "❌ **setrrchannel error:**\n"
                f"```py\n{type(error).__name__}: {error}\n```"
            )

    # =====================================
    # TEST CONFIG
    # =====================================

    @command(
        "⚙️ Configuration",
        "Test the server configuration database"
    )
    async def configtest(
        self,
        ctx
    ):

        try:

            data = db.fetchone(
                "server_config",
                "guild_id = ?",
                (ctx.guild.id,)
            )

            await ctx.send(
                "✅ Database test succeeded.\n\n"
                f"```py\n{data}\n```"
            )

        except Exception as error:

            await ctx.send(
                "❌ **Database error:**\n"
                f"```py\n{type(error).__name__}: {error}\n```"
            )


# =========================================
# SETUP
# =========================================

async def setup(bot):

    await bot.add_cog(
        Config(bot)
        )
