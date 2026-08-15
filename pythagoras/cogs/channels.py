import discord
from discord.ext import commands

from utils.command import command


# =========================================
# CATEGORY FINDER
# =========================================

def find_category(guild, text):

    text = text.strip()

    # Try ID
    if text.isdigit():

        category = guild.get_channel(
            int(text)
        )

        if isinstance(
            category,
            discord.CategoryChannel
        ):
            return category

    # Try exact name
    category = discord.utils.find(
        lambda c: (
            isinstance(
                c,
                discord.CategoryChannel
            )
            and c.name.lower() == text.lower()
        ),
        guild.categories
    )

    if category:
        return category

    # Try underscore version
    category = discord.utils.find(
        lambda c: (
            isinstance(
                c,
                discord.CategoryChannel
            )
            and c.name.lower() == text.replace(
                "_",
                " "
            ).lower()
        ),
        guild.categories
    )

    return category


# =========================================
# CHANNEL FINDER
# =========================================

def find_channel(guild, text):

    text = text.strip()

    # Try ID
    if text.isdigit():

        channel = guild.get_channel(
            int(text)
        )

        if channel:
            return channel

    # Remove #
    if text.startswith("#"):
        text = text[1:]

    # Try exact name
    channel = discord.utils.find(
        lambda c: (
            isinstance(
                c,
                (
                    discord.TextChannel,
                    discord.VoiceChannel,
                    discord.ForumChannel,
                    discord.StageChannel
                )
            )
            and c.name.lower() == text.lower()
        ),
        guild.channels
    )

    if channel:
        return channel

    # Try underscore version
    channel = discord.utils.find(
        lambda c: (
            isinstance(
                c,
                (
                    discord.TextChannel,
                    discord.VoiceChannel,
                    discord.ForumChannel,
                    discord.StageChannel
                )
            )
            and c.name.lower() == text.replace(
                "_",
                " "
            ).lower()
        ),
        guild.channels
    )

    return channel


# =========================================
# CHANNELS COG
# =========================================

class Channels(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =========================================
    # ADD / MOVE CHANNEL
    # =========================================

    @command(
        "🔵 Channels",
        "Create a channel or move an existing channel into a category"
    )
    @commands.has_guild_permissions(
        manage_channels=True
    )
    async def addchannel(
        self,
        ctx,
        *,
        arguments: str
    ):

        arguments = arguments.strip()

        if not arguments:
            await ctx.send(
                "❌ Usage: `Pythagoras addchannel <category> <channel>`"
            )
            return

        # -------------------------------------
        # FIND CATEGORY
        # -------------------------------------
        #
        # Try every possible split until a
        # real category is found.
        #
        # Example:
        #
        # GENERAL CHANNELS general
        #
        # Tries:
        #
        # GENERAL
        # GENERAL CHANNELS
        #
        # Finds GENERAL CHANNELS.
        # -------------------------------------

        parts = arguments.split()

        category = None
        category_end = 0

        for i in range(1, len(parts) + 1):

            possible_category = " ".join(
                parts[:i]
            )

            found = find_category(
                ctx.guild,
                possible_category
            )

            if found:

                category = found
                category_end = i

                break

        if not category:

            await ctx.send(
                "❌ I couldn't find that category."
            )

            return

        # -------------------------------------
        # GET CHANNEL NAME
        # -------------------------------------

        channel_name = " ".join(
            parts[category_end:]
        ).strip()

        if not channel_name:

            await ctx.send(
                "❌ Please provide a channel name."
            )

            return

        # Remove quotes
        if (
            len(channel_name) >= 2
            and channel_name.startswith('"')
            and channel_name.endswith('"')
        ):

            channel_name = channel_name[1:-1]

        elif (
            len(channel_name) >= 2
            and channel_name.startswith("'")
            and channel_name.endswith("'")
        ):

            channel_name = channel_name[1:-1]

        # -------------------------------------
        # FIND EXISTING CHANNEL
        # -------------------------------------

        channel = find_channel(
            ctx.guild,
            channel_name
        )

        # -------------------------------------
        # EXISTING CHANNEL
        # -------------------------------------

        if channel:

            # Already there
            if channel.category_id == category.id:

                await ctx.send(
                    f"ℹ️ {channel.mention} is already "
                    f"inside **{category.name}**."
                )

                return

            old_category = channel.category

            await channel.edit(
                category=category,
                reason=f"Moved by {ctx.author}"
            )

            if old_category:

                await ctx.send(
                    f"📁 Moved {channel.mention} "
                    f"from **{old_category.name}** "
                    f"to **{category.name}**."
                )

            else:

                await ctx.send(
                    f"📁 Moved {channel.mention} "
                    f"into **{category.name}**."
                )

            return

        # -------------------------------------
        # CREATE NEW CHANNEL
        # -------------------------------------

        channel = await ctx.guild.create_text_channel(
            name=channel_name,
            category=category,
            reason=f"Created by {ctx.author}"
        )

        await ctx.send(
            f"✅ Created {channel.mention} "
            f"inside **{category.name}**."
        )

    # =========================================
    # DELETE CHANNEL
    # =========================================

    @command(
        "🔵 Channels",
        "Delete a server channel"
    )
    @commands.has_guild_permissions(
        manage_channels=True
    )
    async def delchannel(
        self,
        ctx,
        *,
        channel_name: str
    ):

        channel = find_channel(
            ctx.guild,
            channel_name
        )

        if not channel:

            await ctx.send(
                "❌ I couldn't find that channel."
            )

            return

        old_name = channel.name

        await channel.delete(
            reason=f"Deleted by {ctx.author}"
        )

        await ctx.send(
            f"🗑️ Deleted **#{old_name}**."
        )

    # =========================================
    # EDIT CHANNEL
    # =========================================

    @command(
        "🔵 Channels",
        "Rename a server channel"
    )
    @commands.has_guild_permissions(
        manage_channels=True
    )
    async def editchannel(
        self,
        ctx,
        *,
        arguments: str
    ):

        parts = arguments.split()

        if len(parts) < 2:

            await ctx.send(
                "❌ Usage: `Pythagoras editchannel <channel> <new name>`"
            )

            return

        # First word = channel
        channel_name = parts[0]

        # Everything else = new name
        new_name = " ".join(parts[1:])

        channel = find_channel(
            ctx.guild,
            channel_name
        )

        if not channel:

            await ctx.send(
                "❌ I couldn't find that channel."
            )

            return

        old_name = channel.name

        await channel.edit(
            name=new_name,
            reason=f"Edited by {ctx.author}"
        )

        await ctx.send(
            f"✏️ Renamed **#{old_name}** "
            f"→ **#{channel.name}**."
        )

    # =========================================
    # CREATE CATEGORY
    # =========================================

    @command(
        "🔵 Channels",
        "Create a new server category"
    )
    @commands.has_guild_permissions(
        manage_channels=True
    )
    async def addcategory(
        self,
        ctx,
        *,
        name: str
    ):

        category = await ctx.guild.create_category(
            name=name,
            reason=f"Created by {ctx.author}"
        )

        await ctx.send(
            f"✅ Created category "
            f"**{category.name}**."
        )

    # =========================================
    # DELETE CATEGORY
    # =========================================

    @command(
        "🔵 Channels",
        "Delete a server category"
    )
    @commands.has_guild_permissions(
        manage_channels=True
    )
    async def delcategory(
        self,
        ctx,
        *,
        name: str
    ):

        category = find_category(
            ctx.guild,
            name
        )

        if not category:

            await ctx.send(
                "❌ I couldn't find that category."
            )

            return

        category_name = category.name

        await category.delete(
            reason=f"Deleted by {ctx.author}"
        )

        await ctx.send(
            f"🗑️ Deleted category "
            f"**{category_name}**."
        )

    # =========================================
    # LIST CATEGORIES
    # =========================================

    @command(
        "🔵 Channels",
        "Show all server categories"
    )
    async def categories(self, ctx):

        categories = ctx.guild.categories

        if not categories:

            await ctx.send(
                "❌ This server has no categories."
            )

            return

        text = "\n".join(
            f"• {category.name}"
            for category in categories
        )

        embed = discord.Embed(
            title="📁 Server Categories",
            description=text,
            color=discord.Color.blue()
        )

        embed.set_footer(
            text=f"{len(categories)} categories"
        )

        await ctx.send(
            embed=embed
        )


# =========================================
# ERROR HANDLING
# =========================================

    @commands.Cog.listener()
    async def on_command_error(
        self,
        ctx,
        error
    ):

        if isinstance(
            error,
            commands.MissingPermissions
        ):

            await ctx.send(
                "❌ You need **Manage Channels** "
                "to use this command."
            )

        elif isinstance(
            error,
            commands.BadArgument
        ):

            await ctx.send(
                "❌ I couldn't find that "
                "category or channel."
            )


# =========================================
# SETUP
# =========================================

async def setup(bot):

    await bot.add_cog(
        Channels(bot)
    )
