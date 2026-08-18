import discord
from discord.ext import commands
import mycord
from utils.command import command
from datetime import datetime

db = mycord.PunksDB()

db.create_table(
    "cases",
    """
    case_id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    reporter_id INTEGER NOT NULL,
    suspect_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    channel_id INTEGER,
    message_id INTEGER,
    report_reason TEXT,
    violation TEXT,
    moderator_reason TEXT,
    reviewer_id INTEGER
    """
)
CASE_STATUSES = {
    "OPEN",
    "REVIEWING",
    "RESOLVED",
    "DISMISSED"
}
db.create_table(
    "case_history",
    """
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,
    moderator_id INTEGER NOT NULL,
    event TEXT NOT NULL,
    details TEXT,
    created_at TEXT NOT NULL
    """
)
db.create_table(
    "case_actions",
    """
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL,
    guild_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    selected_by INTEGER NOT NULL,
    confirmed INTEGER NOT NULL DEFAULT 0,
    executed INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    executed_at TEXT
    """
)

class Reports(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @command("🔴 Reports", description="Report a message to staff", usage="<reply to message> <reason>")
    async def report(self, ctx, *, reason: str):
        if not ctx.message.reference:
            await ctx.send("❌️ You must reply to the message you're reporting, *sigh*")
            return
        reported_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        db.insert(
            "cases",
            """
            guild_id,
            reporter_id,
            suspect_id,
            status,
            created_at,
            channel_id,
            message_id,
            report_reason
            """,
            (
                ctx.guild.id,
                ctx.author.id,
                reported_message.author.id,
                "OPEN",
                datetime.utcnow().isoformat(),
                reported_message.channel.id,
                reported_message.id,
                reason
            )
        )
        case = db.fetchone(
            "cases",
            "guild_id = ? AND reporter_id = ? AND message_id = ?",
            (
                ctx.guild.id,
                ctx.author.id,
                reported_message.id
            )
        )
        embed = discord.Embed(
            title="📨 Report Received",
            description=("Your report has been successfully submitted "
                         "for mods review"
                        ),
            color=discord.Color.blue()
        )
        embed.add_field(
            name="🆔️ Case ID",
            value=f"`#{case[0]}`",
            inline=True
        )
        embed.add_field(
            name="👤 Reported User",
            value=reported_message.author.mention,
            inline=True
        )
        embed.add_field(
            name="📌 Status",
            value="`OPEN`",
            inline=True
        )
        embed.set_footer(
            text="Lilith • Moderation System"
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Reports(bot))
