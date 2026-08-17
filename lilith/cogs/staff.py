import discord

from discord.ext import commands

from utils.command import command
from utils import staff


class StaffSystem(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.bot_name = (
            bot.user.name
            if bot.user
            else "Lilith"
        )

    # =====================================================
    # AUTHORITY
    # =====================================================

    async def require_rank(
        self,
        ctx,
        required_rank
    ):

        # Owner bypass

        if (
            ctx.author.id
            == ctx.guild.owner_id
        ):

            return True

        current = staff.get_member_rank(
            ctx.guild,
            ctx.author
        )

        required = staff.get_rank(
            ctx.guild.id,
            required_rank
        )

        if not required:

            await ctx.send(
                "❌ That staff rank does not exist."
            )

            return False

        if not current:

            await ctx.send(
                "🔒 You are not registered as staff."
            )

            return False

        if (
            current["level"]
            < required["level"]
        ):

            await ctx.send(
                "🔒 **Insufficient staff rank.**\n"
                f"Required: **{required['name']}**\n"
                f"Your rank: **{current['name']}**"
            )

            return False

        return True

    # =====================================================
    # HIERARCHY
    # =====================================================

    @command(
        "Staff",
        description="Show the staff hierarchy.",
        usage="Lilith hierarchy"
    )
    async def hierarchy(
        self,
        ctx
    ):

        ranks = staff.list_ranks(
            ctx.guild.id
        )

        lines = []

        for name, level in ranks:

            lines.append(
                f"**{level}.** {name}"
            )

        embed = discord.Embed(
            title="🛡️ Staff Hierarchy",
            description="\n".join(lines)
        )

        await ctx.send(
            embed=embed
        )

    # =====================================================
    # RANK
    # =====================================================

    @command(
        "Staff",
        description="Show a member's staff rank.",
        usage="Lilith rank <member>"
    )
    async def rank(
        self,
        ctx,
        member: discord.Member
    ):

        rank = staff.get_member_rank(
            ctx.guild,
            member
        )

        if not rank:

            await ctx.send(
                f"👤 {member.mention} "
                f"is not staff."
            )

            return

        await ctx.send(
            f"🛡️ {member.mention} is "
            f"**{rank['name']}** "
            f"(Level {rank['level']})."
        )

    # =====================================================
    # SET RANK
    # =====================================================

    @command(
        "Staff",
        description="Assign a staff rank.",
        usage="Lilith setrank <member> <rank>"
    )
    async def setrank(
        self,
        ctx,
        member: discord.Member,
        *,
        rank_name: str
    ):

        if not await self.require_rank(
            ctx,
            "Administrator"
        ):

            return

        target = staff.get_rank(
            ctx.guild.id,
            rank_name
        )

        if not target:

            available = "\n".join(
                f"• {name}"
                for name, _ in staff.list_ranks(
                    ctx.guild.id
                )
            )

            await ctx.send(
                "❌ **Unknown rank.**\n\n"
                + available
            )

            return

        actor = staff.get_member_rank(
            ctx.guild,
            ctx.author
        )

        if (
            ctx.author.id
            != ctx.guild.owner_id
        ):

            if (
                target["level"]
                >= actor["level"]
            ):

                await ctx.send(
                    "🔒 You cannot assign a rank "
                    "equal to or higher than your own."
                )

                return

        old = staff.get_member_rank(
            ctx.guild,
            member
        )

        if (
            old
            and ctx.author.id
            != ctx.guild.owner_id
            and old["level"]
            >= actor["level"]
        ):

            await ctx.send(
                "🔒 You cannot modify someone "
                "at or above your own rank."
            )

            return

        old_rank, new_rank = staff.set_member_rank(
            ctx.guild,
            member,
            target["name"],
            ctx.author.id,
            "Manual staff rank change."
        )

        await ctx.send(
            f"🛡️ {member.mention} is now "
            f"**{new_rank['name']}**."
        )

    # =====================================================
    # COMMAND PERMISSION
    # =====================================================

    @command(
        "Staff",
        description="Set the required rank for a command.",
        usage="Lilith setcommand <command> <rank>"
    )
    async def setcommand(
        self,
        ctx,
        command_name: str,
        *,
        rank_name: str
    ):

        if not await self.require_rank(
            ctx,
            "Administrator"
        ):

            return

        if not staff.get_rank(
            ctx.guild.id,
            rank_name
        ):

            await ctx.send(
                "❌ Unknown staff rank."
            )

            return

        staff.set_command_rank(
            ctx.guild.id,
            self.bot_name,
            command_name,
            rank_name
        )

        await ctx.send(
            f"⚙️ `{command_name}` now requires "
            f"**{rank_name}**."
        )

    @command(
        "Staff",
        description="Show a command's required rank.",
        usage="Lilith commandinfo <command>"
    )
    async def commandinfo(
        self,
        ctx,
        command_name: str
    ):

        required = staff.get_command_rank(
            ctx.guild.id,
            self.bot_name,
            command_name
        )

        await ctx.send(
            f"⚙️ **Command:** `{command_name}`\n"
            f"🔒 **Required rank:** **{required}**"
        )

    # =====================================================
    # CAREER PROFILE
    # =====================================================

    @command(
        "Staff",
        description="View a staff career profile.",
        usage="Lilith career [member]"
    )
    async def career(
        self,
        ctx,
        member: discord.Member = None
    ):

        member = member or ctx.author

        rank = staff.get_member_rank(
            ctx.guild,
            member
        )

        if not rank:

            await ctx.send(
                "❌ That member is not staff."
            )

            return

        career = staff.get_career(
            ctx.guild.id,
            member.id
        )

        score = staff.calculate_career_score(
            career
        )

        cases = staff.career_value(
            career,
            "cases_reviewed"
        )

        resolved = staff.career_value(
            career,
            "cases_resolved"
        )

        correct = staff.career_value(
            career,
            "correct_decisions"
        )

        overturned = staff.career_value(
            career,
            "overturned_cases"
        )

        appeals = staff.career_value(
            career,
            "appeals_lost"
        )

        promotions = staff.career_value(
            career,
            "promotions"
        )

        demotions = staff.career_value(
            career,
            "demotions"
        )

        warnings = staff.career_value(
            career,
            "warnings"
        )

        accuracy = (
            correct / cases * 100
            if cases
            else 0
        )

        embed = discord.Embed(
            title="🪪 Staff Career",
            description=(
                f"**{member.display_name}**\n"
                f"{member.mention}"
            )
        )

        embed.add_field(
            name="🏅 Rank",
            value=rank["name"],
            inline=True
        )

        embed.add_field(
            name="⭐ Career Score",
            value=f"{score}/100",
            inline=True
        )

        embed.add_field(
            name="⚖️ Accuracy",
            value=f"{accuracy:.1f}%",
            inline=True
        )

        embed.add_field(
            name="📋 Cases",
            value=(
                f"Reviewed: **{cases}**\n"
                f"Resolved: **{resolved}**"
            ),
            inline=True
        )

        embed.add_field(
            name="🚨 Decisions",
            value=(
                f"Overturned: **{overturned}**\n"
                f"Appeals lost: **{appeals}**"
            ),
            inline=True
        )

        embed.add_field(
            name="🏆 Career",
            value=(
                f"Promotions: **{promotions}**\n"
                f"Demotions: **{demotions}**\n"
                f"Warnings: **{warnings}**"
            ),
            inline=True
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        await ctx.send(
            embed=embed
        )

    # =====================================================
    # PROMOTION CHECK
    # =====================================================

    @command(
        "Staff",
        description="Check promotion eligibility.",
        usage="Lilith promotion <member>"
    )
    async def promotion(
        self,
        ctx,
        member: discord.Member
    ):

        if not await self.require_rank(
            ctx,
            "Administrator"
        ):

            return

        result = staff.promotion_check(
            ctx.guild.id,
            member.id
        )

        if not result["eligible"]:

            await ctx.send(
                "❌ **Not promotion eligible.**\n"
                f"{result.get('reason', 'Requirements not met.')}"
            )

            return

        embed = discord.Embed(
            title="🏆 Promotion Recommendation",
            description=(
                f"**{member.display_name}**\n\n"
                f"Current rank: **{result['current_rank']}**\n"
                f"Next rank: **{result['next_rank']}**"
            )
        )

        embed.add_field(
            name="📊 Performance",
            value=(
                f"Career score: **{result['score']}/100**\n"
                f"Cases: **{result['cases']}**\n"
                f"Accuracy: **{result['accuracy']}%**\n"
                f"Active days: **{result['active_days']}**"
            ),
            inline=False
        )

        embed.set_footer(
            text=(
                "Eligibility is calculated from recorded staff data."
            )
        )

        await ctx.send(
            embed=embed
        )

    # =====================================================
    # PROMOTE
    # =====================================================

    @command(
        "Staff",
        description="Promote an eligible staff member.",
        usage="Lilith promote <member> [reason]"
    )
    async def promote(
        self,
        ctx,
        member: discord.Member,
        *,
        reason: str = "Promotion approved by staff."
    ):

        if not await self.require_rank(
            ctx,
            "Administrator"
        ):

            return

        result = staff.promotion_check(
            ctx.guild.id,
            member.id
        )

        if not result["eligible"]:

            await ctx.send(
                "❌ This member does not meet "
                "the promotion requirements."
            )

            return

        actor = staff.get_member_rank(
            ctx.guild,
            ctx.author
        )

        next_rank = staff.get_rank(
            ctx.guild.id,
            result["next_rank"]
        )

        if (
            ctx.author.id
            != ctx.guild.owner_id
            and next_rank["level"]
            >= actor["level"]
        ):

            await ctx.send(
                "🔒 You cannot promote someone "
                "to your rank or higher."
            )

            return

        old, new = staff.set_member_rank(
            ctx.guild,
            member,
            next_rank["name"],
            ctx.author.id,
            reason
        )

        await ctx.send(
            f"🏆 **Promotion approved!**\n"
            f"{member.mention}\n"
            f"**{old['name']} → {new['name']}**"
        )

    # =====================================================
    # DEMOTE
    # =====================================================

    @command(
        "Staff",
        description="Demote a staff member.",
        usage="Lilith demote <member> <rank> [reason]"
    )
    async def demote(
        self,
        ctx,
        member: discord.Member,
        rank_name: str,
        *,
        reason: str = "Demotion approved by staff."
    ):

        if not await self.require_rank(
            ctx,
            "Administrator"
        ):

            return

        target = staff.get_rank(
            ctx.guild.id,
            rank_name
        )

        if not target:

            await ctx.send(
                "❌ Unknown staff rank."
            )

            return

        current = staff.get_member_rank(
            ctx.guild,
            member
        )

        if not current:

            await ctx.send(
                "❌ That member is not staff."
            )

            return

        actor = staff.get_member_rank(
            ctx.guild,
            ctx.author
        )

        if (
            ctx.author.id
            != ctx.guild.owner_id
        ):

            if current["level"] >= actor["level"]:

                await ctx.send(
                    "🔒 You cannot demote someone "
                    "at or above your rank."
                )

                return

            if target["level"] >= current["level"]:

                await ctx.send(
                    "❌ The new rank must be lower "
                    "than their current rank."
                )

                return

        old, new = staff.set_member_rank(
            ctx.guild,
            member,
            target["name"],
            ctx.author.id,
            reason
        )

        await ctx.send(
            f"📉 **Demotion applied.**\n"
            f"{member.mention}\n"
            f"**{old['name']} → {new['name']}**"
        )

    # =====================================================
    # CAREER HISTORY
    # =====================================================

    @command(
        "Staff",
        description="Show staff career history.",
        usage="Lilith careerhistory <member>"
    )
    async def careerhistory(
        self,
        ctx,
        member: discord.Member
    ):

        history = []

        for row in staff.all_rows(
            "staff_career_history"
        ):

            if isinstance(row, dict):

                if (
                    row.get("guild_id")
                    == ctx.guild.id
                    and row.get("user_id")
                    == member.id
                ):

                    history.append(row)

            else:

                if (
                    row[1] == ctx.guild.id
                    and row[2] == member.id
                ):

                    history.append(row)

        if not history:

            await ctx.send(
                "📜 No career history found."
            )

            return

        embed = discord.Embed(
            title=(
                f"📜 Career History — "
                f"{member.display_name}"
            )
        )

        for row in history[-10:]:

            if isinstance(row, dict):

                action = row["action"]
                old_rank = row["old_rank"]
                new_rank = row["new_rank"]
                reason = row["reason"]
                date = row["created_at"]

            else:

                action = row[3]
                old_rank = row[4]
                new_rank = row[5]
                reason = row[6]
                date = row[8]

            embed.add_field(
                name=f"📌 {action.title()}",
                value=(
                    f"**From:** "
                    f"{old_rank or 'None'}\n"
                    f"**To:** "
                    f"{new_rank or 'None'}\n"
                    f"**Reason:** "
                    f"{reason}\n"
                    f"**Date:** "
                    f"{date}"
                ),
                inline=False
            )

        await ctx.send(
            embed=embed
        )


async def setup(bot):

    await bot.add_cog(
        StaffSystem(bot)
    )
