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
    goodbye_channel_id INTEGER,
    welcome_role_id INTEGER,
    member_role_id INTEGER,
    reaction_role_channel_id INTEGER
    """
)


# =========================================
# MIGRATION
# =========================================

try:

    db.add_column(
        "server_config",
        "reaction_role_channel_id",
        "INTEGER"
    )

except Exception:

    # Column already exists.
    pass


# =========================================
# CONFIG COG
# =========================================

class Config(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

    # =====================================
    # ENSURE CONFIG
    # =====================================

    def ensure_config(
        self,
        guild_id
    ):

        if not db.exists(
            "server_config",
            "guild_id = ?",
            (guild_id,)
        ):

            db.insert(
                "server_config",
                (
                    "guild_id, "
                    "welcome_channel_id, "
                    "goodbye_channel_id, "
                    "welcome_role_id, "
                    "member_role_id, "
                    "reaction_role_channel_id"
                ),
                (
                    guild_id,
                    None,
                    None,
                    None,
                    None,
                    None
                )
            )

    # =====================================
    # WELCOME CHANNEL
    # =====================================

    @command(
        "⚙️ Configuration",
        "Set the channel used for welcome messages"
    )
    @commands.has_guild_permissions(
        manage_guild=True
    )
    async def setwelcome(
        self,
        ctx,
        channel: discord.TextChannel
    ):

        self.ensure_config(
            ctx.guild.id
        )

        db.update(
            "server_config",
            "welcome_channel_id = ?",
            "guild_id = ?",
            (
                channel.id,
                ctx.guild.id
            )
        )

        await ctx.send(
            f"👋 Welcome channel set to {channel.mention}."
        )

    # =====================================
    # REMOVE WELCOME CHANNEL
    # =====================================

    @command(
        "⚙️ Configuration",
        "Remove the configured welcome channel"
    )
    @commands.has_guild_permissions(
        manage_guild=True
    )
    async def unsetwelcome(
        self,
        ctx
    ):

        self.ensure_config(
            ctx.guild.id
        )

        db.update(
            "server_config",
            "welcome_channel_id = ?",
            "guild_id = ?",
            (
                None,
                ctx.guild.id
            )
        )

        await ctx.send(
            "✅ Welcome channel removed."
        )

    # =====================================
    # GOODBYE CHANNEL
    # =====================================

    @command(
        "⚙️ Configuration",
        "Set the channel used for goodbye messages"
    )
    @commands.has_guild_permissions(
        manage_guild=True
    )
    async def setgoodbye(
        self,
        ctx,
        channel: discord.TextChannel
    ):

        self.ensure_config(
            ctx.guild.id
        )

        db.update(
            "server_config",
            "goodbye_channel_id = ?",
            "guild_id = ?",
            (
                channel.id,
                ctx.guild.id
            )
        )

        await ctx.send(
            f"🚪 Goodbye channel set to {channel.mention}."
        )

    # =====================================
    # REMOVE GOODBYE CHANNEL
    # =====================================

    @command(
        "⚙️ Configuration",
        "Remove the configured goodbye channel"
    )
    @commands.has_guild_permissions(
        manage_guild=True
    )
    async def unsetgoodbye(
        self,
        ctx
    ):

        self.ensure_config(
            ctx.guild.id
        )

        db.update(
            "server_config",
            "goodbye_channel_id = ?",
            "guild_id = ?",
            (
                None,
                ctx.guild.id
            )
        )

        await ctx.send(
            "✅ Goodbye channel removed."
        )

    # =====================================
    # WELCOME ROLE
    # =====================================

    @command(
        "⚙️ Configuration",
        "Set the role given to new members"
    )
    @commands.has_guild_permissions(
        manage_guild=True
    )
    async def setwelcome_role(
        self,
        ctx,
        role: discord.Role
    ):

        self.ensure_config(
            ctx.guild.id
        )

        db.update(
            "server_config",
            "welcome_role_id = ?",
            "guild_id = ?",
            (
                role.id,
                ctx.guild.id
            )
        )

        await ctx.send(
            f"👋 Welcome role set to {role.mention}."
        )

    # =====================================
    # REMOVE WELCOME ROLE
    # =====================================

    @command(
        "⚙️ Configuration",
        "Remove the configured welcome role"
    )
    @commands.has_guild_permissions(
        manage_guild=True
    )
    async def unsetwelcome_role(
        self,
        ctx
    ):

        self.ensure_config(
            ctx.guild.id
        )

        db.update(
            "server_config",
            "welcome_role_id = ?",
            "guild_id = ?",
            (
                None,
                ctx.guild.id
            )
        )

        await ctx.send(
            "✅ Welcome role removed."
        )

    # =====================================
    # MEMBER ROLE
    # =====================================

    @command(
        "⚙️ Configuration",
        "Set the main member role"
    )
    @commands.has_guild_permissions(
        manage_guild=True
    )
    async def setmember_role(
        self,
        ctx,
        role: discord.Role
    ):

        self.ensure_config(
            ctx.guild.id
        )

        db.update(
            "server_config",
            "member_role_id = ?",
            "guild_id = ?",
            (
                role.id,
                ctx.guild.id
            )
        )

        await ctx.send(
            f"👤 Member role set to {role.mention}."
        )

    # =====================================
    # REMOVE MEMBER ROLE
    # =====================================

    @command(
        "⚙️ Configuration",
        "Remove the configured member role"
    )
    @commands.has_guild_permissions(
        manage_guild=True
    )
    async def unsetmember_role(
        self,
        ctx
    ):

        self.ensure_config(
            ctx.guild.id
        )

        db.update(
            "server_config",
            "member_role_id = ?",
            "guild_id = ?",
            (
                None,
                ctx.guild.id
            )
        )

        await ctx.send(
            "✅ Member role removed."
        )

    # =====================================
    # REACTION ROLE CHANNEL
    # =====================================

    @command(
        "⚙️ Configuration",
        "Set the channel used for reaction-role panels"
    )
    @commands.has_guild_permissions(
        manage_guild=True
    )
    async def setrrchannel(
        self,
        ctx,
        channel: discord.TextChannel
    ):

        self.ensure_config(
            ctx.guild.id
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
            f"🎭 Reaction-role channel set to {channel.mention}."
        )

    # =====================================
    # REMOVE REACTION ROLE CHANNEL
    # =====================================

    @command(
        "⚙️ Configuration",
        "Remove the configured reaction-role channel"
    )
    @commands.has_guild_permissions(
        manage_guild=True
    )
    async def unsetrrchannel(
        self,
        ctx
    ):

        self.ensure_config(
            ctx.guild.id
        )

        db.update(
            "server_config",
            "reaction_role_channel_id = ?",
            "guild_id = ?",
            (
                None,
                ctx.guild.id
            )
        )

        await ctx.send(
            "✅ Reaction-role channel removed."
        )

    # =====================================
    # SHOW CONFIGURATION
    # =====================================

    @command(
        "⚙️ Configuration",
        "Show this server's configuration"
    )
    @commands.has_guild_permissions(
        manage_guild=True
    )
    async def config(
        self,
        ctx
    ):

        self.ensure_config(
            ctx.guild.id
        )

        data = db.fetchone(
            "server_config",
            "guild_id = ?",
            (ctx.guild.id,)
        )

        if not data:

            await ctx.send(
                "❌ Couldn't load the server configuration."
            )

            return

        welcome_channel_id = data[1]
        goodbye_channel_id = data[2]
        welcome_role_id = data[3]
        member_role_id = data[4]
        reaction_role_channel_id = data[5]

        welcome_channel = (
            ctx.guild.get_channel(
                welcome_channel_id
            )
            if welcome_channel_id
            else None
        )

        goodbye_channel = (
            ctx.guild.get_channel(
                goodbye_channel_id
            )
            if goodbye_channel_id
            else None
        )

        welcome_role = (
            ctx.guild.get_role(
                welcome_role_id
            )
            if welcome_role_id
            else None
        )

        member_role = (
            ctx.guild.get_role(
                member_role_id
            )
            if member_role_id
            else None
        )

        reaction_role_channel = (
            ctx.guild.get_channel(
                reaction_role_channel_id
            )
            if reaction_role_channel_id
            else None
        )

        embed = discord.Embed(
            title="⚙️ Server Configuration",
            description=(
                f"Configuration for **{ctx.guild.name}**"
            ),
            color=discord.Color.blue()
        )

        embed.add_field(
            name="👋 Welcome Channel",
            value=(
                welcome_channel.mention
                if welcome_channel
                else "Not configured"
            ),
            inline=True
        )

        embed.add_field(
            name="🚪 Goodbye Channel",
            value=(
                goodbye_channel.mention
                if goodbye_channel
                else "Not configured"
            ),
            inline=True
        )

        embed.add_field(
            name="👋 Welcome Role",
            value=(
                welcome_role.mention
                if welcome_role
                else "Not configured"
            ),
            inline=True
        )

        embed.add_field(
            name="👤 Member Role",
            value=(
                member_role.mention
                if member_role
                else "Not configured"
            ),
            inline=True
        )

        embed.add_field(
            name="🎭 Reaction Role Channel",
            value=(
                reaction_role_channel.mention
                if reaction_role_channel
                else "Not configured"
            ),
            inline=True
        )

        embed.set_footer(
            text="Pythagoras • Server Configuration"
        )

        await ctx.send(
            embed=embed
        )


# =========================================
# SETUP
# =========================================

async def setup(bot):

    await bot.add_cog(
        Config(bot)
                )
