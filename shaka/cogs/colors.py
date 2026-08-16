import discord
from discord.ext import commands

from utils.command import command
from utils.role_colors import ROLE_COLORS


# =========================================
# COLORS COG
# =========================================

class Colors(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

    # =====================================
    # SETUP COLOR ROLES
    # =====================================

    @command(
        "🎨 Colors",
        "Create the Discord roles used to preview Shaka's colors"
    )
    @commands.has_guild_permissions(
        manage_roles=True
    )
    async def setupcolors(
        self,
        ctx
    ):

        created = 0
        existing = 0

        # ---------------------------------
        # BOT MEMBER
        # ---------------------------------

        bot_member = ctx.guild.me

        if not bot_member:

            await ctx.send(
                "❌ I couldn't find my server member."
            )

            return

        # ---------------------------------
        # BOT PERMISSION
        # ---------------------------------

        if not bot_member.guild_permissions.manage_roles:

            await ctx.send(
                "❌ I need **Manage Roles** "
                "to create the color roles."
            )

            return

        # ---------------------------------
        # CREATE / UPDATE ROLES
        # ---------------------------------

        for name, value in ROLE_COLORS.items():

            role_name = name.title()

            # Find existing role
            role = discord.utils.find(
                lambda r:
                    r.name.lower() == role_name.lower(),
                ctx.guild.roles
            )

            # -----------------------------
            # EXISTING ROLE
            # -----------------------------

            if role:

                existing += 1

                # Update color if necessary
                if role.color.value != value:

                    try:

                        await role.edit(
                            color=discord.Color(
                                value
                            ),
                            reason=(
                                "Updating Shaka "
                                "color role"
                            )
                        )

                    except discord.Forbidden:

                        pass

                continue

            # -----------------------------
            # CREATE ROLE
            # -----------------------------

            try:

                await ctx.guild.create_role(
                    name=role_name,
                    color=discord.Color(
                        value
                    ),
                    reason=(
                        f"Shaka color role: "
                        f"{name}"
                    )
                )

                created += 1

            except discord.Forbidden:

                await ctx.send(
                    "❌ I lost permission to "
                    "create roles."
                )

                return

        # ---------------------------------
        # RESULT
        # ---------------------------------

        await ctx.send(
            "🎨 **Color roles are ready!**\n\n"
            f"Created: **{created}**\n"
            f"Already existed: **{existing}**"
        )

    # =====================================
    # SHOW COLORS
    # =====================================

    @command(
        "🎨 Colors",
        "Show all available profile colors"
    )
    async def colors(
        self,
        ctx
    ):

        lines = []

        # ---------------------------------
        # FIND ROLES
        # ---------------------------------

        for name in ROLE_COLORS:

            role_name = name.title()

            role = discord.utils.find(
                lambda r:
                    r.name.lower() == role_name.lower(),
                ctx.guild.roles
            )

            if role:

                lines.append(
                    f"{role.mention} "
                    f"`{name}`"
                )

            else:

                lines.append(
                    f"🎨 **{name.title()}**"
                )

        # ---------------------------------
        # SPLIT INTO DISCORD-SAFE CHUNKS
        # ---------------------------------

        chunks = []
        current = ""

        for line in lines:

            if len(current) + len(line) + 1 > 4000:

                chunks.append(
                    current
                )

                current = ""

            current += line + "\n"

        if current:

            chunks.append(
                current
            )

        # ---------------------------------
        # SEND EMBEDS
        # ---------------------------------

        for index, chunk in enumerate(
            chunks
        ):

            if index == 0:

                description = (
                    "Choose a color to use "
                    "for your profile embed.\n\n"
                    "**Usage**\n"
                    "`Shaka profilecolor <color>`\n\n"
                    + chunk
                )

                embed = discord.Embed(
                    title="🎨 Shaka Profile Colors",
                    description=description,
                    color=discord.Color.blue()
                )

            else:

                embed = discord.Embed(
                    description=chunk,
                    color=discord.Color.blue()
                )

            embed.set_footer(
                text=(
                    f"{len(ROLE_COLORS)} "
                    "available colors"
                )
            )

            await ctx.send(
                embed=embed
            )

    # =====================================
    # SETUP COLORS ERROR
    # =====================================

    @setupcolors.error
    async def setupcolors_error(
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
                "to set up the color roles."
            )


# =========================================
# SETUP
# =========================================

async def setup(bot):

    await bot.add_cog(
        Colors(bot)
    )
