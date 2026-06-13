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
    user_id INTEGER PRIMARY KEY,
    bounty INTEGER
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

# ============================================
# CREATE BOUNTY COG
# ============================================

class Bounty(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =====================================
    # AUTO CREATE + ADD BOUNTY PER MESSAGE
    # =====================================

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        exists = db.exists(
            "bounty",
            "user_id = ?",
            (message.author.id,)
        )

        if not exists:

            db.insert(
                "bounty",
                "user_id, bounty",
                (message.author.id, 0)
            )

        data = db.fetchone(
            "bounty",
            "user_id = ?",
            (message.author.id,)
        )

        current_bounty = data[1]

        gain = random.randint(5, 20)

        new_bounty = current_bounty + gain

        db.update(
            "bounty",
            "bounty = ?",
            "user_id = ?",
            (new_bounty, message.author.id)
        )

    # =====================================
    # VIEW BOUNTY
    # =====================================

    @commands.command()
    async def bounty(self, ctx, member: discord.Member = None):

        member = member or ctx.author

        data = db.fetchone(
            "bounty",
            "user_id = ?",
            (member.id,)
        )

        if not data:
            await ctx.send("❌ No bounty found")
            return

        user_id, bounty = data
        milestone = get_milestone(bounty)

        embed = discord.Embed(
            title=f"🏴‍☠️ {member.mention}",
            description=f"💰 Bounty: **{bounty:,}**<:berries:1506064566260338779>\n\n **{milestone}**",
            color=discord.Color.gold()
        )

        await ctx.send(embed=embed)

    # =====================================
    # LEADERBOARD
    # =====================================

    @commands.command()
    async def bountylb(self, ctx):

        data = db.fetchall("bounty")

        if not data:
            await ctx.send("❌ No bounty data")
            return

        sorted_data = sorted(
            data,
            key=lambda x: x[1],
            reverse=True
        )

        text = ""

        for index, user in enumerate(sorted_data, start=1):

            user_id, bounty = user

            member = self.bot.get_user(user_id)

            if member:
                text += (
                    f"**{index}.** "
                    f"{member.mention} — "
                    f"💰 {bounty:,}\n"
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
