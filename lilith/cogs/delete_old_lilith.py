import mycord
from discord.ext import commands


db = mycord.PunksDB()


class DeleteOldLilith(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        old_tables = [
            "mod_cases",
            "case_actions",
            "case_history"
        ]

        for table in old_tables:

            db.drop_table(table)

            print(f"🗑️ Deleted: {table}")

        print(
            "✅ Old Lilith moderation system removed."
        )


async def setup(bot):
    await bot.add_cog(
        DeleteOldLilith(bot)
      )
