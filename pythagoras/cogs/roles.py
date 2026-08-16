import discord
from discord.ext import commands

from utils.command import command


# =========================================
# ROLE CONVERTER
# =========================================

class RoleConverter(commands.Converter):

    async def convert(self, ctx, argument):

        # Remove role mention formatting if supplied
        if argument.startswith("<@&") and argument.endswith(">"):
            argument = argument[3:-1]

        # Try role ID
        if argument.isdigit():

            role = ctx.guild.get_role(
                int(argument)
            )

            if role:
                return role

        # Try exact role name
        role = discord.utils.find(
            lambda r: (
                r.name.lower() == argument.lower()
            ),
            ctx.guild.roles
        )

        if role:
            return role

        raise commands.BadArgument(
            "Role not found."
        )


class Roles(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =========================================
    # CREATE ROLE
    # =========================================

    @command("🔵 Roles", "Create a new server role")
    @commands.has_guild_permissions(manage_roles=True)
    async def addrole(self, ctx, *, name: str):

        role = await ctx.guild.create_role(
            name=name,
            reason=f"Created by {ctx.author}"
        )

        await ctx.send(
            f"✅ Created role **{role.name}**."
        )

    # =========================================
    # DELETE ROLE
    # =========================================

    @command("🔵 Roles", "Delete a server role")
    @commands.has_guild_permissions(manage_roles=True)
    async def delrole(
        self,
        ctx,
        role: RoleConverter
    ):

        if role == ctx.guild.default_role:

            await ctx.send(
                "❌ I can't delete @everyone."
            )
            return

        if role >= ctx.guild.me.top_role:

            await ctx.send(
                "❌ I can't delete that role because "
                "it's higher than or equal to my highest role."
            )
            return

        role_name = role.name

        await role.delete(
            reason=f"Deleted by {ctx.author}"
        )

        await ctx.send(
            f"🗑️ Deleted role **{role_name}**."
        )

    # =========================================
    # EDIT ROLE
    # =========================================

    @command("🔵 Roles", "Rename an existing server role")
    @commands.has_guild_permissions(manage_roles=True)
    async def editrole(
        self,
        ctx,
        role: RoleConverter,
        *,
        name: str
    ):

        if role == ctx.guild.default_role:

            await ctx.send(
                "❌ I can't edit @everyone."
            )
            return

        if role >= ctx.guild.me.top_role:

            await ctx.send(
                "❌ I can't edit that role because "
                "it's higher than or equal to my highest role."
            )
            return

        old_name = role.name

        await role.edit(
            name=name,
            reason=f"Edited by {ctx.author}"
        )

        await ctx.send(
            f"✏️ Renamed **{old_name}** → "
            f"**{role.name}**."
        )

    # =========================================
    # LIST ROLES
    # =========================================

    @command("🔵 Roles", "Show all server roles")
    async def roles(self, ctx):

        roles = [
            role
            for role in ctx.guild.roles
            if role != ctx.guild.default_role
        ]

        if not roles:

            await ctx.send(
                "❌ This server has no custom roles."
            )
            return

        roles.reverse()

        text = "\n".join(
            f"• **{role.name}**"
            for role in roles
        )

        embed = discord.Embed(
            title="🔵 Server Roles",
            description=text,
            color=discord.Color.blue()
        )

        embed.set_footer(
            text=f"{len(roles)} roles"
        )

        await ctx.send(
            embed=embed
        )

    # =========================================
    # MOVE ROLE
    # =========================================

    @command(
        "🔵 Roles",
        "Move a role above or below another role"
    )
    @commands.has_guild_permissions(manage_roles=True)
    async def moverole(
        self,
        ctx,
        role: RoleConverter,
        position: str,
        target: RoleConverter
    ):

        # =====================================
        # BASIC CHECKS
        # =====================================

        if role == ctx.guild.default_role:

            await ctx.send(
                "❌ I can't move @everyone."
            )
            return

        if target == ctx.guild.default_role:

            await ctx.send(
                "❌ You can't move a role "
                "relative to @everyone."
            )
            return

        if role == target:

            await ctx.send(
                "❌ The two roles must be different."
            )
            return

        # =====================================
        # POSITION CHECK
        # =====================================

        position = position.lower()

        if position not in (
            "above",
            "below"
        ):

            await ctx.send(
                "❌ Position must be "
                "`above` or `below`."
            )
            return

        # =====================================
        # BOT HIERARCHY
        # =====================================

        bot_role = ctx.guild.me.top_role

        if role >= bot_role:

            await ctx.send(
                "❌ I can't move that role because "
                "it's higher than or equal to my "
                "highest role."
            )
            return

        if target >= bot_role:

            await ctx.send(
                "❌ I can't move a role relative to "
                "a role that's higher than or equal "
                "to my highest role."
            )
            return

        # =====================================
        # MOVE
        # =====================================

        if position == "above":

            new_position = target.position + 1

        else:

            new_position = target.position - 1

        # Prevent invalid position
        new_position = max(
            1,
            min(
                new_position,
                bot_role.position - 1
            )
        )

        await role.edit(
            position=new_position,
            reason=f"Moved by {ctx.author}"
        )

        await ctx.send(
            f"↕️ Moved **{role.name}** "
            f"**{position}** **{target.name}**."
        )

    # =========================================
    # ERROR HANDLING
    # =========================================

    @commands.Cog.listener()
    async def on_command_error(
        self,
        ctx,
        error
    ):

        if isinstance(
            error,
            commands.MissingPermissions
        ):

            await ctx.send(
                "❌ You need **Manage Roles** "
                "to use this command."
            )

        elif isinstance(
            error,
            commands.BadArgument
        ):

            await ctx.send(
                "❌ I couldn't find that role."
            )


# =========================================
# SETUP
# =========================================

async def setup(bot):

    await bot.add_cog(
        Roles(bot)
        )
