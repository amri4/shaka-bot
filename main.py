import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import shared_db

load_dotenv()

# Init DB safely
shared_db.init_db()


intents = discord.Intents.default()
intents.message_content = True
intents.members = True


EXTENSIONS = [
    "cogs.help_command",
    "cogs.admin",
]


# Custom bot class (FIX: proper setup_hook)
class ShakaBot(commands.Bot):
    async def setup_hook(self):
        for ext in EXTENSIONS:
            try:
                await self.load_extension(ext)
                print(f"[SHAKA] Loaded {ext}")
            except Exception as e:
                print(f"[SHAKA] Failed to load {ext}: {e}")


# Cleaner prefix handler (FIX)
def prefix(bot, message):
    return ["shaka ", "Shaka "]


bot = ShakaBot(
    command_prefix=prefix,
    intents=intents,
    help_command=None,
)


@bot.event
async def on_ready():
    print(f"[SHAKA] Online as {bot.user} | Satellite 01 — Good (Central DB)")
    print(f"[SHAKA] DB path: {shared_db.get_db_path()}")
    print(f"[SHAKA] Guilds: {len(bot.guilds)}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            f"Missing argument: `{error.param.name}`. Use `shaka help` for usage."
        )
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("Member not found. Mention them directly.")
    else:
        cmd = ctx.command if ctx.command else "Unknown"
        print(f"[SHAKA] Error in {cmd}: {error}")


# Token safety check (FIX)
token = os.getenv("DISCORD_TOKEN")
if not token:
    raise RuntimeError("DISCORD_TOKEN not found in environment variables")


bot.run(token)
