import discord
from discord.ext import commands
import shared_db

TRUST_BAR = ["░░░░░░░░░░", "██░░░░░░░░", "████░░░░░░", "██████░░░░", "██████████"]


def trust_bar(trust):
    level, label, _ = shared_db.get_trust_level(trust)
    return TRUST_BAR[level], label


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="stats")
    async def stats(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        berries, trust, last_daily = shared_db.get_user(target.id, ctx.guild.id)
        level, label, multiplier = shared_db.get_trust_level(trust)
        bar, _ = trust_bar(trust)
        next_thresholds = [100, 300, 700, 1500, 99999]
        next_needed = next_thresholds[level] - trust if level < 4 else 0
        embed = discord.Embed(
            title=f"🧠 SHAKA — User Profile",
            color=discord.Color.blue(),
        )
        embed.set_author(name=target.display_name, icon_url=target.display_avatar.url)
        embed.add_field(name="🍓 Berries", value=f"**{berries:,}**", inline=True)
        embed.add_field(name="💜 Trust", value=f"**{trust}** pts", inline=True)
        embed.add_field(name="🏅 Trust Level", value=f"**{label}** (Lv.{level})", inline=True)
        embed.add_field(name="Trust Progress", value=f"`{bar}` {trust} pts\n{'Next level: ' + str(next_needed) + ' pts away' if level < 4 else '**MAX LEVEL**'}", inline=False)
        embed.add_field(name="Daily Multiplier", value=f"×{multiplier}", inline=True)
        embed.add_field(name="Last Daily", value=last_daily or "Never", inline=True)
        embed.set_footer(text="SHAKA — Central Memory Core | Satellite 01")
        await ctx.send(embed=embed)

    @commands.command(name="top")
    async def top(self, ctx):
        rows = shared_db.get_leaderboard(ctx.guild.id, by="berries")
        embed = discord.Embed(
            title="🧠 SHAKA — Berry Leaderboard",
            color=discord.Color.blue(),
        )
        if not rows:
            embed.description = "No data recorded yet."
        else:
            medals = ["🥇", "🥈", "🥉"]
            lines = []
            for i, (uid, berries, trust) in enumerate(rows):
                medal = medals[i] if i < 3 else f"`{i+1}.`"
                lines.append(f"{medal} <@{uid}> — **{berries:,}** 🍓")
            embed.description = "\n".join(lines)
        embed.set_footer(text="SHAKA — Central Memory Core | Satellite 01")
        await ctx.send(embed=embed)

    @commands.command(name="logs")
    async def logs(self, ctx):
        rows = shared_db.get_recent_transactions(ctx.guild.id)
        embed = discord.Embed(
            title="🧠 SHAKA — Recent Transactions",
            color=discord.Color.blue(),
        )
        if not rows:
            embed.description = "No transactions recorded yet."
        else:
            lines = []
            for from_id, to_id, amount, reason, ts in rows:
                sender = f"<@{from_id}>" if from_id else "System"
                receiver = f"<@{to_id}>" if to_id else "System"
                lines.append(f"`{ts[:10]}` {sender} → {receiver}: **{amount:,}** 🍓 _{reason or ''}_")
            embed.description = "\n".join(lines)
        embed.set_footer(text="SHAKA — Central Memory Core | Satellite 01")
        await ctx.send(embed=embed)

    @commands.command(name="give")
    @commands.has_permissions(administrator=True)
    async def give(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            await ctx.send("Amount must be positive.")
            return
        shared_db.add_berries(member.id, ctx.guild.id, amount, reason="Admin grant")
        embed = discord.Embed(
            title="🧠 SHAKA — Admin Transfer",
            description=f"Granted **{amount:,}** 🍓 to {member.mention}.",
            color=discord.Color.blue(),
        )
        embed.set_footer(text="SHAKA — Central Memory Core")
        await ctx.send(embed=embed)

    @commands.command(name="reset")
    @commands.has_permissions(administrator=True)
    async def reset(self, ctx, member: discord.Member):
        import sqlite3, os
        with shared_db.get_conn() as conn:
            conn.execute(
                "DELETE FROM users WHERE user_id = ? AND guild_id = ?",
                (str(member.id), str(ctx.guild.id)),
            )
            conn.commit()
        await ctx.send(f"User data for {member.mention} has been reset.")

    @commands.command(name="system")
    async def system(self, ctx):
        stats = shared_db.get_server_stats(ctx.guild.id)
        embed = discord.Embed(
            title="🧠 SHAKA — System Status",
            description="Central memory core is operational.",
            color=discord.Color.blue(),
        )
        embed.add_field(name="Registered Users", value=str(stats["total_users"]), inline=True)
        embed.add_field(name="Total Berries in Circulation", value=f"{stats['total_berries']:,} 🍓", inline=True)
        embed.add_field(name="Total Warnings Issued", value=str(stats["total_warnings"]), inline=True)
        embed.add_field(name="Times York Was Fed", value=str(stats["total_feeds"]), inline=True)
        embed.add_field(name="Average Trust Score", value=str(stats["avg_trust"]), inline=True)
        embed.add_field(name="DB Path", value=f"`{shared_db.get_db_path()}`", inline=False)
        embed.set_footer(text="SHAKA — Satellite 01 | All systems nominal.")
        await ctx.send(embed=embed)

    @give.error
    async def give_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Only administrators can use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Usage: `shaka give @user <amount>`")

    @reset.error
    async def reset_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Only administrators can use this command.")

    @stats.error
    async def stats_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("User not found.")


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
