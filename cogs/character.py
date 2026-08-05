# cogs/character.py

import discord
from discord.ext import commands

from views.character import CharacterView
from utils import characters


class Character(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Register the persistent button
        self.bot.add_view(CharacterView())

    @commands.command(
        name="characterpanel",
        aliases=["characters", "claimpanel"]
    )
    @commands.has_permissions(administrator=True)
    async def characterpanel(self, ctx):

        total = len(characters.all())
        claimed = sum(
            1
            for c in characters.all()
            if c["claimed_by"] is not None
        )

        embed = discord.Embed(
            title="🎭 Character Selection",
            description=(
                "Every pirate, marine, revolutionary, and civilian has a story.\n\n"
                "Press **Claim Character** below to choose the canon character you wish to roleplay.\n\n"
                "### Rules\n"
                "• One character per member.\n"
                "• Every character can only be claimed once.\n"
                "• Nicknames will automatically update.\n"
                "• Staff can revoke inactive claims.\n"
            ),
            color=0xf4c542
        )

        embed.add_field(
            name="📚 Characters",
            value=f"**{claimed}/{total}** claimed",
            inline=True
        )

        embed.add_field(
            name="🌊 Server",
            value=ctx.guild.name,
            inline=True
        )

        embed.set_footer(
            text="The seas await your arrival."
        )

        await ctx.send(
            embed=embed,
            view=CharacterView()
        )

    @commands.command()
    async def character(self, ctx, *, name=None):

        if name is None:
            current = characters.get_user_character(ctx.author.id)

            if current is None:
                return await ctx.send(
                    "You haven't claimed a character."
                )

            name = current["name"]

        character = characters.search(name)

        if character is None:
            return await ctx.send(
                "Character not found."
            )

        embed = discord.Embed(
            title=character["name"],
            color=0x3498db
        )

        if character["claimed_by"] is None:
            embed.description = "✅ Available"
        else:
            member = ctx.guild.get_member(
                character["claimed_by"]
            )

            embed.description = (
                f"❌ Claimed by {member.mention}"
                if member
                else "❌ Claimed"
            )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Character(bot))
