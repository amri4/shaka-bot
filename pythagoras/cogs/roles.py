import discord
import unicodedata

from discord.ext import commands

from utils.command import command
from utils.role_colors import parse_role_color


# =========================================
# ROLE NAME NORMALIZER
# =========================================

def normalize_role_name(text):

    text = unicodedata.normalize(
        "NFKC",
        text
    )

    return text.casefold().strip()


# =========================================
# ROLE CONVERTER
# =========================================

class RoleConverter(commands.Converter):

    async def convert(self, ctx, argument):

        # =====================================
        # ROLE MENTION
        # =====================================

        if argument.startswith("<@&") and argument.endswith(">"):

            argument = argument[3:-1]

        # =====================================
        # ROLE ID
        # =====================================

        if argument.isdigit():

            role = ctx.guild.get_role(
                int(argument)
            )

            if role:
                return role

        # =====================================
        # NORMALIZED SEARCH
        # =====================================

        search = normalize_role_name(
            argument
        )

        # =====================================
        # EXACT MATCH
        # =====================================

        for role in ctx.guild.roles:

            if normalize_role_name(
                role.name
            ) == search:

                return role

        # =====================================
        # PARTIAL MATCH
        # =====================================

        matches = [
            role
            for role in ctx.guild.roles
            if search in normalize_role_name(
                role.name
            )
        ]

        if len(matches) == 1:

            return matches[0]

        if matches:

            names = "\n".join(
                f"• {role.mention}"
                for role in matches[:10]
            )

            raise commands.BadArgument(
                "Multiple roles found:\n"
                + names
            )

        raise commands.BadArgument(
            "Role not found."
        )


# =========================================
# MEMBER CONVERTER
# =========================================

class MemberConverter(commands.Converter):

    async def convert(self, ctx, argument):

        try:

            return await commands.MemberConverter().convert(
                ctx,
                argument
            )

        except commands.BadArgument:

            raise commands.BadArgument(
                "Member not found."
            )


# =========================================
# ROLES COG
# =========================================

class Roles(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =========================================
    # CREATE ROLE
    # =========================================

    @command(
        "🔵 Roles",
        "Create a new server role"
    )
    @commands.has_guild_permissions(
        manage_roles=True
    )
    async def addrole(
        self,
        ctx,
        *,
        name: str
    ):

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

    @command(
        "🔵 Roles",
        "Delete a server role"
    )
    @commands.has_guild_permissions(
        manage_roles=True
    )
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
                "it's higher than or equal to my "
                "highest role."
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

    @command(
        "🔵 Roles",
        "Rename an existing server role"
    )
    @commands.has_guild_permissions(
        manage_roles=True
    )
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
                "it's higher than or equal to my "
                "highest role."
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

    @command(
        "🔵 Roles",
        "Show all server roles"
    )
    async def roles(
        self,
        ctx
    ):

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

        # Actual clickable role mentions
        text = "\n".join(
            f"• {role.mention}"
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
    # ROLE SEARCH
    # =========================================

    @command(
        "🔵 Roles",
        "Search for server roles"
    )
    async def rolesearch(
        self,
        ctx,
        *,
        search: str
    ):

        search = normalize_role_name(
            search
        )

        matches = [
            role
            for role in ctx.guild.roles
            if role != ctx.guild.default_role
            and search in normalize_role_name(
                role.name
            )
        ]

        if not matches:

            await ctx.send(
                "❌ No roles found matching "
                f"**{search}**."
            )
            return

        matches = matches[:25]

        # Actual clickable role mentions
        text = "\n".join(
            f"• {role.mention}"
            for role in matches
        )

        embed = discord.Embed(
            title="🔎 Role Search",
            description=text,
            color=discord.Color.blue()
        )

        embed.set_footer(
            text=f"{len(matches)} result(s)"
        )

        await ctx.send(
            embed=embed
        )

    # =========================================
    # GIVE ROLE
    # =========================================

    @command(
        "🔵 Roles",
        "Give a role to a member"
    )
    @commands.has_guild_permissions(
        manage_roles=True
    )
    async def giverole(
        self,
        ctx,
        member: MemberConverter,
        role: RoleConverter
    ):

        if role == ctx.guild.default_role:

            await ctx.send(
                "❌ I can't assign @everyone."
            )
            return

        if role >= ctx.guild.me.top_role:

            await ctx.send(
                "❌ I can't assign that role because "
                "it's higher than or equal to my "
                "highest role."
            )
            return

        if role in member.roles:

            await ctx.send(
                f"❌ {member.mention} already has "
                f"{role.mention}."
            )
            return

        await member.add_roles(
            role,
            reason=f"Role given by {ctx.author}"
        )

        await ctx.send(
            f"✅ Added {role.mention} to "
            f"{member.mention}."
        )

    # =========================================
    # TAKE ROLE
    # =========================================

    @command(
        "🔵 Roles",
        "Remove a role from a member"
    )
    @commands.has_guild_permissions(
        manage_roles=True
    )
    async def takerole(
        self,
        ctx,
        member: MemberConverter,
        role: RoleConverter
    ):

        if role == ctx.guild.default_role:

            await ctx.send(
                "❌ I can't remove @everyone."
            )
            return

        if role >= ctx.guild.me.top_role:

            await ctx.send(
                "❌ I can't remove that role because "
                "it's higher than or equal to my "
                "highest role."
            )
            return

        if role not in member.roles:

            await ctx.send(
                f"❌ {member.mention} doesn't have "
                f"{role.mention}."
            )
            return

        await member.remove_roles(
            role,
            reason=f"Role removed by {ctx.author}"
        )

        await ctx.send(
            f"✅ Removed {role.mention} from "
            f"{member.mention}."
        )

    # =========================================
    # MOVE ROLE
    # =========================================

    @command(
        "🔵 Roles",
        "Move a role above or below another role"
    )
    @commands.has_guild_permissions(
        manage_roles=True
    )
    async def moverole(
        self,
        ctx,
        role: RoleConverter,
        position: str,
        target: RoleConverter
    ):

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

        if position == "above":

            new_position = target.position + 1

        else:

            new_position = target.position - 1

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
            f"↕️ Moved {role.mention} "
            f"**{position}** {target.mention}."
        )

    # =========================================
    # SET ROLE COLOR
    # =========================================

    @command(
        "🔵 Roles",
        "Change the color of a server role"
    )
    @commands.has_guild_permissions(
        manage_roles=True
    )
    async def setrolecolor(
        self,
        ctx,
        role: RoleConverter,
        color: str
    ):

        if role == ctx.guild.default_role:

            await ctx.send(
                "❌ I can't change the color "
                "of @everyone."
            )
            return

        if role >= ctx.guild.me.top_role:

            await ctx.send(
                "❌ I can't change that role because "
                "it's higher than or equal to my "
                "highest role."
            )
            return

        parsed_color = parse_role_color(
            color
        )

        if parsed_color is None:

            await ctx.send(
                "❌ Invalid color.\n\n"
                "Use a color name such as "
                "`red`, `crimson`, `cyan`, "
                "`gold`, `lavender`, etc.\n\n"
                "Or use a hex code such as "
                "`#5865F2`."
            )
            return

        await role.edit(
            color=discord.Color(parsed_color),
            reason=f"Color changed by {ctx.author}"
        )

        await ctx.send(
            f"🎨 Changed {role.mention} "
            f"to `{color}`."
        )

    # =========================================
    # RESET ROLE COLOR
    # =========================================

    @command(
        "🔵 Roles",
        "Reset a server role's color"
    )
    @commands.has_guild_permissions(
        manage_roles=True
    )
    async def resetrolecolor(
        self,
        ctx,
        role: RoleConverter
    ):

        if role == ctx.guild.default_role:

            await ctx.send(
                "❌ I can't change the color "
                "of @everyone."
            )
            return

        if role >= ctx.guild.me.top_role:

            await ctx.send(
                "❌ I can't change that role because "
                "it's higher than or equal to my "
                "highest role."
            )
            return

        await role.edit(
            color=discord.Color.default(),
            reason=f"Color reset by {ctx.author}"
        )

        await ctx.send(
            f"🎨 Reset the color of "
            f"{role.mention}."
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
                f"❌ {error}"
            )


# =========================================
# SETUP
# =========================================

async def setup(bot):

    await bot.add_cog(
        Roles(bot)
        )
