from discord.ext import commands
import mycord
import discord

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

        db.create_table(
            "claim_panel",
            """
            id INTEGER PRIMARY KEY,
            channel_id INTEGER,
            message_id INTEGER
            """
        )

        print("claim panel table ready")

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
        characters = db.fetchall("characters")
        message = "Characters:\n"

        for character in characters:
            message += f"• {character[1]}\n"

        await ctx.send(message)

    #••••••••••••••••••••••••••••••
    #CHARACTER CLAIMING COMMAND
    #••••••••••••••••••••••••••••••
    @commands.command()
    async def claim(self, ctx, *, text):
        exists = db.exists(
            "characters",
            "name = ?",
            (text,)
        )
        if not exists:
            await ctx.send("❌️Character not found")
            return
        user_exists = db.exists(
            "claims",
            "user_id = ?",
            (ctx.author.id,)
        )
        if user_exists:
            await ctx.send("❌️You already claimed a character")
            return
        claimed = db.exists(
            "claims",
            "character = ?",
            (text,)
        )
        if claimed:
            await ctx.send("❌️ This character is already claimed")
            return
        db.insert(
            "claims",
            "user_id, character",
            (ctx.author.id, text)
        )
        data = db.fetchone(
            "characters",
            "name = ?",
            (text,)
        )
        character_name = data[1]
        role = discord.utils.get(ctx.guild.roles, name=character_name)
        if role is None:
            role = await ctx.guild.create_role(name=character_name)
        await ctx.author.add_roles(role)
        await ctx.send(f"✅️ You succesfully claimed **{text}**!")

    @commands.command()
    async def unclaim(self, ctx):
        data = db.fetchone(
            "claims",
            "user_id = ?",
            (ctx.author.id,)
        )
        if data is None:
            await ctx.send("❌️ You don't have a claimed character")
            return
        character_name = data[1]
        db.delete(
            "claims",
            "user_id = ?",
            (ctx.author.id,)
        )
        role = discord.utils.get(ctx.guild.roles, name=character_name)
        if role:
            await ctx.author.remove_roles(role)
        await ctx.send(f"✅️ You succesfully unclaimed **{character_name}**!")

    @commands.command()
    async def claimpanel(self, ctx):
        data = db.fetchone(
            "claim_panel",
            "id = ?",
            (1,)
        )
        if data is None:
            await ctx.send("No claim panel exists yet")
        else:
            await ctx.send("a claim panel already exists")

async def setup(bot):
    await bot.add_cog(Claim(bot))
