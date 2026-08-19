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

    def get_report_channel_id(self, guild_id):
        data = db.fetchone(
            "server_config",
            "guild_id = ?",
            (guild_id,)
        )

        if not data:
            return None

        return data[6]
    
    @command("🔴 Reports", description="Report a message to staff", usage="<reply to message> <reason>")
    async def report(self, ctx, *, reason: str):
        if not ctx.message.reference:
            await ctx.send("❌️ You must reply to the message you're reporting, *sigh*")
            return
        reported_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        report_channel_id = self.get_report_channel_id(ctx.guild.id)

        if not report_channel_id:
            await ctx.send(
                "❌️ The report channel has not been configured."
            )
            return

        report_channel = ctx.guild.get_channel(
                report_channel_id
            )

        if not report_channel:
            await ctx.send(
                "❌️ The configured report channel no longer exists."
            )
            return
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

        mod_embed = discord.Embed(
            title="🚨 New Report",
            color=discord.Color.red()
        )
        mod_embed.add_field(
            name="🆔️ Case ID",
            value=f"`#{case[0]}`",
            inline=True
        )
        mod_embed.add_field(
            name="👤 Reporter",
            value=ctx.author.mention,
            inline=True
        )
        mod_embed.add_field(
            name="🎯 Reported User",
            value=reported_message.author.mention,
            inline=True
        )
        mod_embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=True
        )
        mod_embed.add_field(
            name="📌 Status",
            value="`OPEN`",
            inline=True
        )
        mod_embed.add_field(
            name="💬 Reported Message",
            value=reported_message,
            inline=True
        )
        mod_embed.add_field(
            name="📍 Channel",
            value=reported_message.channel,
            inline=True
        )
        created_at = datetime.utcnow()
        mod_embed.add_field(
            name="🕒 Reported",
            value=f"<t:{int(created_at.timestamp())}:R>",
            inline=True
        )
        await report_channel.send(embed=mod_embed)
        
async def setup(bot):
    await bot.add_cog(Reports(bot))
