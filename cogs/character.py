from discord.ext import commands
import mycord
import re
import discord

db = mycord.DB()

def normalize_name(name):
    name = name.lower()
    name = re.sub(r"[^a-z0-9]", "", name)
    return name

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
        characters = db.fetchall("characters")

        exists = False
        character = None
        for row in characters:
            if normalize_name(row[1]) == normalize_name(text):
                exists = True
                character = row
                break

        if not exists:
            await ctx.send("❌️ Character not found")
            return

        character_name = character[1]
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
            (character_name,)
        )
        if claimed:
            await ctx.send("❌️ This character is already claimed")
            return
        db.insert(
            "claims",
            "user_id, character",
            (ctx.author.id, character_name)
        )
        role = discord.utils.get(ctx.guild.roles, name=character_name)
        if role is None:
            role = await ctx.guild.create_role(name=character_name)
        await ctx.author.add_roles(role)
        await ctx.author.edit(nick=character_name)
        data = db.fetchone(
            "claim_panel",
            "id = ?",
            (1,)
        )

        if data:
            channel = self.bot.get_channel(data[1])
            message = await channel.fetch_message(data[2])

            claims = db.fetchall("claims")

            if claims:
                description = ""

                for claim in claims:
                    description += f"• <@{claim[0]}> — **{claim[1]}**\n"
            else:
                description = "No characters have been claimed yet."

            embed = discord.Embed(
                title="🏴‍☠️ Claimed Characters",
                description=description
            )

            await message.edit(embed=embed)
        print(normalize_name(text))
        await ctx.send(f"✅️ You succesfully claimed **{character_name}**!")

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
            data = db.fetchone(
            "claim_panel",
            "id = ?",
            (1,)
        )

        if data:
            channel = self.bot.get_channel(data[1])
            message = await channel.fetch_message(data[2])

            claims = db.fetchall("claims")

            if claims:
                description = ""

                for claim in claims:
                    description += f"• <@{claim[0]}> — **{claim[1]}**\n"
            else:
                description = "No characters have been claimed yet."

            embed = discord.Embed(
                title="🏴‍☠️ Claimed Characters",
                description=description
            )

            await message.edit(embed=embed)
        await ctx.send(f"✅️ You succesfully unclaimed **{character_name}**!")

    @commands.command()
    async def claimpanel(self, ctx):
        data = db.fetchone(
            "claim_panel",
            "id = ?",
            (1,)
        )
        if data is None:
            claims = db.fetchall("claims")
            if claims:
                description = ""
                for claim in claims:
                    description += f"•<@{claim[0]}> — **{claim[1]}**\n"
            else:
                description = "No characters have been claimed yet."
            embed = discord.Embed(title="🏴‍☠️ Claimed Characters", description=description)
            message = await ctx.send(embed=embed)
            db.insert(
                "claim_panel",
                "id, channel_id, message_id",
                (1, ctx.channel.id, message.id)
            )
        else:
            channel = self.bot.get_channel(data[1])
            message = await channel.fetch_message(data[2])

            claims = db.fetchall("claims")

            if claims:
                description = ""

                for claim in claims:
                    description += f"• <@{claim[0]}> — **{claim[1]}**\n"
            else:
                description = "No characters have been claimed yet."

            embed = discord.Embed(
                title="🏴‍☠️ Claimed Characters",
                description=description
            )

            await message.edit(embed=embed)

async def setup(bot):
    await bot.add_cog(Claim(bot))
