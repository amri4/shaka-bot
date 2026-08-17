import discord
from discord.ext import commands

from datetime import datetime, timedelta

import mycord
from utils.command import command


db = mycord.PunksDB()


# =========================================================
# DATABASE
# =========================================================

db.create_table(
    "mod_cases",
    """
    case_id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    reporter_id INTEGER NOT NULL,
    suspect_id INTEGER NOT NULL,

    channel_id INTEGER,
    message_id INTEGER,

    report_reason TEXT,

    violation TEXT,
    moderator_reason TEXT,

    status TEXT NOT NULL,

    reviewer_id INTEGER,

    created_at TEXT,
    reviewed_at TEXT,
    resolved_at TEXT
    """
)


db.create_table(
    "case_actions",
    """
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    case_id INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,

    action TEXT NOT NULL,

    selected_by INTEGER,

    confirmed INTEGER DEFAULT 0,

    executed INTEGER DEFAULT 0,

    created_at TEXT,
    executed_at TEXT
    """
)


db.create_table(
    "case_history",
    """
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    case_id INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,

    moderator_id INTEGER NOT NULL,

    event TEXT NOT NULL,
    details TEXT,

    created_at TEXT
    """
)


# =========================================================
# MIGRATION
# =========================================================

case_columns = {

    "channel_id": "INTEGER",

    "message_id": "INTEGER",

    "report_reason": "TEXT",

    "violation": "TEXT",

    "moderator_reason": "TEXT",

    "status": "TEXT",

    "reviewer_id": "INTEGER",

    "created_at": "TEXT",

    "reviewed_at": "TEXT",

    "resolved_at": "TEXT"
}


for column, column_type in case_columns.items():

    try:

        db.add_column(
            "mod_cases",
            column,
            column_type
        )

    except Exception:

        # Column already exists.
        pass


# =========================================================
# TIME
# =========================================================

def now():

    return datetime.utcnow().isoformat()


# =========================================================
# GET MEMBER
# =========================================================

def get_member(
    guild,
    user_id
):

    member = guild.get_member(
        user_id
    )

    if member:

        return member

    return None


# =========================================================
# CASE REVIEW VIEW
# =========================================================

class CaseReviewView(
    discord.ui.View
):

    def __init__(
        self,
        cog,
        case_id
    ):

        super().__init__(
            timeout=None
        )

        self.cog = cog
        self.case_id = case_id

    # =====================================================
    # CLAIM CASE
    # =====================================================

    @discord.ui.button(
        label="Claim Case",
        style=discord.ButtonStyle.primary,
        emoji="👮"
    )
    async def claim(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        case = self.cog.get_case(
            self.case_id
        )

        if not case:

            await interaction.response.send_message(
                "❌ This case no longer exists.",
                ephemeral=True
            )

            return

        status = case[10]

        if status == "RESOLVED":

            await interaction.response.send_message(
                "❌ This case has already been resolved.",
                ephemeral=True
            )

            return

        reviewer_id = case[11]

        if (
            reviewer_id
            and reviewer_id != interaction.user.id
        ):

            await interaction.response.send_message(
                (
                    "❌ This case is already being "
                    f"reviewed by <@{reviewer_id}>."
                ),
                ephemeral=True
            )

            return

        db.update(
            "mod_cases",
            "reviewer_id = ?, status = ?",
            "case_id = ?",
            (
                interaction.user.id,
                "REVIEWING",
                self.case_id
            )
        )

        self.cog.add_history(
            self.case_id,
            case[1],
            interaction.user.id,
            "CASE_CLAIMED",
            "Moderator claimed the case."
        )

        await interaction.response.send_message(
            (
                f"👮 You are now reviewing "
                f"**Case #{self.case_id}**."
            ),
            ephemeral=True
        )

    # =====================================================
    # VIEW CASE
    # =====================================================

    @discord.ui.button(
        label="View Case",
        style=discord.ButtonStyle.secondary,
        emoji="🔎"
    )
    async def view_case(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await self.cog.send_case_details(
            interaction,
            self.case_id
        )

    # =====================================================
    # PREVIOUS CASES
    # =====================================================

    @discord.ui.button(
        label="Previous Cases",
        style=discord.ButtonStyle.secondary,
        emoji="📚"
    )
    async def previous(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        case = self.cog.get_case(
            self.case_id
        )

        if not case:

            await interaction.response.send_message(
                "❌ Case not found.",
                ephemeral=True
            )

            return

        cases = db.fetchall(
            "mod_cases"
        )

        previous_cases = []

        for old_case in cases:

            if old_case[1] != case[1]:
                continue

            if old_case[3] != case[3]:
                continue

            if old_case[0] == self.case_id:
                continue

            previous_cases.append(
                old_case
            )

        if not previous_cases:

            await interaction.response.send_message(
                "📚 This member has no previous cases.",
                ephemeral=True
            )

            return

        embed = discord.Embed(
            title="📚 Previous Cases",
            description=(
                f"Previous cases for <@{case[3]}>"
            ),
            color=discord.Color.orange()
        )

        for old_case in previous_cases[-10:]:

            violation = (
                old_case[7]
                or "Not identified"
            )

            embed.add_field(
                name=f"Case #{old_case[0]}",
                value=(
                    f"**Status:** {old_case[10]}\n"
                    f"**Violation:** {violation}"
                ),
                inline=False
            )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # =====================================================
    # IDENTIFY VIOLATION
    # =====================================================

    @discord.ui.button(
        label="Identify Violation",
        style=discord.ButtonStyle.success,
        emoji="⚖️"
    )
    async def identify(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        case = self.cog.get_case(
            self.case_id
        )

        if not case:

            await interaction.response.send_message(
                "❌ Case not found.",
                ephemeral=True
            )

            return

        if case[11] != interaction.user.id:

            await interaction.response.send_message(
                "❌ Claim the case before identifying the violation.",
                ephemeral=True
            )

            return

        await interaction.response.send_modal(
            ViolationModal(
                self.cog,
                self.case_id
            )
        )

    # =====================================================
    # CHOOSE ACTIONS
    # =====================================================

    @discord.ui.button(
        label="Choose Actions",
        style=discord.ButtonStyle.primary,
        emoji="🛠️"
    )
    async def actions(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        case = self.cog.get_case(
            self.case_id
        )

        if not case:

            await interaction.response.send_message(
                "❌ Case not found.",
                ephemeral=True
            )

            return

        if case[11] != interaction.user.id:

            await interaction.response.send_message(
                "❌ Claim the case before selecting actions.",
                ephemeral=True
            )

            return

        await interaction.response.send_message(
            "🛠️ Choose the actions that should be applied:",
            view=ActionView(
                self.cog,
                self.case_id
            ),
            ephemeral=True
        )

    # =====================================================
    # CONFIRM PUNISHMENT
    # =====================================================

    @discord.ui.button(
        label="Confirm Punishment",
        style=discord.ButtonStyle.danger,
        emoji="✅"
    )
    async def confirm(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await self.cog.confirm_case(
            interaction,
            self.case_id
        )


# =========================================================
# VIOLATION MODAL
# =========================================================

class ViolationModal(
    discord.ui.Modal,
    title="Identify Case"
):

    violation = discord.ui.TextInput(
        label="Violation",
        placeholder="Example: Spam",
        max_length=100
    )

    reason = discord.ui.TextInput(
        label="Moderator Reason",
        placeholder="Explain why this is a violation.",
        style=discord.TextStyle.paragraph,
        max_length=1000
    )

    def __init__(
        self,
        cog,
        case_id
    ):

        super().__init__()

        self.cog = cog
        self.case_id = case_id

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        case = self.cog.get_case(
            self.case_id
        )

        if not case:

            await interaction.response.send_message(
                "❌ Case not found.",
                ephemeral=True
            )

            return

        if case[11] != interaction.user.id:

            await interaction.response.send_message(
                "❌ You are not the moderator reviewing this case.",
                ephemeral=True
            )

            return

        db.update(
            "mod_cases",
            """
            violation = ?,
            moderator_reason = ?,
            reviewer_id = ?,
            status = ?,
            reviewed_at = ?
            """,
            "case_id = ?",
            (
                str(self.violation),
                str(self.reason),
                interaction.user.id,
                "REVIEWED",
                now(),
                self.case_id
            )
        )

        self.cog.add_history(
            self.case_id,
            case[1],
            interaction.user.id,
            "VIOLATION_IDENTIFIED",
            (
                f"{self.violation}: "
                f"{self.reason}"
            )
        )

        await interaction.response.send_message(
            (
                f"⚖️ **Case #{self.case_id} updated.**\n\n"
                f"**Violation:** {self.violation}\n"
                f"**Reason:** {self.reason}"
            ),
            ephemeral=True
        )


# =========================================================
# ACTION VIEW
# =========================================================

class ActionView(
    discord.ui.View
):

    def __init__(
        self,
        cog,
        case_id
    ):

        super().__init__(
            timeout=300
        )

        self.cog = cog
        self.case_id = case_id

    # =====================================================
    # ACTION HELPER
    # =====================================================

    async def select_action(
        self,
        interaction,
        action
    ):

        case = self.cog.get_case(
            self.case_id
        )

        if not case:

            await interaction.response.send_message(
                "❌ Case not found.",
                ephemeral=True
            )

            return

        if case[11] != interaction.user.id:

            await interaction.response.send_message(
                "❌ You are not reviewing this case.",
                ephemeral=True
            )

            return

        exists = db.exists(
            "case_actions",
            "case_id = ? AND action = ?",
            (
                self.case_id,
                action
            )
        )

        if exists:

            await interaction.response.send_message(
                f"ℹ️ **{action}** is already selected.",
                ephemeral=True
            )

            return

        db.insert(
            "case_actions",
            """
            case_id,
            guild_id,
            action,
            selected_by,
            confirmed,
            executed,
            created_at
            """,
            (
                self.case_id,
                case[1],
                action,
                interaction.user.id,
                0,
                0,
                now()
            )
        )

        self.cog.add_history(
            self.case_id,
            case[1],
            interaction.user.id,
            "ACTION_SELECTED",
            action
        )

        await interaction.response.send_message(
            f"🛠️ Selected **{action}**.",
            ephemeral=True
        )

    # =====================================================
    # WARN
    # =====================================================

    @discord.ui.button(
        label="Warn",
        style=discord.ButtonStyle.secondary,
        emoji="⚠️"
    )
    async def warn(
        self,
        interaction,
        button
    ):

        await self.select_action(
            interaction,
            "WARN"
        )

    # =====================================================
    # TIMEOUT
    # =====================================================

    @discord.ui.button(
        label="Timeout",
        style=discord.ButtonStyle.secondary,
        emoji="🔇"
    )
    async def timeout(
        self,
        interaction,
        button
    ):

        await self.select_action(
            interaction,
            "TIMEOUT"
        )

    # =====================================================
    # KICK
    # =====================================================

    @discord.ui.button(
        label="Kick",
        style=discord.ButtonStyle.secondary,
        emoji="👢"
    )
    async def kick(
        self,
        interaction,
        button
    ):

        await self.select_action(
            interaction,
            "KICK"
        )

    # =====================================================
    # BAN
    # =====================================================

    @discord.ui.button(
        label="Ban",
        style=discord.ButtonStyle.danger,
        emoji="🔨"
    )
    async def ban(
        self,
        interaction,
        button
    ):

        await self.select_action(
            interaction,
            "BAN"
        )

    # =====================================================
    # NO ACTION
    # =====================================================

    @discord.ui.button(
        label="No Punishment",
        style=discord.ButtonStyle.success,
        emoji="➖"
    )
    async def none(
        self,
        interaction,
        button
    ):

        await self.select_action(
            interaction,
            "NO_ACTION"
        )


# =========================================================
# FINAL CONFIRMATION
# =========================================================

class FinalConfirmationView(
    discord.ui.View
):

    def __init__(
        self,
        cog,
        case_id,
        moderator_id
    ):

        super().__init__(
            timeout=60
        )

        self.cog = cog
        self.case_id = case_id
        self.moderator_id = moderator_id

    # =====================================================
    # CONFIRM
    # =====================================================

    @discord.ui.button(
        label="CONFIRM",
        style=discord.ButtonStyle.danger,
        emoji="🔨"
    )
    async def confirm(
        self,
        interaction,
        button
    ):

        if interaction.user.id != self.moderator_id:

            await interaction.response.send_message(
                (
                    "❌ Only the moderator who started "
                    "this confirmation can confirm it."
                ),
                ephemeral=True
            )

            return

        await self.cog.execute_case(
            interaction,
            self.case_id
        )

    # =====================================================
    # CANCEL
    # =====================================================

    @discord.ui.button(
        label="Cancel",
        style=discord.ButtonStyle.secondary,
        emoji="❌"
    )
    async def cancel(
        self,
        interaction,
        button
    ):

        await interaction.response.edit_message(
            content="❌ Punishment confirmation cancelled.",
            embed=None,
            view=None
        )


# =========================================================
# REPORTS COG
# =========================================================

class Reports(
    commands.Cog
):

    def __init__(
        self,
        bot
    ):

        self.bot = bot

    # =====================================================
    # PYTHAGORAS
    # =====================================================

    def get_config(
        self
    ):

        return self.bot.get_cog(
            "Config"
        )

    # =====================================================
    # GET CASE
    # =====================================================

    def get_case(
        self,
        case_id
    ):

        return db.fetchone(
            "mod_cases",
            "case_id = ?",
            (case_id,)
        )

    # =====================================================
    # ADD HISTORY
    # =====================================================

    def add_history(
        self,
        case_id,
        guild_id,
        moderator_id,
        event,
        details
    ):

        db.insert(
            "case_history",
            """
            case_id,
            guild_id,
            moderator_id,
            event,
            details,
            created_at
            """,
            (
                case_id,
                guild_id,
                moderator_id,
                event,
                details,
                now()
            )
        )

    # =====================================================
    # REPORT COMMAND
    # =====================================================

    @command(
        "🛡️ Moderation",
        "Report a member for moderator review",
        usage="report @member reason"
    )
    async def report(
        self,
        ctx,
        member: discord.Member,
        *,
        reason: str
    ):

        if member.id == ctx.author.id:

            await ctx.send(
                "❌ You cannot report yourself."
            )

            return

        if member.bot:

            await ctx.send(
                "❌ You cannot report a bot."
            )

            return

        # =================================================
        # EXACT MESSAGE
        # =================================================

        message_id = None
        channel_id = None

        reference = ctx.message.reference

        if reference:

            message_id = reference.message_id
            channel_id = ctx.channel.id

        # =================================================
        # CREATE CASE
        # =================================================

        db.insert(
            "mod_cases",
            """
            guild_id,
            reporter_id,
            suspect_id,
            channel_id,
            message_id,
            report_reason,
            status,
            created_at
            """,
            (
                ctx.guild.id,
                ctx.author.id,
                member.id,
                channel_id,
                message_id,
                reason,
                "OPEN",
                now()
            )
        )

        # =================================================
        # FIND NEW CASE
        # =================================================

        cases = db.fetchall(
            "mod_cases"
        )

        case = None

        for item in reversed(cases):

            if (
                item[1] == ctx.guild.id
                and item[2] == ctx.author.id
                and item[3] == member.id
                and item[6] == reason
            ):

                case = item
                break

        if not case:

            await ctx.send(
                "❌ The report was created but I couldn't load the case."
            )

            return

        case_id = case[0]

        self.add_history(
            case_id,
            ctx.guild.id,
            ctx.author.id,
            "REPORT_CREATED",
            reason
        )

        # =================================================
        # PYTHAGORAS
        # =================================================

        config = self.get_config()

        if not config:

            await ctx.send(
                f"✅ Report submitted as **Case #{case_id}**."
            )

            return

        report_channel = config.get_channel(
            ctx.guild,
            "reports"
        )

        case_channel = config.get_channel(
            ctx.guild,
            "case"
        )

        destination = (
            case_channel
            or report_channel
        )

        # =================================================
        # EMBED
        # =================================================

        embed = discord.Embed(
            title=f"📨 New Report • Case #{case_id}",
            color=discord.Color.orange()
        )

        embed.add_field(
            name="👤 Reported Member",
            value=member.mention,
            inline=True
        )

        embed.add_field(
            name="📝 Reporter",
            value=ctx.author.mention,
            inline=True
        )

        embed.add_field(
            name="📊 Status",
            value="OPEN",
            inline=True
        )

        embed.add_field(
            name="📌 Reason",
            value=reason[:1024],
            inline=False
        )

        # =================================================
        # EXACT MESSAGE LINK
        # =================================================

        if message_id:

            jump_url = (
                f"https://discord.com/channels/"
                f"{ctx.guild.id}/"
                f"{channel_id}/"
                f"{message_id}"
            )

            embed.add_field(
                name="📍 Reported Message",
                value=(
                    f"[Jump to the exact message]"
                    f"({jump_url})"
                ),
                inline=False
            )

        embed.set_footer(
            text="Lilith • Awaiting moderator review"
        )

        # =================================================
        # SEND
        # =================================================

        if destination:

            await destination.send(
                embed=embed,
                view=CaseReviewView(
                    self,
                    case_id
                )
            )

        await ctx.send(
            (
                f"✅ Your report has been submitted "
                f"as **Case #{case_id}**."
            )
        )

    # =====================================================
    # CASE COMMAND
    # =====================================================

    @command(
        "🛡️ Moderation",
        "Open a moderation case",
        usage="case <case_id>"
    )
    @commands.has_guild_permissions(
        moderate_members=True
    )
    async def case(
        self,
        ctx,
        case_id: int
    ):

        await self.send_case_details(
            ctx,
            case_id
        )

    # =====================================================
    # CASE DETAILS
    # =====================================================

    async def send_case_details(
        self,
        target,
        case_id
    ):

        case = self.get_case(
            case_id
        )

        if not case:

            await target.send(
                "❌ Case not found."
            )

            return

        guild = target.guild

        reporter = get_member(
            guild,
            case[2]
        )

        suspect = get_member(
            guild,
            case[3]
        )

        reporter_text = (
            reporter.mention
            if reporter
            else f"<@{case[2]}>"
        )

        suspect_text = (
            suspect.mention
            if suspect
            else f"<@{case[3]}>"
        )

        embed = discord.Embed(
            title=f"⚖️ Case #{case_id}",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="👤 Suspect",
            value=suspect_text,
            inline=True
        )

        embed.add_field(
            name="📝 Reporter",
            value=reporter_text,
            inline=True
        )

        embed.add_field(
            name="📊 Status",
            value=case[10],
            inline=True
        )

        embed.add_field(
            name="📌 Report",
            value=(
                case[6]
                or "No reason provided."
            )[:1024],
            inline=False
        )

        embed.add_field(
            name="⚖️ Identified Violation",
            value=(
                case[7]
                or "Not identified yet."
            ),
            inline=False
        )

        if case[8]:

            embed.add_field(
                name="🛡️ Moderator Reason",
                value=case[8][:1024],
                inline=False
            )

        # =================================================
        # EXACT MESSAGE
        # =================================================

        if case[4] and case[5]:

            jump_url = (
                f"https://discord.com/channels/"
                f"{guild.id}/"
                f"{case[4]}/"
                f"{case[5]}"
            )

            embed.add_field(
                name="📍 Evidence",
                value=(
                    f"[Jump to the exact reported message]"
                    f"({jump_url})"
                ),
                inline=False
            )

        embed.set_footer(
            text="Lilith • Case Review"
        )

        await target.send(
            embed=embed,
            view=CaseReviewView(
                self,
                case_id
            )
        )

    # =====================================================
    # CONFIRM CASE
    # =====================================================

    async def confirm_case(
        self,
        interaction,
        case_id
    ):

        case = self.get_case(
            case_id
        )

        if not case:

            await interaction.response.send_message(
                "❌ Case not found.",
                ephemeral=True
            )

            return

        if case[10] == "RESOLVED":

            await interaction.response.send_message(
                "❌ This case has already been resolved.",
                ephemeral=True
            )

            return

        if not case[7]:

            await interaction.response.send_message(
                (
                    "❌ Identify the violation "
                    "before confirming."
                ),
                ephemeral=True
            )

            return

        if case[11] != interaction.user.id:

            await interaction.response.send_message(
                (
                    "❌ You must claim this case "
                    "before confirming it."
                ),
                ephemeral=True
            )

            return

        actions = db.fetchall(
            "case_actions"
        )

        selected = []

        for action in actions:

            if (
                action[1] == case_id
                and action[5] == 0
            ):

                selected.append(
                    action
                )

        if not selected:

            await interaction.response.send_message(
                "❌ Select at least one action first.",
                ephemeral=True
            )

            return

        action_names = []

        for action in selected:

            action_names.append(
                action[3]
            )

        embed = discord.Embed(
            title=f"⚠️ Confirm Case #{case_id}",
            description=(
                "You are about to confirm "
                "these moderation actions."
            ),
            color=discord.Color.red()
        )

        embed.add_field(
            name="Violation",
            value=case[7],
            inline=False
        )

        embed.add_field(
            name="Actions",
            value="\n".join(
                f"• {action}"
                for action in action_names
            ),
            inline=False
        )

        embed.set_footer(
            text="Nothing will happen until you confirm."
        )

        await interaction.response.send_message(
            embed=embed,
            view=FinalConfirmationView(
                self,
                case_id,
                interaction.user.id
            ),
            ephemeral=True
        )

    # =====================================================
    # EXECUTE CASE
    # =====================================================

    async def execute_case(
        self,
        interaction,
        case_id
    ):

        case = self.get_case(
            case_id
        )

        if not case:

            await interaction.response.edit_message(
                content="❌ Case no longer exists.",
                embed=None,
                view=None
            )

            return

        if case[11] != interaction.user.id:

            await interaction.response.edit_message(
                content="❌ You are not the reviewer of this case.",
                embed=None,
                view=None
            )

            return

        actions = db.fetchall(
            "case_actions"
        )

        selected = []

        for action in actions:

            if (
                action[1] == case_id
                and action[5] == 0
            ):

                selected.append(
                    action
                )

        if not selected:

            await interaction.response.edit_message(
                content="❌ There are no pending actions.",
                embed=None,
                view=None
            )

            return

        member = get_member(
            interaction.guild,
            case[3]
        )

        results = []

        for action in selected:

            action_id = action[0]
            action_name = action[3]

            try:

                # =====================================
                # WARN
                # =====================================

                if action_name == "WARN":

                    results.append(
                        "⚠️ Warning recorded"
                    )

                # =====================================
                # TIMEOUT
                # =====================================

                elif action_name == "TIMEOUT":

                    if not member:

                        results.append(
                            "❌ Timeout failed: member not found"
                        )

                    else:

                        await member.timeout(
                            timedelta(
                                minutes=10
                            ),
                            reason=(
                                f"Lilith Case #{case_id}"
                            )
                        )

                        results.append(
                            "🔇 10-minute timeout applied"
                        )

                # =====================================
                # KICK
                # =====================================

                elif action_name == "KICK":

                    if not member:

                        results.append(
                            "❌ Kick failed: member not found"
                        )

                    else:

                        await member.kick(
                            reason=(
                                f"Lilith Case #{case_id}"
                            )
                        )

                        results.append(
                            "👢 Member kicked"
                        )

                # =====================================
                # BAN
                # =====================================

                elif action_name == "BAN":

                    if not member:

                        results.append(
                            "❌ Ban failed: member not found"
                        )

                    else:

                        await member.ban(
                            reason=(
                                f"Lilith Case #{case_id}"
                            )
                        )

                        results.append(
                            "🔨 Member banned"
                        )

                # =====================================
                # NO ACTION
                # =====================================

                elif action_name == "NO_ACTION":

                    results.append(
                        "➖ No punishment"
                    )

                # =====================================
                # MARK EXECUTED
                # =====================================

                db.update(
                    "case_actions",
                    """
                    confirmed = ?,
                    executed = ?,
                    executed_at = ?
                    """,
                    "id = ?",
                    (
                        1,
                        1,
                        now(),
                        action_id
                    )
                )

            except Exception as error:

                results.append(
                    (
                        f"❌ {action_name} failed: "
                        f"{type(error).__name__}"
                    )
                )

        # =================================================
        # RESOLVE
        # =================================================

        db.update(
            "mod_cases",
            "status = ?, resolved_at = ?",
            "case_id = ?",
            (
                "RESOLVED",
                now(),
                case_id
            )
        )

        self.add_history(
            case_id,
            case[1],
            interaction.user.id,
            "CASE_RESOLVED",
            ", ".join(results)
        )

        # =================================================
        # PYTHAGORAS LOG
        # =================================================

        config = self.get_config()

        if config:

            log_channel = config.get_channel(
                interaction.guild,
                "punishment_log"
            )

            if log_channel:

                embed = discord.Embed(
                    title=f"🛡️ Case #{case_id} Resolved",
                    color=discord.Color.green()
                )

                embed.add_field(
                    name="Suspect",
                    value=f"<@{case[3]}>",
                    inline=True
                )

                embed.add_field(
                    name="Moderator",
                    value=interaction.user.mention,
                    inline=True
                )

                embed.add_field(
                    name="Violation",
                    value=case[7],
                    inline=False
                )

                embed.add_field(
                    name="Actions",
                    value="\n".join(
                        f"• {result}"
                        for result in results
                    ),
                    inline=False
                )

                await log_channel.send(
                    embed=embed
                )

        await interaction.response.edit_message(
            content=(
                f"✅ **Case #{case_id} resolved.**\n\n"
                + "\n".join(results)
            ),
            embed=None,
            view=None
        )


# =========================================================
# SETUP
# =========================================================

async def setup(
    bot
):

    await bot.add_cog(
        Reports(bot)
)
