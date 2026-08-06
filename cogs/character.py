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

        db.create_table(
            "characters",
            """
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE
            """
        )

        print("characters table ready")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def addcharacter(self, ctx, *, text):
        data = db.fetchall("characters")
        if data is None:
            db.insert(
                "characters",
                "name",
                (text,)
            )

async def setup(bot):
    await bot.add_cog(Claim(bot))
