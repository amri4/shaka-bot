import discord
from discord.ext import commands

import mycord
from utils.command import command


db = mycord.DB()


# =========================================
# DATABASE
# =========================================

db.create_table(
    "server_config",
    """
    guild_id INTEGER PRIMARY KEY,

    welcome_channel_id INTEGER,
    goodbye_channel_id,

    welcome_role_id INTEGER,
    member_role_id,

    reaction_role_channel_id INTEGER,
    report_channel_id INTEGER
    """
)


# =========================================
# MIGRATION
# =========================================

columns = {
    "reaction_role_channel_id": "INTEGER",
    "report_channel_id": "INTEGER"
}


for column, column_type in columns.items():

    try:

        db.add_column(
            "server_config",
            column,
            column_type
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
                """
                guild_id,
                welcome_channel_id,
                goodbye_channel_id,
                welcome_role_id,
                member_role_id,
                reaction_role_channel_id,
                report_channel_id
                """,
                (
                    guild_id,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None
                )
            )


    # =====================================
    # GET CONFIG
    # =====================================

    def get_config(
        self,
        guild_id
    ):

        self.ensure_config(
            guild_id
        )

        return db.fetchone(
            "server_config",
            "guild_id = ?",
            (guild_id,)
        )


    # =====================================
    # GET CONFIGURED CHANNEL
    # =====================================

    def get_channel(
        self,
        guild,
        channel_type
    ):

        data = self.get_config(
            guild.id
        )

        if not data:
            return None

        channel_map = {

            "welcome": 1,
            "goodbye": 2,
            "reaction_role": 5,
            "reports": 6,
            "report": 6
        }

        index = channel_map.get(
            channel_type.lower()
        )

        if index is None:
            return None

        channel_id = data[index]

        if not channel_id:
            return None

        return guild.get_channel(
            channel_id
        )


    # =====================================
    # GET CONFIGURED ROLE
    # =====================================

    def get_role(
        self,
        guild,
        role_type
    ):

        data = self.get_config(
            guild.id
        )

        if not data:
            return None

        role_map = {

            "welcome": 3,
            "member": 4
        }

        index = role_map.get(
            role_type.lower()
        )

        if index is None:
            return None

        role_id = data[index]

        if not role_id:
            return None

        return guild.get_role(
            role_id
        )


    # =====================================
    # SET CHANNEL HELPER
    # =====================================

    async def set_channel(
        self,
        ctx,
        column,
        channel,
        message
    ):

        self.ensure_config(
            ctx.guild.id
        )

        db.update(
            "server_config",
            f"{column} = ?",
            "guild_id = ?",
            (
                channel.id,
                ctx.guild.id
            )
        )

        await ctx.send(
            message.format(
                channel=channel
            )
        )


    # =====================================
    # REMOVE CHANNEL HELPER
    # =====================================

    async def unset_channel(
        self,
        ctx,
        column,
        message
    ):

        self.ensure_config(
            ctx.guild.id
        )

        db.update(
            "server_config",
            f"{column} = ?",
            "guild_id = ?",
            (
                None,
                ctx.guild.id
            )
        )

        await ctx.send(
            message
        )


    # =====================================
    # SET ROLE HELPER
    # =====================================

    async def set_role(
        self,
        ctx,
        column,
        role,
        message
    ):

        self.ensure_config(
            ctx.guild.id
        )

        db.update(
            "server_config",
            f"{column} = ?",
            "guild_id = ?",
            (
                role.id,
                ctx.guild.id
            )
        )

        await ctx.send(
            message.format(
                role=role
            )
        )


    # =====================================
    # REMOVE ROLE HELPER
    # =====================================

    async def unset_role(
        self,
        ctx,
        column,
        message
    ):

        self.ensure_config(
            ctx.guild.id
        )

        db.update(
            "server_config",
            f"{column} = ?",
            "guild_id = ?"
        )

        await ctx.send(
            message
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

        await self.set_channel(
            ctx,
            "welcome_channel_id",
            channel,
            "👋 Welcome channel set to {channel.mention}."
        )


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

        await self.unset_channel(
            ctx,
            "welcome_channel_id",
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

        await self.set_channel(
            ctx,
            "goodbye_channel_id",
            channel,
            "🚪 Goodbye channel set to {channel.mention}."
        )


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

        await self.unset_channel(
            ctx,
            "goodbye_channel_id",
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

        await self.set_role(
            ctx,
            "welcome_role_id",
            role,
            "👋 Welcome role set to {role.mention}."
        )


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

        await self.unset_role(
            ctx,
            "welcome_role_id",
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

        await self.set_role(
            ctx,
            "member_role_id",
            role,
            "👤 Member role set to {role.mention}."
        )


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

        await self.unset_role(
            ctx,
            "member_role_id",
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

        await self.set_channel(
            ctx,
            "reaction_role_channel_id",
            channel,
            "🎭 Reaction-role channel set to {channel.mention}."
        )


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

        await self.unset_channel(
            ctx,
            "reaction_role_channel_id",
            "✅ Reaction-role channel removed."
        )


    # =====================================
    # REPORT CHANNEL
    # =====================================

    @command(
        "⚙️ Configuration",
        "Set the channel where reports are sent to mods"
    )
    @commands.has_guild_permissions(
        manage_guild=True
    )
    async def setreportchannel(
        self,
        ctx,
        channel: discord.TextChannel
    ):

        await self.set_channel(
            ctx,
            "report_channel_id",
            channel,
            "📨 Reports channel set to {channel.mention}."
        )


    @command(
        "⚙️ Configuration",
        "Remove the configured reports channel"
    )
    @commands.has_guild_permissions(
        manage_guild=True
    )
    async def unsetreportchannel(
        self,
        ctx
    ):

        await self.unset_channel(
            ctx,
            "report_channel_id",
            "✅ Reports channel removed."
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

        data = self.get_config(
            ctx.guild.id
        )

        if not data:

            await ctx.send(
                "❌ Couldn't load the server configuration."
            )

            return

        channel_names = {

            "👋 Welcome Channel": 1,
            "🚪 Goodbye Channel": 2,
            "🎭 Reaction Role Channel": 5,
            "📨 Report Channel": 6
        }

        role_names = {

            "👋 Welcome Role": 3,
            "👤 Member Role": 4
        }

        embed = discord.Embed(
            title="⚙️ Server Configuration",
            description=(
                f"Configuration for **{ctx.guild.name}**"
            ),
            color=discord.Color.blue()
        )

        for name, index in channel_names.items():

            channel_id = data[index]

            channel = (
                ctx.guild.get_channel(
                    channel_id
                )
                if channel_id
                else None
            )

            embed.add_field(
                name=name,
                value=(
                    channel.mention
                    if channel
                    else "Not configured"
                ),
                inline=True
            )

        for name, index in role_names.items():

            role_id = data[index]

            role = (
                ctx.guild.get_role(
                    role_id
                )
                if role_id
                else None
            )

            embed.add_field(
                name=name,
                value=(
                    role.mention
                    if role
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
