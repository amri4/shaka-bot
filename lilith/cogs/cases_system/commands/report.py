import discord
import mycord

from datetime import datetime

from utils.discord_setup import *
from ..buttons.continue_punishments import continue_punishments


db = mycord.PunksDB()

@command()
async def testreport(ctx):
    await ctx.send("REPORT MODULE WORKS")

def get_report_channel_id(guild_id):

    data = db.fetchone(
        "server_config",
        "guild_id = ?",
        (guild_id,)
    )

    if not data:
        return None

    return data[6]


@command()
async def report(ctx, *, reason: str):

    # =========================================
    # CHECK REPLY
    # =========================================

    if not ctx.message.reference:

        await ctx.send(
            "❌️ You must reply to the message you're reporting, *sigh*"
        )

        return

    # =========================================
    # GET REPORTED MESSAGE
    # =========================================

    reported_message = await ctx.channel.fetch_message(
        ctx.message.reference.message_id
    )

    created_at = datetime.utcnow()

    # =========================================
    # GET REPORT CHANNEL
    # =========================================

    report_channel_id = get_report_channel_id(
        ctx.guild.id
    )

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

    # =========================================
    # CREATE CASE
    # =========================================

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
            created_at.isoformat(),
            reported_message.channel.id,
            reported_message.id,
            reason
        )
    )

    # =========================================
    # GET CREATED CASE
    # =========================================

    case = db.fetchone(
        "cases",
        "guild_id = ? AND reporter_id = ? AND message_id = ?",
        (
            ctx.guild.id,
            ctx.author.id,
            reported_message.id
        )
    )

    # =========================================
    # REPORTER EMBED
    # =========================================

    embed = discord.Embed(
        title="📨 Report Received",
        description=(
            "Your report has been successfully submitted "
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

    await ctx.send(
        embed=embed
    )

    # =========================================
    # MODERATOR EMBED
    # =========================================

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
        value=reported_message.content or "*No content*",
        inline=True
    )

    mod_embed.add_field(
        name="📍 Channel",
        value=reported_message.channel.mention,
        inline=True
    )

    mod_embed.add_field(
        name="🕒 Reported",
        value=f"<t:{int(created_at.timestamp())}:R>",
        inline=True
    )

    message = (
        "🧪 Punishment test\n\n"
            "React with:\n"
            "⚠️ Warning\n"
            "🔇 Timeout\n"
            "👢 Kick\n\n"
            "Then press Continue."
    )
    mod_embed.add_field(
        name="Actions",
        value=message,
        inline=True
    )

    report_message = await report_channel.send(embed=mod_embed, view=ui(continue_punishments))
    await report_message.add_reaction("🔇")
    await report_message.add_reaction("👢")
