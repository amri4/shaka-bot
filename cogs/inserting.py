from discord.ext import commands
import mycord
from characters_1 import CHARACTERS


db = mycord.PunksDB()


class CharacterDatabase(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        # Create table
        db.create_table(
            "characters",
            "id INTEGER PRIMARY KEY, name TEXT UNIQUE"
        )

        # Add characters
        added = 0

        for character_id, name in enumerate(CHARACTERS, start=1):

            if db.exists(
                "characters",
                "name = ?",
                (name,)
            ):
                continue

            db.insert(
                "characters",
                "id, name",
                (character_id, name)
            )

            added += 1

        print(
            f"✅ Characters loaded: {added} new / "
            f"{len(CHARACTERS)} total"
        )


async def setup(bot):
    await bot.add_cog(CharacterDatabase(bot))
