import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import database

load_dotenv()

SIBLING_NAMES = ["Lilith", "Edison", "Pythagoras", "Atlas", "York"]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="shaka", intents=intents, help_command=None)


@bot.event
async def on_ready():
    database.init_db()
    await bot.load_extension("cogs.help_command")
    await bot.load_extension("cogs.justice")
    print(f"[Shaka] Online as {bot.user} (ID: {bot.user.id})")
    print(f"[Shaka] Prefix: shaka | Satellite 01 — Good")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content_lower = message.content.lower()
    for name in SIBLING_NAMES:
        if name.lower() in content_lower:
            responses = [
                f"I have noted the mention of {name}. They are one of us — Satellite fragments of Vegapunk.",
                f"{name}... I monitor their activities closely. Logic demands it.",
                f"Ah, {name}. We share the same origin. That is where the similarities end.",
            ]
            import random
            await message.channel.send(random.choice(responses))
            break

    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error


if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN not set in .env")
    bot.run(token)
