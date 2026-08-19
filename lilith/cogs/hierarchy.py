import discord
from discord.ext import commands

import utils.hierarchy as hierarchy

from utils.command import command


class Hierarchy(commands.Cog):

    def __init__(
        self,
        bot
    ):

        self.bot = bot

    # =====================================================
    # READY
    # =====================================================

    @commands.Cog.listener()
    async def on_ready(
        self
    ):

        for guild in self.bot.guilds:

            try:

                await hierarchy.ensure_roles(
                    guild,
                    guild.me
                )

            except Exception as error:

                print(
                    f"[Hierarchy] "
                    f"{guild.name}: {error}"
                )

    # =====================================================
    # GUILD JOIN
    # =====================================================

    @commands.Cog.listener()
    async def on_guild_join(
        self,
        guild
    ):

        await hierarchy.ensure_roles(
            guild,
            guild.me
        )

    # =====================================================
    # MEMBER JOIN
    # =====================================================

    @commands.Cog.listener()
    async def on_member_join(
        self,
        member
    ):

        if member.bot:
            return

        try:

            await hierarchy.ensure_roles(
                member.guild,
                member.guild.me
            )

            member_role = hierarchy.get_role(
                member.guild,
                hierarchy.RANKS["MEMBER"]
            )

            if member_role:

                await member.add_roles(
                    member_role,
                    reason="Hierarchy system"
                )

        except (
            discord.Forbidden,
            discord.HTTPException
        ):

            pass

    # =====================================================
    # HIERARCHY
    # =====================================================

    @command(
        "🛡️ Hierarchy",
        "Show the server staff hierarchy"
    )
    async def hierarchy(
        self,
        ctx
    ):

        embed = discord.Embed(
            title="🛡️ Staff Team",
            description=(
                f"Staff hierarchy for "
                f"**{ctx.guild.name}**"
            ),
            color=discord.Color.blue()
        )

        # Highest → lowest staff rank.

        for rank in range(
            hierarchy.RANKS["OWNER"],
            hierarchy.RANKS["TRAINEE"] - 1,
            -1
        ):

            members = [
                member
                for member in ctx.guild.members
                if not member.bot
                and hierarchy.get_rank(member) == rank
            ]

            if members:

                members.sort(
                    key=lambda member:
                    member.display_name.lower()
                )

                value = "\n".join(
                    member.mention
                    for member in members
                )

            else:

                value = "*No members*"

            embed.add_field(
                name=hierarchy.RANK_NAMES[rank],
                value=value,
                inline=False
            )

        embed.set_footer(
            text="Lilith • Staff Hierarchy"
        )

        await ctx.send(
            embed=embed
        )

    # =====================================================
    # RANK
    # =====================================================

    @command(
        "🛡️ Hierarchy",
        "Show a member's rank",
        usage="[member]"
    )
    async def rank(
        self,
        ctx,
        member: discord.Member = None
    ):

        member = member or ctx.author

        rank = hierarchy.get_rank(
            member
        )

        embed = discord.Embed(
            title="🛡️ Member Rank",
            color=discord.Color.blue()
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        embed.add_field(
            name="👤 Member",
            value=member.mention,
            inline=True
        )

        embed.add_field(
            name="🏷️ Rank",
            value=hierarchy.rank_name(rank),
            inline=True
        )

        embed.set_footer(
            text="Lilith • Hierarchy System"
        )

        await ctx.send(
            embed=embed
        )

    # =====================================================
    # SET RANK
    # =====================================================

    @command(
        "🛡️ Hierarchy",
        "Set a member's staff rank",
        usage="<member> <rank>"
    )
    async def setrank(
        self,
        ctx,
        member: discord.Member,
        rank: str
    ):

        aliases = {
            "JUNIOR": "JUNIOR",
            "JUNIOR_MOD": "JUNIOR",

            "MOD": "MODERATOR",

            "SENIOR": "SENIOR",
            "SENIOR_MOD": "SENIOR",

            "HEAD": "HEAD",
            "HEAD_MOD": "HEAD",

            "ADMIN": "ADMINISTRATOR"
        }

        rank_key = aliases.get(
            rank.upper(),
            rank.upper()
        )

        if rank_key not in hierarchy.RANKS:

            await ctx.send(
                "❌ Invalid rank.\n\n"
                "Available ranks:\n"
                "`Trainee` • `Junior` • `Moderator` • "
                "`Senior` • `Head` • `Administrator`"
            )

            return

        target_rank = hierarchy.RANKS[
            rank_key
        ]

        # Owner is controlled by Discord itself.

        if target_rank == hierarchy.RANKS["OWNER"]:

            await ctx.send(
                "❌ The Owner rank belongs to "
                "the actual server owner."
            )

            return

        if member.id == ctx.author.id:

            await ctx.send(
                "❌ You cannot change your own rank."
            )

            return

        success, message = await hierarchy.set_rank(
            ctx.author,
            member,
            target_rank
        )

        await ctx.send(
            message
        )

    # =====================================================
    # RATE
    # =====================================================

    @command(
        "🛡️ Hierarchy",
        "Rate a staff member below you",
        usage="<member> <1-5> [feedback]"
    )
    async def rate(
        self,
        ctx,
        member: discord.Member,
        rating: int,
        *,
        feedback: str = None
    ):

        if rating < 1 or rating > 5:

            await ctx.send(
                "❌ Rating must be between `1` and `5`."
            )

            return

        if not hierarchy.can_manage(
            ctx.author,
            member
        ):

            await ctx.send(
                "❌ You can only rate staff members "
                "below your own rank."
            )

            return

        hierarchy.db.insert(
            "mod_ratings",
            """
            guild_id,
            moderator_id,
            rated_by,
            rating,
            feedback,
            created_at
            """,
            (
                ctx.guild.id,
                member.id,
                ctx.author.id,
                rating,
                feedback,
                discord.utils.utcnow().isoformat()
            )
        )

        await ctx.send(
            f"⭐ Rating recorded for "
            f"{member.mention}: **{rating}/5**"
        )


# =========================================================
# SETUP
# =========================================================

async def setup(
    bot
):

    await bot.add_cog(
        Hierarchy(bot)
              )
