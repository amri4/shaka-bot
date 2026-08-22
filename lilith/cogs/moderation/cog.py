from utils.loader import load


async def setup(bot):
    await load(bot, __package__)
