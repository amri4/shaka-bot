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

        # ==========================================
        # CLAIMS TABLE
        # ==========================================
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

        # ==========================================
        # CHARACTERS TABLE
        # ==========================================
        db.create_table(
            "characters",
            """
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE
            """
        )

        print("Characters table ready!")

        # ==========================================
        # CLAIM PANEL TABLE
        # ==========================================
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
    # UPDATE CURRENT CLAIM PANEL
    # ==========================================
    async def update_panel(self, guild_id):

        data = db.fetchone(
            "claim_panel",
            "guild_id = ?",
            (guild_id,)
        )

        # No panel has been created yet
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
            claim
            for claim in claims
            if claim[0] == guild_id
        ]

        # ==========================================
        # BUILD DESCRIPTION
        # ==========================================

        if claims:

            description = ""

            for claim in claims:
                description += (
                    f"• <@{claim[1]}> — **{claim[2]}**\n"
                )

        else:

            description = "No characters have been claimed yet."

        # ==========================================
        # CREATE EMBED
        # ==========================================

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
            await ctx.send(
                "🚫 Character already exists."
            )
            return

        db.insert(
            "characters",
            "name",
            (text,)
        )

        await ctx.send(
            f"✅ Added **{text}**"
        )

    # ==========================================
    # SHOW CHARACTERS
    # ==========================================
    @commands.command()
    async def characters(self, ctx):

        characters = db.fetchall("characters")

        if not characters:
            await ctx.send(
                "❌ No characters have been added."
            )
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

        matches = []

        # ==========================================
        # FIND ALL MATCHES
        # ==========================================

        for row in characters:

            character_name = row[1]

            full_name = normalize_name(character_name)

            parts = [
                normalize_name(part)
                for part in character_name.split()
            ]

            # --------------------------------------
            # FULL NAME
            # --------------------------------------

            if input_name == full_name:
                matches.append(row)
                continue

            # --------------------------------------
            # ANY WORD / LAST NAME
            # --------------------------------------

            if input_name in parts:
                matches.append(row)

        # ==========================================
        # NO MATCH
        # ==========================================

        if not matches:

            await ctx.send(
                f"❌ Character **{text}** not found."
            )

            return

        # ==========================================
        # REMOVE DUPLICATES
        # ==========================================

        unique_matches = []

        for row in matches:

            if row[0] not in [
                existing[0]
                for existing in unique_matches
            ]:
                unique_matches.append(row)

        matches = unique_matches

        # ==========================================
        # MULTIPLE MATCHES
        # ==========================================

        if len(matches) > 1:

            emojis = [
                "1️⃣",
                "2️⃣",
                "3️⃣",
                "4️⃣",
                "5️⃣",
                "6️⃣",
                "7️⃣",
                "8️⃣",
                "9️⃣",
                "🔟"
            ]

            # Maximum 10 options
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

            embed.set_footer(
                text="React with the number of the character you want."
            )

            message = await ctx.send(
                embed=embed
            )

            # ==========================================
            # ADD REACTIONS
            # ==========================================

            for emoji in emojis[:len(matches)]:

                try:
                    await message.add_reaction(emoji)

                except discord.Forbidden:
                    await ctx.send(
                        "❌ I don't have permission to add reactions."
                    )
                    return

            # ==========================================
            # REACTION CHECK
            # ==========================================

            def check(reaction, user):

                return (
                    user.id == ctx.author.id
                    and reaction.message.id == message.id
                    and str(reaction.emoji)
                    in emojis[:len(matches)]
                )

            # ==========================================
            # WAIT FOR SELECTION
            # ==========================================

            try:

                reaction, user = await self.bot.wait_for(
                    "reaction_add",
                    timeout=30,
                    check=check
                )

            except asyncio.TimeoutError:

                embed = discord.Embed(
                    title="⏱️ Selection expired",
                    description=(
                        "You didn't choose a character "
                        "within 30 seconds."
                    )
                )

                await message.edit(
                    embed=embed
                )

                return

            # ==========================================
            # GET SELECTED CHARACTER
            # ==========================================

            selected_index = emojis.index(
                str(reaction.emoji)
            )

            character = matches[selected_index]

        # ==========================================
        # ONLY ONE MATCH
        # ==========================================

        else:

            character = matches[0]

        # ==========================================
        # GET CHARACTER NAME
        # ==========================================

        character_name = character[1]

        # ==========================================
        # CHECK USER CLAIM
        # ==========================================

        user_exists = db.exists(
            "claims",
            "guild_id = ? AND user_id = ?",
            (
                ctx.guild.id,
                ctx.author.id
            )
        )

        if user_exists:

            await ctx.send(
                "❌ You already claimed a character."
            )

            return

        # ==========================================
        # CHECK CHARACTER CLAIM
        # ==========================================

        claimed = db.exists(
            "claims",
            "guild_id = ? AND character = ?",
            (
                ctx.guild.id,
                character_name
            )
        )

        if claimed:

            await ctx.send(
                f"❌ **{character_name}** is already claimed."
            )

            return

        # ==========================================
        # SAVE CLAIM
        # ==========================================

        db.insert(
            "claims",
            "guild_id, user_id, character",
            (
                ctx.guild.id,
                ctx.author.id,
                character_name
            )
        )

        # ==========================================
        # GET / CREATE ROLE
        # ==========================================

        role = discord.utils.get(
            ctx.guild.roles,
            name=character_name
        )

        if role is None:

            try:

                role = await ctx.guild.create_role(
                    name=character_name
                )

            except discord.Forbidden:

                print(
                    "Cannot create character role."
                )

                role = None

        # ==========================================
        # GIVE ROLE
        # ==========================================

        if role is not None:

            try:

                await ctx.author.add_roles(role)

            except discord.Forbidden:

                print(
                    "Cannot give character role."
                )

        # ==========================================
        # CHANGE NICKNAME
        # ==========================================

        try:

            await ctx.author.edit(
                nick=character_name
            )

        except discord.Forbidden:

            print(
                "Cannot change nickname."
            )

        # ==========================================
        # AUTOMATICALLY UPDATE PANEL
        # ==========================================

        await self.update_panel(
            ctx.guild.id
        )

        # ==========================================
        # SUCCESS
        # ==========================================

        await ctx.send(
            f"✅ You successfully claimed "
            f"**{character_name}**!"
        )

    # ==========================================
    # UNCLAIM
    # ==========================================
    @commands.command()
    async def unclaim(self, ctx):

        data = db.fetchone(
            "claims",
            "guild_id = ? AND user_id = ?",
            (
                ctx.guild.id,
                ctx.author.id
            )
        )

        # ==========================================
        # NO CLAIM
        # ==========================================

        if data is None:

            await ctx.send(
                "❌ You don't have a claimed character."
            )

            return

        character_name = data[2]

        # ==========================================
        # DELETE CLAIM
        # ==========================================

        db.delete(
            "claims",
            "guild_id = ? AND user_id = ?",
            (
                ctx.guild.id,
                ctx.author.id
            )
        )

        # ==========================================
        # REMOVE ROLE
        # ==========================================

        role = discord.utils.get(
            ctx.guild.roles,
            name=character_name
        )

        if role is not None:

            try:

                await ctx.author.remove_roles(
                    role
                )

            except discord.Forbidden:

                print(
                    "Cannot remove character role."
                )

        # ==========================================
        # RESET NICKNAME
        # ==========================================

        try:

            await ctx.author.edit(
                nick=None
            )

        except discord.Forbidden:

            print(
                "Cannot reset nickname."
            )

        # ==========================================
        # AUTOMATICALLY UPDATE PANEL
        # ==========================================

        await self.update_panel(
            ctx.guild.id
        )

        # ==========================================
        # SUCCESS MESSAGE
        # ==========================================

        await ctx.send(
            f"✅ You successfully unclaimed "
            f"**{character_name}**!"
        )

    # ==========================================
    # CLAIM PANEL
    # ==========================================
    @commands.command()
    async def claimpanel(self, ctx):

        # ==========================================
        # GET CURRENT CLAIMS
        # ==========================================

        claims = db.fetchall("claims")

        claims = [
            claim
            for claim in claims
            if claim[0] == ctx.guild.id
        ]

        # ==========================================
        # BUILD DESCRIPTION
        # ==========================================

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

        # ==========================================
        # CREATE NEW PANEL
        # ==========================================

        embed = discord.Embed(
            title="🏴‍☠️ Claimed Characters",
            description=description
        )

        message = await ctx.send(
            embed=embed
        )

        # ==========================================
        # SAVE THIS AS THE CURRENT PANEL
        # ==========================================

        old_panel = db.fetchone(
            "claim_panel",
            "guild_id = ?",
            (ctx.guild.id,)
        )

        if old_panel:

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


# ==========================================
# SETUP
# ==========================================
async def setup(bot):

    await bot.add_cog(
        Claim(bot)
        )
