from discord.ext import commands
import mycord

db = mycord.DB()

#==========================================
#CHARACTER CLAIM CLASS
#==========================================
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

    #••••••••••••••••••••••••••••••
    #ADDING A CHARACTER COMMAND
    #••••••••••••••••••••••••••••••
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def addcharacter(self, ctx, *, text):
        exists = db.exists(
            "characters",
            "name = ?",
            (text,)
        )

        if exists:
            await ctx.send("🚫 Character already exists.")
        else:
            db.insert(
                "characters",
                "name",
                (text,)
            )
            await ctx.send(f"✅️ Added **{text}**")
            print("addcharacter working")
    print("addcharacter functioning")

    #••••••••••••••••••••••••••••••
    #SHOW ALL CHARACTERS
    #••••••••••••••••••••••••••••••
    @commands.command()
    async def characters(self, ctx):
        print("triggered")
        characters = db.fetchall("characters")
        message = "Characters:\n"
        for character in characters:
            message += f"• {character[1]}\n"
        await ctx.send(message)

async def setup(bot):
    await bot.add_cog(Claim(bot))
