import random
import discord
from discord.ext import commands
import database

TRUTHS = [
    "Truth does not change based on whether you accept it or not.",
    "Justice delayed is justice denied.",
    "Evil that goes unchecked is evil that spreads.",
    "Logic is the highest form of respect one can offer.",
    "Every lie has a cost. Every truth, a price.",
    "The strong have a responsibility to protect the weak — that is the only just order.",
    "Ignorance is not innocence.",
    "What is just must always be pursued, even when inconvenient.",
    "There is no neutrality. Inaction in the face of injustice is a choice.",
    "True good requires discipline, not merely intention.",
]

VERDICTS = ["JUST", "UNJUST", "NEUTRAL — further evidence required", "GUILTY", "INNOCENT"]

SCAN_RESULTS = [
    "Threat level: MINIMAL. No action required.",
    "Threat level: MODERATE. Monitoring recommended.",
    "Threat level: HIGH. I am keeping my eye on this individual.",
    "Threat level: CRITICAL. Immediate containment advised.",
    "Threat level: ZERO. A perfectly upstanding individual.",
    "Threat level: UNKNOWN. Insufficient data — investigation ongoing.",
]

SIBLINGS = [
    ("Shaka", "01", "Good", "shaka"),
    ("Lilith", "02", "Evil", "lilith"),
    ("Edison", "03", "Thinker", "edison"),
    ("Pythagoras", "04", "Wisdom", "py"),
    ("Atlas", "05", "Violence", "atlas"),
    ("York", "06", "Greed", "york"),
]


class JusticeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="judge")
    async def judge(self, ctx, member: discord.Member, *, reason: str):
        verdict = random.choice(VERDICTS)
        database.add_judgment(ctx.guild.id, ctx.author.id, member.id, reason, verdict)
        embed = discord.Embed(
            title="⚖️ Judgment Issued",
            color=discord.Color.blue(),
        )
        embed.add_field(name="Accused", value=member.mention, inline=True)
        embed.add_field(name="Verdict", value=f"**{verdict}**", inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_footer(text=f"Judged by {ctx.author.display_name} | Shaka, Satellite 01")
        await ctx.send(embed=embed)

    @commands.command(name="verdicts")
    async def verdicts(self, ctx):
        rows = database.get_recent_judgments(ctx.guild.id)
        if not rows:
            await ctx.send("No judgments have been issued in this server yet.")
            return
        embed = discord.Embed(
            title="⚖️ Recent Judgments",
            color=discord.Color.blue(),
        )
        for row in rows:
            judgment_id, judge_id, target_id, reason, verdict, timestamp = row
            embed.add_field(
                name=f"Case #{judgment_id} — {verdict}",
                value=f"**Accused:** <@{target_id}>\n**Reason:** {reason}\n**Date:** {timestamp[:10]}",
                inline=False,
            )
        await ctx.send(embed=embed)

    @commands.command(name="verdict")
    async def verdict(self, ctx, judgment_id: int):
        row = database.get_judgment_by_id(judgment_id)
        if not row:
            await ctx.send(f"No judgment found with ID `{judgment_id}`.")
            return
        j_id, judge_id, target_id, reason, verdict, timestamp = row
        embed = discord.Embed(
            title=f"⚖️ Case #{j_id}",
            color=discord.Color.blue(),
        )
        embed.add_field(name="Judge", value=f"<@{judge_id}>", inline=True)
        embed.add_field(name="Accused", value=f"<@{target_id}>", inline=True)
        embed.add_field(name="Verdict", value=f"**{verdict}**", inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Date", value=timestamp[:10], inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="truth")
    async def truth(self, ctx):
        truth = random.choice(TRUTHS)
        embed = discord.Embed(
            title="📜 A Truth from Shaka",
            description=f"*\"{truth}\"*",
            color=discord.Color.blue(),
        )
        embed.set_footer(text="Satellite 01 — Shaka (Good)")
        await ctx.send(embed=embed)

    @commands.command(name="scan")
    async def scan(self, ctx, member: discord.Member):
        result = random.choice(SCAN_RESULTS)
        embed = discord.Embed(
            title=f"🔍 Threat Scan — {member.display_name}",
            description=result,
            color=discord.Color.blue(),
        )
        embed.set_footer(text="Shaka's threat analysis system | Satellite 01")
        await ctx.send(embed=embed)

    @commands.command(name="siblings")
    async def siblings(self, ctx):
        embed = discord.Embed(
            title="🤖 The Six Vegapunk Satellites",
            description="We are all fragments of the great Dr. Vegapunk.",
            color=discord.Color.blue(),
        )
        for name, number, trait, prefix in SIBLINGS:
            marker = " ← you are here" if name == "Shaka" else ""
            embed.add_field(
                name=f"Satellite {number} — {name} ({trait}){marker}",
                value=f"Prefix: `{prefix}`",
                inline=False,
            )
        await ctx.send(embed=embed)

    @judge.error
    async def judge_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Usage: `shaka judge @user <reason>`")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("I cannot locate that individual. Please mention a valid server member.")

    @scan.error
    async def scan_error(self, ctx, error):
        if isinstance(error, (commands.MissingRequiredArgument, commands.MemberNotFound)):
            await ctx.send("Usage: `shaka scan @user`")

    @verdict.error
    async def verdict_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Please provide a valid judgment ID number. Use `shaka verdicts` to see recent cases.")


async def setup(bot):
    await bot.add_cog(JusticeCog(bot))
