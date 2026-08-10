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
            guild_id INTEGER,
            user_id INTEGER,
            character TEXT,
            UNIQUE(guild_id, user_id),
            UNIQUE(guild_id, character)
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
            guild_id INTEGER PRIMARY KEY,
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
        input_name = normalize_name(text)

        matches = []

        for row in characters:
            full_name = normalize_name(row[1])
            input_name = normalize_name(text)

            parts = [
                normalize_name(part)
                for part in row[1].split()
            ]

            if full_name == input_name or input_name == parts[-1]:
                matches.append(row)

        if not matches:
            await ctx.send("❌️ Character not found")
            return

        if len(matches) > 1:
            emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣",
                      "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

            matches = matches[:10]

            description = ""

            for i, row in enumerate(matches):
                description += f"{emojis[i]} **{row[1]}**\n"

            embed = discord.Embed(
                title="🏴‍☠️ Which character do you mean?",
                description=description
            )

            message = await ctx.send(embed=embed)

            for emoji in emojis[:len(matches)]:
                await message.add_reaction(emoji)

            def check(reaction, user):
                return (
                    user == ctx.author
                    and reaction.message.id == message.id
                    and str(reaction.emoji) in emojis[:len(matches)]
                )

            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add",
                    timeout=30,
                    check=check
                )
            except TimeoutError:
                await message.edit(
                    embed=discord.Embed(
                        title="⏱️ Selection expired",
                        description="You didn't choose a character in time."
                    )
                )
                return

            selected_index = emojis.index(str(reaction.emoji))
            character = matches[selected_index]
        else:
            character = matches[0]

        character_name = character[1]

        
        user_exists = db.exists(
            "claims",
            "guild_id = ? AND user_id = ?",
            (ctx.guild.id, ctx.author.id)
        )
        if user_exists:
            await ctx.send("❌️You already claimed a character")
            return
        claimed = db.exists(
            "claims",
            "guild_id = ? AND character = ?",
            (ctx.guild.id, character_name)
        )
        if claimed:
            await ctx.send("❌️ This character is already claimed")
            return
        db.insert(
            "claims",
            "guild_id, user_id, character",
            (ctx.guild.id, ctx.author.id, character_name)
        )
        role = discord.utils.get(ctx.guild.roles, name=character_name)
        if role is None:
            role = await ctx.guild.create_role(name=character_name)
        await ctx.author.add_roles(role)
        try:
            await ctx.author.edit(nick=character_name)
        except discord.Forbidden:
            print("Cannot change nickname")
        data = db.fetchone(
            "claim_panel",
            "guild_id = ?",
            (ctx.guild.id,)
        )

        if data:
            channel = self.bot.get_channel(data[1])
            message = await channel.fetch_message(data[2])

            claims = db.fetchall("claims")
            claims = [
                claim for claim in claims
                if claim[0] == ctx.guild.id
            ]

            if claims:
                description = ""

                for claim in claims:
                    description += f"• <@{claim[1]}> — **{claim[2]}**\n"
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
            "guild_id = ? AND user_id = ?",
            (ctx.guild.id, ctx.author.id)
        )
        if data is None:
            await ctx.send("❌️ You don't have a claimed character")
            return
        character_name = data[2]
        db.delete(
            "claims",
            "guild_id = ? AND user_id = ?",
            (ctx.guild.id, ctx.author.id)
        )
        role = discord.utils.get(ctx.guild.roles, name=character_name)
        if role:
            await ctx.author.remove_roles(role)
            await ctx.author.edit(nick=None)
            data = db.fetchone(
            "claim_panel",
            "guild_id = ?",
            (ctx.guild.id,)
        )

        if data:
            channel = self.bot.get_channel(data[1])
            message = await channel.fetch_message(data[2])

            claims = db.fetchall("claims")
            claims = [
                claim for claim in claims
                if claim[0] == ctx.guild.id
            ]

            if claims:
                description = ""

                for claim in claims:
                    description += f"• <@{claim[1]}> — **{claim[2]}**\n"
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
            "guild_id = ?",
            (ctx.guild.id,)
        )
        if data is None:
            claims = db.fetchall("claims")
            claims = [
                claim for claim in claims
                if claim[0] == ctx.guild.id
            ]
            if claims:
                description = ""
                for claim in claims:
                    description += f"•<@{claim[1]}> — **{claim[2]}**\n"
            else:
                description = "No characters have been claimed yet."
            embed = discord.Embed(title="🏴‍☠️ Claimed Characters", description=description)
            message = await ctx.send(embed=embed)
            db.insert(
                "claim_panel",
                "guild_id, channel_id, message_id",
                (ctx.guild.id, ctx.channel.id, message.id)
            )
        else:
            channel = self.bot.get_channel(data[1])
            message = await channel.fetch_message(data[2])

            claims = db.fetchall("claims")
            claims = [
                claim for claim in claims
                if claim[0] == ctx.guild.id
            ]

            if claims:
                description = ""

                for claim in claims:
                    description += f"• <@{claim[1]}> — **{claim[2]}**\n"
            else:
                description = "No characters have been claimed yet."

            embed = discord.Embed(
                title="🏴‍☠️ Claimed Characters",
                description=description
            )

            await message.edit(embed=embed)

async def setup(bot):
    await bot.add_cog(Claim(bot))
