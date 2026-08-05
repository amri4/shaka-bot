# cogs/character_admin.py

import discord
from discord.ext import commands

from utils import characters
from import_characters import db


class CharacterAdmin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def unclaim(self, ctx, *, character):

        found = characters.search(character)

        if found is None:
            return await ctx.send("❌ Character not found.")

        characters.unclaim(found["name"])

        await ctx.send(
            f"✅ **{found['name']}** is now available again."
        )

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def forceclaim(self, ctx, member: discord.Member, *, character):

        if characters.user_has_character(member.id):
            return await ctx.send(
                "❌ That member already owns a character."
            )

        found = characters.search(character)

        if found is None:
            return await ctx.send(
                "❌ Character not found."
            )

        if found["claimed_by"] is not None:
            return await ctx.send(
                "❌ Character already claimed."
            )

        characters.claim(
            member.id,
            found["name"]
        )

        try:
            await member.edit(
                nick=found["name"]
            )
        except Exception:
            pass

        await ctx.send(
            f"✅ {member.mention} is now **{found['name']}**."
        )

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def resetclaims(self, ctx):

        confirm = discord.ui.View(timeout=30)

        class Yes(discord.ui.Button):

            def __init__(self):
                super().__init__(
                    label="Reset",
                    style=discord.ButtonStyle.red
                )

            async def callback(self, interaction):

                if interaction.user != ctx.author:
                    return await interaction.response.send_message(
                        "❌ Only the command author can use this.",
                        ephemeral=True
                    )

                for character in characters.all():

                    if character["claimed_by"] is not None:
                        characters.unclaim(character["name"])

                await interaction.response.edit_message(
                    content="✅ All character claims have been reset.",
                    embed=None,
                    view=None
                )

        class Cancel(discord.ui.Button):

            def __init__(self):
                super().__init__(
                    label="Cancel",
                    style=discord.ButtonStyle.gray
                )

            async def callback(self, interaction):

                if interaction.user != ctx.author:
                    return

                await interaction.response.edit_message(
                    content="Cancelled.",
                    embed=None,
                    view=None
                )

        confirm.add_item(Yes())
        confirm.add_item(Cancel())

        await ctx.send(
            "⚠️ Reset every claimed character?",
            view=confirm
        )

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def characterstats(self, ctx):

        all_characters = characters.all()

        claimed = len(
            [
                c
                for c in all_characters
                if c["claimed_by"] is not None
            ]
        )

        available = len(all_characters) - claimed

        embed = discord.Embed(
            title="📊 Character Statistics",
            color=0x3498db
        )

        embed.add_field(
            name="Characters",
            value=len(all_characters)
        )

        embed.add_field(
            name="Claimed",
            value=claimed
        )

        embed.add_field(
            name="Available",
            value=available
        )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(CharacterAdmin(bot))
