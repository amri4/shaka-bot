import os
import random
import discord
from discord.ext import commands
from dotenv import load_dotenv
import database

load_dotenv()

SIBLING_NAMES = ["Lilith", "Edison", "Pythagoras", "Atlas", "York"]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True


class ShakaBot(commands.Bot):
    async def setup_hook(self):
        database.init_db()
        for ext in ["cogs.help_command", "cogs.justice"]:
            try:
                await self.load_extension(ext)
                print(f"[Shaka] Loaded {ext}")
            except Exception as e:
                print(f"[Shaka] ERROR loading {ext}: {e}")


bot = ShakaBot(
    command_prefix=("shaka ", "shaka", "Shaka ", "Shaka"),
    intents=intents,
    help_command=None,
)


@bot.event
async def on_ready():
    print(f"[Shaka] Online as {bot.user} (ID: {bot.user.id})")
    print(f"[Shaka] Prefix: shaka  | Satellite 01 — Good")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content_lower = message.content.lower()
    for name in SIBLING_NAMES:
        if name.lower() in content_lower:
            responses = [
                f"I have noted the mention of {name}. They are one of us — Satellite fragments of Vegapunk.",
g                f"{name}... I monitor their activities closely. Logic demands it.",
                f"Ah, {name}. We share the same origin. That is where the similarities end.",
            ]
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
