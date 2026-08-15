import discord
from discord.ext import commands

from utils.command import command


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
            f"✅ Created role {role.mention}"
        )

    # =========================================
    # DELETE ROLE
    # =========================================

    @command("🔵 Roles", "Delete a server role")
    @commands.has_guild_permissions(manage_roles=True)
    async def delrole(self, ctx, role: discord.Role):

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
        role: discord.Role,
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
            f"✏️ Renamed **{old_name}** → **{role.mention}**"
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

        await ctx.send(embed=embed)


# =========================================
# ERROR HANDLING
# =========================================

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                "❌ You need **Manage Roles** to use this command."
            )


# =========================================
# SETUP
# =========================================

async def setup(bot):
    await bot.add_cog(Roles(bot))
