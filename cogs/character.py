from discord.ext import commands
import mycord

db = mycord.DB()


class Claim(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        db.create_table(
            "claims",
            """
            user_id INTEGER PRIMARY KEY,
            character TEXT UNIQUE
            """
        )

        print("Claims table ready!")


async def setup(bot):
    await bot.add_cog(Claim(bot))
