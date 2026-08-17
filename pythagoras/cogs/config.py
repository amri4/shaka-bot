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
    goodbye_channel_id,

    welcome_role_id INTEGER,
    member_role_id,

    reaction_role_channel_id,

    report_channel_id,
    case_channel_id,
    mod_log_channel_id,
    punishment_log_channel_id,
    promotion_log_channel_id,
    mod_activity_channel_id
    """
)


# =========================================
# MIGRATION
# =========================================

columns = {
    "reaction_role_channel_id": "INTEGER",
    "report_channel_id": "INTEGER",
    "case_channel_id": "INTEGER",
    "mod_log_channel_id": "INTEGER",
    "punishment_log_channel_id": "INTEGER",
    "promotion_log_channel_id": "INTEGER",
    "mod_activity_channel_id": "INTEGER"
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
                report_channel_id,
                case_channel_id,
                mod_log_channel_id,
                punishment_log_channel_id,
                promotion_log_channel_id,
                mod_activity_channel_id
                """,
                (
                    guild_id,
                    None,
                    None,
                    None,
                    None,
                    None,
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

            "report": 6,

            "cases": 7,

            "case": 7,

            "mod_log": 8,

            "punishment_log": 9,

            "punishments": 9,

            "promotion_log": 10,

            "promotions": 10,

            "mod_activity": 11,

            "activity": 11
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

    # =====================================
    # REMOVE WELCOME
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

    # =====================================
    # REMOVE GOODBYE
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

        await self.unset_channel(
            ctx,
            "reaction_role_channel_id",
            "✅ Reaction-role channel removed."
        )

    # =====================================
    # LILITH CHANNELS
    # =====================================

    @command(
        "🛡️ Lilith Configuration",
        "Set the channel where member reports are sent"
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
            "📨 Report channel set to {channel.mention}."
        )

    @command(
        "🛡️ Lilith Configuration",
        "Remove the report channel"
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
            "✅ Report channel removed."
        )

    # =====================================

    @command(
        "🛡️ Lilith Configuration",
        "Set the channel where cases are reviewed"
    )
    @commands.has_guild_permissions(
        manage_guild=True
    )
    async def setcasechannel(
        self,
        ctx,
        channel: discord.TextChannel
    ):

        await self.set_channel(
            ctx,
            "case_channel_id",
            channel,
            "⚖️ Case channel set to {channel.mention}."
        )

    @command(
        "🛡️ Lilith Configuration",
        "Remove the case channel"
    )
    @commands.has_guild_permissions(
        manage_guild=True
    )
    async def unsetcasechannel(
        self,
        ctx
    ):

        await self.unset_channel(
            ctx,
            "case_channel_id",
            "✅ Case channel removed."
        )

    # =====================================

    @command(
        "🛡️ Lilith Configuration",
        "Set the moderator log channel"
    )
    @commands.has_guild_permissions(
        manage_guild=True
    )
    async def setmodlogchannel(
        self,
        ctx,
        channel: discord.TextChannel
    ):

        await self.set_channel(
            ctx,
            "mod_log_channel_id",
            channel,
            "📋 Moderator log channel set to {channel.mention}."
        )

    @command(
        "🛡️ Lilith Configuration",
        "Remove the moderator log channel"
    )
    @commands.has_guild_permissions(
        manage_guild=True
    )
    async def unsetmodlogchannel(
        self,
        ctx
    ):

        await self.unset_channel(
            ctx,
            "mod_log_channel_id",
            "✅ Moderator log channel removed."
        )

    # =====================================

    @command(
        "🛡️ Lilith Configuration",
        "Set the punishment log channel"
    )
    @commands.has_guild_permissions(
        manage_guild=True
    )
    async def setpunishmentlog(
        self,
        ctx,
        channel: discord.TextChannel
    ):

        await self.set_channel(
            ctx,
            "punishment_log_channel_id",
            channel,
            "⚔️ Punishment log channel set to {channel.mention}."
        )

    @command(
        "🛡️ Lilith Configuration",
        "Remove the punishment log channel"
    )
    @commands.has_guild_permissions(
        manage_guild=True
    )
    async def unsetpunishmentlog(
        self,
        ctx
    ):

        await self.unset_channel(
            ctx,
            "punishment_log_channel_id",
            "✅ Punishment log channel removed."
        )

    # =====================================

    @command(
        "🛡️ Lilith Configuration",
        "Set the moderator promotion log channel"
    )
    @commands.has_guild_permissions(
        manage_guild=True
    )
    async def setpromotionlog(
        self,
        ctx,
        channel: discord.TextChannel
    ):

        await self.set_channel(
            ctx,
            "promotion_log_channel_id",
            channel,
            "🏆 Promotion log channel set to {channel.mention}."
        )

    @command(
        "🛡️ Lilith Configuration",
        "Remove the promotion log channel"
    )
    @commands.has_guild_permissions(
        manage_guild=True
    )
    async def unsetpromotionlog(
        self,
        ctx
    ):

        await self.unset_channel(
            ctx,
            "promotion_log_channel_id",
            "✅ Promotion log channel removed."
        )

    # =====================================

    @command(
        "🛡️ Lilith Configuration",
        "Set the moderator activity channel"
    )
    @commands.has_guild_permissions(
        manage_guild=True
    )
    async def setmodactivity(
        self,
        ctx,
        channel: discord.TextChannel
    ):

        await self.set_channel(
            ctx,
            "mod_activity_channel_id",
            channel,
            "📊 Moderator activity channel set to {channel.mention}."
        )

    @command(
        "🛡️ Lilith Configuration",
        "Remove the moderator activity channel"
    )
    @commands.has_guild_permissions(
        manage_guild=True
    )
    async def unsetmodactivity(
        self,
        ctx
    ):

        await self.unset_channel(
            ctx,
            "mod_activity_channel_id",
            "✅ Moderator activity channel removed."
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
            "📨 Report Channel": 6,
            "⚖️ Case Channel": 7,
            "📋 Mod Log": 8,
            "⚔️ Punishment Log": 9,
            "🏆 Promotion Log": 10,
            "📊 Mod Activity": 11
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
