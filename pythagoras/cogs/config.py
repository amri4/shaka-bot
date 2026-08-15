import discord
from discord.ext import commands

import mycord
from utils.command import command


db = mycord.PunksDB()


# =========================================
# DATABASE
# =========================================

db.create_table(
    "server_config",
    """
    guild_id INTEGER PRIMARY KEY,
    welcome_channel_id INTEGER,
    goodbye_channel_id INTEGER
    """
)


# =========================================
# CONFIG COG
# =========================================

class Config(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =====================================
    # MAKE SURE SERVER HAS CONFIG
    # =====================================

    def ensure_config(self, guild_id):

        if not db.exists(
            "server_config",
            "guild_id = ?",
            (guild_id,)
        ):

            db.insert(
                "server_config",
                "guild_id, welcome_channel_id, goodbye_channel_id",
                (guild_id, None, None)
            )

    # =====================================
    # SET WELCOME CHANNEL
    # =====================================

    @command(
        "⚙️ Configuration",
        "Set the channel used for welcome messages"
    )
    @commands.has_guild_permissions(manage_guild=True)
    async def setwelcome(
        self,
        ctx,
        channel: discord.TextChannel
    ):

        self.ensure_config(ctx.guild.id)

        db.update(
            "server_config",
            "welcome_channel_id = ?",
            "guild_id = ?",
            (channel.id, ctx.guild.id)
        )

        await ctx.send(
            f"👋 Welcome channel set to {channel.mention}."
        )

    # =====================================
    # SET GOODBYE CHANNEL
    # =====================================

    @command(
        "⚙️ Configuration",
        "Set the channel used for goodbye messages"
    )
    @commands.has_guild_permissions(manage_guild=True)
    async def setgoodbye(
        self,
        ctx,
        channel: discord.TextChannel
    ):

        self.ensure_config(ctx.guild.id)

        db.update(
            "server_config",
            "goodbye_channel_id = ?",
            "guild_id = ?",
            (channel.id, ctx.guild.id)
        )

        await ctx.send(
            f"🚪 Goodbye channel set to {channel.mention}."
        )

    # =====================================
    # SHOW CONFIGURATION
    # =====================================

    @command(
        "⚙️ Configuration",
        "Show the current server configuration"
    )
    @commands.has_guild_permissions(manage_guild=True)
    async def config(self, ctx):

        self.ensure_config(ctx.guild.id)

        data = db.fetchone(
            "server_config",
            "guild_id = ?",
            (ctx.guild.id,)
        )

        welcome_id = data[1]
        goodbye_id = data[2]

        welcome = (
            ctx.guild.get_channel(welcome_id)
            if welcome_id
            else None
        )

        goodbye = (
            ctx.guild.get_channel(goodbye_id)
            if goodbye_id
            else None
        )

        embed = discord.Embed(
            title="⚙️ Server Configuration",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="👋 Welcome Channel",
            value=welcome.mention if welcome else "Not configured",
            inline=False
        )

        embed.add_field(
            name="🚪 Goodbye Channel",
            value=goodbye.mention if goodbye else "Not configured",
            inline=False
        )

        await ctx.send(embed=embed)


# =========================================
# SETUP
# =========================================

async def setup(bot):
    await bot.add_cog(Config(bot))
