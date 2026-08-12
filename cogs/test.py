from discord.ext import commands
from punksdb import db


class PunksDBTest(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def dbtest(self, ctx):

        try:

            db.create_table(
                "test",
                {
                    "id": "INTEGER PRIMARY KEY",
                    "message": "TEXT"
                }
            )

            db.insert(
                "test",
                {
                    "message": "PunksDB works!"
                }
            )

            result = db.fetchone(
                "test",
                "message = ?",
                ("PunksDB works!",)
            )

            await ctx.send(
                f"🧪 PunksDB result: `{result}`"
            )

        except Exception as e:

            await ctx.send(
                f"❌ PunksDB error:\n```py\n{e}\n```"
            )


async def setup(bot):
    await bot.add_cog(PunksDBTest(bot))
