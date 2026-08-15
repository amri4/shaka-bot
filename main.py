import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
import mycord


load_dotenv()


# =========================================
# SHAKA
# =========================================

shaka_intents = discord.Intents.default()
shaka_intents.message_content = True
shaka_intents.members = True

shaka = commands.Bot(
    command_prefix="Shaka ",
    help_command=None,
    intents=shaka_intents
)


# =========================================
# PYTHAGORAS
# =========================================

pythagoras_intents = discord.Intents.default()
pythagoras_intents.message_content = True
pythagoras_intents.members = True

pythagoras = commands.Bot(
    command_prefix="Pythagoras ",
    help_command=None,
    intents=pythagoras_intents
)


# =========================================
# LOAD SHAKA COGS
# =========================================

async def load_shaka_cogs():

    print("📂 Shaka: Scanning for cogs...")

    folder = "./shaka/cogs"

    if not os.path.exists(folder):
        print("⚠️ Shaka: No 'cogs' folder found.")
        return

    for filename in os.listdir(folder):

        if filename.endswith(".py") and not filename.startswith("__"):

            try:

                await shaka.load_extension(
                    f"shaka.cogs.{filename[:-3]}"
                )

                print(
                    f"  └─ Shaka loaded cog: {filename}"
                )

            except Exception as e:

                print(
                    f"  ❌ Shaka failed to load "
                    f"{filename}: {e}"
                )


# =========================================
# LOAD PYTHAGORAS COGS
# =========================================

async def load_pythagoras_cogs():

    print("📂 Pythagoras: Scanning for cogs...")

    folder = "./pythagoras/cogs"

    if not os.path.exists(folder):
        print("⚠️ Pythagoras: No 'cogs' folder found.")
        return

    for filename in os.listdir(folder):

        if filename.endswith(".py") and not filename.startswith("__"):

            try:

                await pythagoras.load_extension(
                    f"pythagoras.cogs.{filename[:-3]}"
                )

                print(
                    f"  └─ Pythagoras loaded cog: {filename}"
                )

            except Exception as e:

                print(
                    f"  ❌ Pythagoras failed to load "
                    f"{filename}: {e}"
                )


# =========================================
# SHAKA READY
# =========================================

@shaka.event
async def on_ready():

    print(
        f"🤖 Shaka logged in as {shaka.user.name}"
    )

    print("⚡ Shaka is online and listening.")


# =========================================
# PYTHAGORAS READY
# =========================================

@pythagoras.event
async def on_ready():

    print(
        f"🤖 Pythagoras logged in as "
        f"{pythagoras.user.name}"
    )

    print("⚡ Pythagoras is online and listening.")


# =========================================
# MAIN
# =========================================

async def main():

    await load_shaka_cogs()
    await load_pythagoras_cogs()

    shaka_token = os.getenv("SHAKA_TOKEN")
    pythagoras_token = os.getenv("PYTHAGORAS_TOKEN")

    if not shaka_token:
        print("❌ 'SHAKA_TOKEN' is missing!")
        return

    if not pythagoras_token:
        print("❌ 'PYTHAGORAS_TOKEN' is missing!")
        return

    await asyncio.gather(
        shaka.start(shaka_token),
        pythagoras.start(pythagoras_token)
    )


asyncio.run(main())
