# cogs/bounties.py

import discord
from discord.ext import commands
import sqlite3
import os


MARINE_WEBHOOK = "https://discord.com/api/webhooks/1524398186725380236/yIXwVf1n6Kc4FpeC6y5Lb7ntfYdZv57pBSnKInGeUzb5GqnHd8DN6O5fYtrDSRaOvayW"


class Bounties(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        os.makedirs("data", exist_ok=True)

        self.db = sqlite3.connect("data/bounties.db")
        self.cursor = self.db.cursor()

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS bounties (
            user_id INTEGER PRIMARY KEY,
            bounty INTEGER DEFAULT 0
        )
        """)

        self.db.commit()


    def get_bounty(self, user_id):
        self.cursor.execute(
            "SELECT bounty FROM bounties WHERE user_id = ?",
            (user_id,)
        )

        result = self.cursor.fetchone()

        return result[0] if result else 0


    def change_bounty(self, user_id, amount):
        current = self.get_bounty(user_id)
        new_amount = max(0, current + amount)

        self.cursor.execute("""
        INSERT INTO bounties (user_id, bounty)
        VALUES (?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET bounty = ?
        """, (user_id, new_amount, new_amount))

        self.db.commit()

        return new_amount


    async def marine_announce(self, message):
        webhook = discord.Webhook.from_url(
            MARINE_WEBHOOK,
            client=self.bot
        )

        embed = discord.Embed(
            title="⚓ MARINE HEADQUARTERS",
            description=message,
            color=discord.Color.blue()
        )

        await webhook.send(embed=embed)


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def addbounty(self, ctx, member: discord.Member, amount: int):

        total = self.change_bounty(member.id, amount)

        await ctx.send(
            f"☠️ {member.mention} bounty increased by **{amount:,}**\n"
            f"Total bounty: **{total:,}**"
        )

        await self.marine_announce(
            f"🚨 WANTED UPDATE 🚨\n\n"
            f"Pirate: {member}\n"
            f"Bounty Added: {amount:,}\n"
            f"New Bounty: {total:,}"
        )


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def removebounty(self, ctx, member: discord.Member, amount: int):

        total = self.change_bounty(member.id, -amount)

        await ctx.send(
            f"⚓ {member.mention} bounty decreased by **{amount:,}**\n"
            f"Total bounty: **{total:,}**"
        )

        await self.marine_announce(
            f"⚓ MARINE RECORD UPDATE ⚓\n\n"
            f"Pirate: {member}\n"
            f"Bounty Removed: {amount:,}\n"
            f"New Bounty: {total:,}"
        )


async def setup(bot):
    await bot.add_cog(Bounties(bot))
