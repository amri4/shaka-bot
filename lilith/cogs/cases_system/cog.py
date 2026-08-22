from utils.discord_setup import setup_system


async def setup(bot):

    print("🔥 SYSTEM COG LOADED")

    print(
        "📦 PACKAGE:",
        __package__
    )

    await setup_system(
        bot,
        __package__
    )
