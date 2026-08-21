from utils.discord_setup import setup_system


async def setup(bot):
    await setup_system(bot, __package__)
