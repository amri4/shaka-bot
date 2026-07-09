import discord
from discord.ext import commands
import mycord
import random

# =========================================
# DATABASE SETUP
# =========================================

db = mycord.Bot()

db.create_table(
    "bounty",
    """
    guild_id INTEGER,
    user_id INTEGER,
    bounty INTEGER,
    PRIMARY KEY (guild_id, user_id)
    """
)

# =========================================
# BOUNTY SYSTEM
# =========================================

def get_milestone(bounty):

    if bounty >= 10000:
        return "👑 Emperor Candidate"

    elif bounty >= 5000:
        return "☠️ Notorious Pirate"

    elif bounty >= 1000:
        return "🔴 Dangerous Pirate"

    elif bounty >= 500:
        return "🟠 Rising Threat"

    elif bounty >= 100:
        return "🟡 Rookie Pirate"

    else:
        return "🟤 Unknown Pirate"


# =========================================
# BOUNTY COG
# =========================================

class Bounty(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =====================================
    # AUTO BOUNTY GAIN
    # =====================================

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot or not message.guild:
            return

        exists = db.exists(
            "bounty",
            "guild_id = ? AND user_id = ?",
            (message.guild.id, message.author.id)
        )

        if not exists:

            db.insert(
                "bounty",
                "guild_id, user_id, bounty",
                (message.guild.id, message.author.id, 0)
            )

        data = db.fetchone(
            "bounty",
            "guild_id = ? AND user_id = ?",
            (message.guild.id, message.author.id)
        )

        current_bounty = data[2]

        gain = random.randint(5, 20)

        new_bounty = current_bounty + gain

        db.update(
            "bounty",
            "bounty = ?",
            "guild_id = ? AND user_id = ?",
            (new_bounty, message.guild.id, message.author.id)
        )

    # =====================================
    # VIEW BOUNTY
    # =====================================

    @commands.command()
    async def bounty(self, ctx, member: discord.Member = None):

        member = member or ctx.author

        if member.bot:
            await ctx.send("❌ Bots don't have bounties.")
            return

        data = db.fetchone(
            "bounty",
            "guild_id = ? AND user_id = ?",
            (ctx.guild.id, member.id)
        )

        if not data:
            await ctx.send("❌ No bounty found.")
            return

        _, _, bounty = data

        milestone = get_milestone(bounty)

        embed = discord.Embed(
            title=f"🏴‍☠️ {member.display_name}",
            description=(
                f"💰 Bounty: **{bounty:,}** <:berries:1506064566260338779>\n\n"
                f"{milestone}"
            ),
            color=discord.Color.gold()
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        await ctx.send(embed=embed)

    # =====================================
    # LEADERBOARD
    # =====================================

    @commands.command()
    async def bountylb(self, ctx):

        data = db.fetchall(
            "bounty",
            "guild_id = ?",
            (ctx.guild.id,)
        )

        if not data:
            await ctx.send("❌ No bounty data found.")
            return

        sorted_data = sorted(
            data,
            key=lambda x: x[2],
            reverse=True
        )

        medals = ["🥇", "🥈", "🥉"]

        text = ""

        for index, user in enumerate(sorted_data[:10], start=1):

            _, user_id, bounty = user

            member = self.bot.get_user(user_id)

            if not member:
                try:
                    member = await self.bot.fetch_user(user_id)
                except:
                    continue

            icon = medals[index - 1] if index <= 3 else f"**{index}.**"

            text += (
                f"{icon} {member.mention} — "
                f"💰 **{bounty:,}** "
                f"<:berries:1506064566260338779>\n"
            )

        embed = discord.Embed(
            title="🏴‍☠️ Bounty Leaderboard",
            description=text,
            color=discord.Color.gold()
        )

        await ctx.send(embed=embed)


# =========================================
# SETUP
# =========================================

async def setup(bot):
    await bot.add_cog(Bounty(bot))
