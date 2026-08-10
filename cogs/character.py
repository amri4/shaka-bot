from discord.ext import commands
import mycord
import re
import discord
import asyncio

db = mycord.DB()


def normalize_name(name):
    name = name.lower()
    name = re.sub(r"[^a-z0-9]", "", name)
    return name


# ==========================================
# CHARACTER CLAIM CLASS
# ==========================================
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

        print("Characters table ready!")

        db.create_table(
            "claim_panel",
            """
            guild_id INTEGER PRIMARY KEY,
            channel_id INTEGER,
            message_id INTEGER
            """
        )

        print("Claim panel table ready!")

    # ==========================================
    # UPDATE CLAIM PANEL
    # ==========================================
    async def update_panel(self, guild_id):

        data = db.fetchone(
            "claim_panel",
            "guild_id = ?",
            (guild_id,)
        )

        if data is None:
            return

        channel = self.bot.get_channel(data[1])

        if channel is None:
            return

        try:
            message = await channel.fetch_message(data[2])
        except (discord.NotFound, discord.Forbidden):
            return

        claims = db.fetchall("claims")

        claims = [
            claim for claim in claims
            if claim[0] == guild_id
        ]

        if claims:
            description = ""

            for claim in claims:
                description += (
                    f"• <@{claim[1]}> — **{claim[2]}**\n"
                )
        else:
            description = "No characters have been claimed yet."

        embed = discord.Embed(
            title="🏴‍☠️ Claimed Characters",
            description=description
        )

        await message.edit(embed=embed)

    # ==========================================
    # ADD CHARACTER
    # ==========================================
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
            return

        db.insert(
            "characters",
            "name",
            (text,)
        )

        await ctx.send(f"✅ Added **{text}**")

    # ==========================================
    # SHOW CHARACTERS
    # ==========================================
    @commands.command()
    async def characters(self, ctx):

        characters = db.fetchall("characters")

        if not characters:
            await ctx.send("❌ No characters have been added.")
            return

        message = "🏴‍☠️ **Characters:**\n\n"

        for character in characters:
            message += f"• {character[1]}\n"

        await ctx.send(message)

    # ==========================================
    # CLAIM
    # ==========================================
    @commands.command()
    async def claim(self, ctx, *, text):

        characters = db.fetchall("characters")

        input_name = normalize_name(text)

        # --------------------------------------
        # FIND MATCHES
        # --------------------------------------

        exact_matches = []
        partial_matches = []

        for row in characters:

            character_name = row[1]

            full_name = normalize_name(character_name)

            # Exact full-name match
            if full_name == input_name:
                exact_matches.append(row)
                continue

            # Check individual words
            parts = [
                normalize_name(part)
                for part in character_name.split()
            ]

            # Example:
            # Monkey D. Luffy -> luffy
            # Fake Luffy -> luffy
            if input_name in parts:
                partial_matches.append(row)

        # --------------------------------------
        # EXACT MATCH
        # --------------------------------------

        if exact_matches:

            character = exact_matches[0]

        # --------------------------------------
        # NO EXACT MATCH
        # USE PARTIAL MATCHES
        # --------------------------------------

        elif partial_matches:

            matches = partial_matches

            # More than one character matches
            if len(matches) > 1:

                emojis = [
                    "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣",
                    "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"
                ]

                matches = matches[:10]

                description = ""

                for i, row in enumerate(matches):
                    description += (
                        f"{emojis[i]} **{row[1]}**\n"
                    )

                embed = discord.Embed(
                    title="🏴‍☠️ Which character do you mean?",
                    description=description
                )

                message = await ctx.send(embed=embed)

                for emoji in emojis[:len(matches)]:
                    await message.add_reaction(emoji)

                def check(reaction, user):

                    return (
                        user.id == ctx.author.id
                        and reaction.message.id == message.id
                        and str(reaction.emoji)
                        in emojis[:len(matches)]
                    )

                try:

                    reaction, user = await self.bot.wait_for(
                        "reaction_add",
                        timeout=30,
                        check=check
                    )

                except asyncio.TimeoutError:

                    embed = discord.Embed(
                        title="⏱️ Selection expired",
                        description="You didn't choose a character in time."
                    )

                    await message.edit(embed=embed)
                    return

                selected_index = emojis.index(
                    str(reaction.emoji)
                )

                character = matches[selected_index]

            else:

                character = matches[0]

        # --------------------------------------
        # NO MATCH
        # --------------------------------------

        else:

            await ctx.send(
                f"❌ Character **{text}** not found."
            )

            return

        # --------------------------------------
        # SELECTED CHARACTER
        # --------------------------------------

        character_name = character[1]

        # --------------------------------------
        # CHECK IF USER ALREADY CLAIMED
        # --------------------------------------

        user_exists = db.exists(
            "claims",
            "guild_id = ? AND user_id = ?",
            (ctx.guild.id, ctx.author.id)
        )

        if user_exists:

            await ctx.send(
                "❌ You already claimed a character."
            )

            return

        # --------------------------------------
        # CHECK IF CHARACTER IS CLAIMED
        # --------------------------------------

        claimed = db.exists(
            "claims",
            "guild_id = ? AND character = ?",
            (ctx.guild.id, character_name)
        )

        if claimed:

            await ctx.send(
                "❌ This character is already claimed."
            )

            return

        # --------------------------------------
        # SAVE CLAIM
        # --------------------------------------

        db.insert(
            "claims",
            "guild_id, user_id, character",
            (
                ctx.guild.id,
                ctx.author.id,
                character_name
            )
        )

        # --------------------------------------
        # ROLE
        # --------------------------------------

        role = discord.utils.get(
            ctx.guild.roles,
            name=character_name
        )

        if role is None:

            role = await ctx.guild.create_role(
                name=character_name
            )

        try:

            await ctx.author.add_roles(role)

        except discord.Forbidden:

            print("Cannot give character role.")

        # --------------------------------------
        # NICKNAME
        # --------------------------------------

        try:

            await ctx.author.edit(
                nick=character_name
            )

        except discord.Forbidden:

            print("Cannot change nickname.")

        # --------------------------------------
        # UPDATE PANEL
        # --------------------------------------

        await self.update_panel(
            ctx.guild.id
        )

        # --------------------------------------
        # SUCCESS
        # --------------------------------------

        await ctx.send(
            f"✅ You successfully claimed **{character_name}**!"
        )

    # ==========================================
    # UNCLAIM
    # ==========================================
    @commands.command()
    async def unclaim(self, ctx):

        data = db.fetchone(
            "claims",
            "guild_id = ? AND user_id = ?",
            (ctx.guild.id, ctx.author.id)
        )

        if data is None:

            await ctx.send(
                "❌ You don't have a claimed character."
            )

            return

        character_name = data[2]

        # --------------------------------------
        # DELETE CLAIM
        # --------------------------------------

        db.delete(
            "claims",
            "guild_id = ? AND user_id = ?",
            (ctx.guild.id, ctx.author.id)
        )

        # --------------------------------------
        # REMOVE ROLE
        # --------------------------------------

        role = discord.utils.get(
            ctx.guild.roles,
            name=character_name
        )

        if role:

            try:
                await ctx.author.remove_roles(role)
            except discord.Forbidden:
                print("Cannot remove character role.")

        # --------------------------------------
        # RESET NICKNAME
        # --------------------------------------

        try:

            await ctx.author.edit(nick=None)

        except discord.Forbidden:

            print("Cannot reset nickname.")

        # --------------------------------------
        # UPDATE PANEL
        # --------------------------------------

        await self.update_panel(
            ctx.guild.id
        )

        # --------------------------------------
        # SUCCESS MESSAGE
        # --------------------------------------

        await ctx.send(
            f"✅ You successfully unclaimed **{character_name}**!"
        )

    # ==========================================
    # CLAIM PANEL
    # ==========================================
    @commands.command()
    async def claimpanel(self, ctx):

        # --------------------------------------
        # CHECK EXISTING PANEL
        # --------------------------------------

        data = db.fetchone(
            "claim_panel",
            "guild_id = ?",
            (ctx.guild.id,)
        )

        # --------------------------------------
        # EXISTING PANEL
        # --------------------------------------

        if data:

            channel = self.bot.get_channel(data[1])

            if channel:

                try:

                    message = await channel.fetch_message(
                        data[2]
                    )

                    await self.update_panel(
                        ctx.guild.id
                    )

                    await ctx.send(
                        "✅ Claim panel updated."
                    )

                    return

                except discord.NotFound:

                    pass

        # --------------------------------------
        # CREATE NEW PANEL
        # --------------------------------------

        claims = db.fetchall("claims")

        claims = [
            claim for claim in claims
            if claim[0] == ctx.guild.id
        ]

        if claims:

            description = ""

            for claim in claims:

                description += (
                    f"• <@{claim[1]}> — **{claim[2]}**\n"
                )

        else:

            description = (
                "No characters have been claimed yet."
            )

        embed = discord.Embed(
            title="🏴‍☠️ Claimed Characters",
            description=description
        )

        message = await ctx.send(
            embed=embed
        )

        # --------------------------------------
        # SAVE PANEL
        # --------------------------------------

        db.delete(
            "claim_panel",
            "guild_id = ?",
            (ctx.guild.id,)
        )

        db.insert(
            "claim_panel",
            "guild_id, channel_id, message_id",
            (
                ctx.guild.id,
                ctx.channel.id,
                message.id
            )
        )

        await ctx.send(
            "✅ Claim panel created!"
        )


# ==========================================
# SETUP
# ==========================================
async def setup(bot):

    await bot.add_cog(
        Claim(bot)
        )
