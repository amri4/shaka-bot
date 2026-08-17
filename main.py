import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()


# =========================================
# BOT CONFIGURATION
# =========================================

BOT_CONFIG = {
    "Lilith": {
        "prefix": "Lilith ",
        "folder": "lilith",
        "token": "LILITH_TOKEN"
    },

    "Shaka": {
        "prefix": "Shaka ",
        "folder": "shaka",
        "token": "SHAKA_TOKEN"
    },

    "Pythagoras": {
        "prefix": "Pythagoras ",
        "folder": "pythagoras",
        "token": "PYTHAGORAS_TOKEN"
    },

    "York": {
        "prefix": "York ",
        "folder": "york",
        "token": "YORK_TOKEN"
    },

    "Edison": {
        "prefix": "Edison ",
        "folder": "edison",
        "token": "EDISON_TOKEN"
    },

    "Atlas": {
        "prefix": "Atlas ",
        "folder": "atlas",
        "token": "ATLAS_TOKEN"
    }
}


# =========================================
# CREATE BOTS
# =========================================

bots = {}


for name, config in BOT_CONFIG.items():

    intents = discord.Intents.default()

    intents.message_content = True
    intents.members = True

    bot = commands.Bot(
        command_prefix=config["prefix"],
        help_command=None,
        intents=intents
    )

    # Store the satellite name.
    # The hierarchy system can use this
    # to identify which bot a command belongs to.
    bot.satellite_name = name

    bots[name] = bot


# =========================================
# LOAD COGS
# =========================================

async def load_cogs(
    bot,
    name,
    folder
):

    print(
        f"📂 {name}: Scanning for cogs..."
    )

    cog_folder = f"./{folder}/cogs"

    if not os.path.exists(cog_folder):

        print(
            f"⚠️ {name}: No 'cogs' folder found."
        )

        return

    for filename in os.listdir(cog_folder):

        if (
            filename.endswith(".py")
            and not filename.startswith("__")
        ):

            extension = (
                f"{folder}.cogs.{filename[:-3]}"
            )

            try:

                await bot.load_extension(
                    extension
                )

                print(
                    f"  └─ {name} loaded cog: "
                    f"{filename}"
                )

            except Exception as e:

                print(
                    f"  ❌ {name} failed to load "
                    f"{filename}: {e}"
                )


# =========================================
# READY EVENTS
# =========================================

def setup_ready_event(
    bot,
    name
):

    @bot.event
    async def on_ready():

        print(
            f"🤖 {name} logged in as "
            f"{bot.user}"
        )

        print(
            f"⚡ {name} is online and listening."
        )


# =========================================
# START ONE BOT
# =========================================

async def start_bot(
    name,
    bot,
    config
):

    token = os.getenv(
        config["token"]
    )

    if not token:

        print(
            f"❌ {name}: "
            f"'{config['token']}' is missing!"
        )

        return

    await load_cogs(
        bot,
        name,
        config["folder"]
    )

    setup_ready_event(
        bot,
        name
    )

    try:

        await bot.start(
            token
        )

    except Exception as e:

        print(
            f"❌ {name} stopped: {e}"
        )


# =========================================
# MAIN
# =========================================

async def main():

    print(
        "🚀 Starting Vegapunk satellite system..."
    )

    tasks = []

    for name, config in BOT_CONFIG.items():

        tasks.append(
            start_bot(
                name,
                bots[name],
                config
            )
        )

    await asyncio.gather(
        *tasks
    )


# =========================================
# RUN
# =========================================

try:

    asyncio.run(
        main()
    )

except KeyboardInterrupt:

    print(
        "\n🛑 All satellites stopped."
    )
