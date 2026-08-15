import discord
from discord.ext import commands


class Welcome(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):

        channel = discord.utils.get(
            member.guild.text_channels,
            name="welcome"
        )

        if not channel:
            return

        embed = discord.Embed(
            title="🏴‍☠️ Welcome!",
            description=(
                f"Welcome to **{member.guild.name}**, "
                f"{member.mention}!\n\n"
                "We're glad to have you here. ⚓"
            ),
            color=discord.Color.blue()
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        embed.set_footer(
            text=f"Member #{member.guild.member_count}"
        )

        await channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Welcome(bot))
