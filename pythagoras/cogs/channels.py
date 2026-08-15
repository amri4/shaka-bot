import discord
from discord.ext import commands

from utils.command import command


# =========================================
# SUPPORTED CHANNEL TYPES
# =========================================

CHANNEL_TYPES = (
    discord.TextChannel,
    discord.VoiceChannel,
    discord.ForumChannel,
    discord.StageChannel,
)


# =========================================
# FIND CATEGORY
# =========================================

def find_category(guild, text):

    text = text.strip()

    # Remove quotes
    if len(text) >= 2:
        if text[0] == text[-1] and text[0] in ("\"", "'"):
            text = text[1:-1]

    # Category ID
    if text.isdigit():

        category = guild.get_channel(
            int(text)
        )

        if isinstance(
            category,
            discord.CategoryChannel
        ):
            return category

    # Exact category name
    for category in guild.categories:

        if category.name.lower() == text.lower():
            return category

    # Underscore version
    converted = text.replace("_", " ")

    for category in guild.categories:

        if category.name.lower() == converted.lower():
            return category

    return None


# =========================================
# FIND CHANNEL
# =========================================

def find_channel(guild, text):

    text = text.strip()

    # Discord channel mention
    # <#123456789>
    if text.startswith("<#") and text.endswith(">"):

        channel_id = text[2:-1]

        if channel_id.isdigit():

            channel = guild.get_channel(
                int(channel_id)
            )

            if channel:
                return channel

    # #channel
    if text.startswith("#"):
        text = text[1:]

    # Channel ID
    if text.isdigit():

        channel = guild.get_channel(
            int(text)
        )

        if channel:
            return channel

    # Remove quotes
    if len(text) >= 2:

        if (
            text[0] == text[-1]
            and text[0] in ("\"", "'")
        ):
            text = text[1:-1]

    # Exact name
    for channel in guild.channels:

        if not isinstance(
            channel,
            CHANNEL_TYPES
        ):
            continue

        if channel.name.lower() == text.lower():
            return channel

    # Underscore version
    converted = text.replace("_", " ")

    for channel in guild.channels:

        if not isinstance(
            channel,
            CHANNEL_TYPES
        ):
            continue

        if channel.name.lower() == converted.lower():
            return channel

    return None


# =========================================
# FIND CATEGORY USING MULTIPLE WORDS
# =========================================

def find_category_from_parts(guild, parts):

    for i in range(1, len(parts) + 1):

        possible = " ".join(
            parts[:i]
        )

        category = find_category(
            guild,
            possible
        )

        if category:

            return category, i

    return None, None


# =========================================
# FIND CHANNEL USING MULTIPLE WORDS
# =========================================

def find_channel_from_parts(guild, parts):

    for i in range(1, len(parts) + 1):

        possible = " ".join(
            parts[:i]
        )

        channel = find_channel(
            guild,
            possible
        )

        if channel:

            return channel, i

    return None, None


# =========================================
# CHANNELS COG
# =========================================

class Channels(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

    # =====================================
    # ADD / MOVE CHANNEL
    # =====================================

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
                "❌ Usage: "
                "`Pythagoras addchannel <category> <channel>`"
            )

            return

        parts = arguments.split()

        # Find category first
        category, category_end = find_category_from_parts(
            ctx.guild,
            parts
        )

        if not category:

            await ctx.send(
                "❌ I couldn't find that category."
            )

            return

        # Remaining text is channel
        channel_name = " ".join(
            parts[category_end:]
        ).strip()

        if not channel_name:

            await ctx.send(
                "❌ Please provide a channel."
            )

            return

        # Find existing channel
        channel = find_channel(
            ctx.guild,
            channel_name
        )

        # =================================
        # EXISTING CHANNEL
        # =================================

        if channel:

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

        # Explicit channel reference
        explicit_reference = (
            channel_name.startswith("#")
            or (
                channel_name.startswith("<#")
                and channel_name.endswith(">")
            )
            or channel_name.isdigit()
        )

        if explicit_reference:

            await ctx.send(
                "❌ I couldn't find that channel."
            )

            return

        # =================================
        # CREATE CHANNEL
        # =================================

        channel = await ctx.guild.create_text_channel(
            name=channel_name,
            category=category,
            reason=f"Created by {ctx.author}"
        )

        await ctx.send(
            f"✅ Created {channel.mention} "
            f"inside **{category.name}**."
        )

    # =====================================
    # DELETE CHANNEL
    # =====================================

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

    # =====================================
    # EDIT CHANNEL
    # =====================================

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
                "❌ Usage: "
                "`Pythagoras editchannel <channel> <new name>`"
            )

            return

        channel = find_channel(
            ctx.guild,
            parts[0]
        )

        if not channel:

            await ctx.send(
                "❌ I couldn't find that channel."
            )

            return

        new_name = " ".join(
            parts[1:]
        )

        old_name = channel.name

        await channel.edit(
            name=new_name,
            reason=f"Edited by {ctx.author}"
        )

        await ctx.send(
            f"✏️ Renamed **#{old_name}** "
            f"→ **#{channel.name}**."
        )

    # =====================================
    # CREATE CATEGORY
    # =====================================

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

    # =====================================
    # DELETE CATEGORY
    # =====================================

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

    # =====================================
    # LIST CATEGORIES
    # =====================================

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

        lines = []

        for category in categories:

            channel_count = len(
                category.channels
            )

            lines.append(
                f"📁 **{category.name}** "
                f"— {channel_count} channels"
            )

        embed = discord.Embed(
            title="📁 Server Categories",
            description="\n".join(lines),
            color=discord.Color.blue()
        )

        embed.set_footer(
            text=f"{len(categories)} categories"
        )

        await ctx.send(
            embed=embed
        )

    # =====================================
    # MOVE CHANNEL
    # =====================================

    @command(
        "🔵 Channels",
        "Move a channel above or below another channel"
    )
    @commands.has_guild_permissions(
        manage_channels=True
    )
    async def movechannel(
        self,
        ctx,
        *,
        arguments: str
    ):

        parts = arguments.split()

        if len(parts) < 3:

            await ctx.send(
                "❌ Usage: "
                "`Pythagoras movechannel <channel> "
                "<above/below> <target>`"
            )

            return

        # ---------------------------------
        # FIND SOURCE CHANNEL
        # ---------------------------------

        source = None
        source_end = None

        # Try each possible amount of words
        # until we find a channel.
        for i in range(1, len(parts)):

            possible = " ".join(
                parts[:i]
            )

            found = find_channel(
                ctx.guild,
                possible
            )

            if found:

                source = found
                source_end = i
                break

        if not source:

            await ctx.send(
                "❌ I couldn't find the channel "
                "you want to move."
            )

            return

        # ---------------------------------
        # DIRECTION
        # ---------------------------------

        if source_end >= len(parts):

            await ctx.send(
                "❌ Please specify `above` or `below`."
            )

            return

        direction = parts[source_end].lower()

        if direction not in (
            "above",
            "below"
        ):

            await ctx.send(
                "❌ Direction must be "
                "`above` or `below`."
            )

            return

        # ---------------------------------
        # FIND TARGET
        # ---------------------------------

        target_text = " ".join(
            parts[source_end + 1:]
        )

        target = find_channel(
            ctx.guild,
            target_text
        )

        if not target:

            await ctx.send(
                "❌ I couldn't find the target channel."
            )

            return

        if source.id == target.id:

            await ctx.send(
                "❌ You can't move a channel "
                "relative to itself."
            )

            return

        # ---------------------------------
        # SAME CATEGORY
        # ---------------------------------

        if source.category_id != target.category_id:

            await ctx.send(
                "❌ Both channels must be "
                "in the same category."
            )

            return

        # ---------------------------------
        # MOVE
        # ---------------------------------

        target_position = target.position

        if direction == "above":

            new_position = target_position

        else:

            new_position = target_position + 1

        await source.edit(
            position=new_position,
            reason=f"Moved by {ctx.author}"
        )

        await ctx.send(
            f"📁 Moved {source.mention} "
            f"**{direction}** {target.mention}."
        )

    # =====================================
    # MOVE CATEGORY
    # =====================================

    @command(
        "🔵 Channels",
        "Move a category above or below another category"
    )
    @commands.has_guild_permissions(
        manage_channels=True
    )
    async def movecategory(
        self,
        ctx,
        *,
        arguments: str
    ):

        parts = arguments.split()

        if len(parts) < 3:

            await ctx.send(
                "❌ Usage: "
                "`Pythagoras movecategory <category> "
                "<above/below> <target>`"
            )

            return

        # ---------------------------------
        # FIND SOURCE CATEGORY
        # ---------------------------------

        source = None
        source_end = None

        for i in range(1, len(parts)):

            possible = " ".join(
                parts[:i]
            )

            found = find_category(
                ctx.guild,
                possible
            )

            if found:

                source = found
                source_end = i
                break

        if not source:

            await ctx.send(
                "❌ I couldn't find the category "
                "you want to move."
            )

            return

        # ---------------------------------
        # DIRECTION
        # ---------------------------------

        if source_end >= len(parts):

            await ctx.send(
                "❌ Please specify `above` or `below`."
            )

            return

        direction = parts[source_end].lower()

        if direction not in (
            "above",
            "below"
        ):

            await ctx.send(
                "❌ Direction must be "
                "`above` or `below`."
            )

            return

        # ---------------------------------
        # TARGET CATEGORY
        # ---------------------------------

        target_text = " ".join(
            parts[source_end + 1:]
        )

        target = find_category(
            ctx.guild,
            target_text
        )

        if not target:

            await ctx.send(
                "❌ I couldn't find the "
                "target category."
            )

            return

        if source.id == target.id:

            await ctx.send(
                "❌ You can't move a category "
                "relative to itself."
            )

            return

        # ---------------------------------
        # MOVE
        # ---------------------------------

        target_position = target.position

        if direction == "above":

            new_position = target_position

        else:

            new_position = target_position + 1

        await source.edit(
            position=new_position,
            reason=f"Moved by {ctx.author}"
        )

        await ctx.send(
            f"📁 Moved category "
            f"**{source.name}** "
            f"**{direction}** "
            f"**{target.name}**."
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


# =========================================
# SETUP
# =========================================

async def setup(bot):

    await bot.add_cog(
        Channels(bot)
        )
