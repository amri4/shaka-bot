from discord.ext import commands
from ..buttons.test import test_button


@commands.command()
async def test(ctx):
    embed = discord.Embed(title="embed works", description="embed, command and loader works", color=discord.Color.green())
    await ctx.send(embed=embed, view=ui(test_button))
