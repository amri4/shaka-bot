from discord.ext import commands


@commands.command()
async def test(ctx):
    await ctx.send("Loader works!")
