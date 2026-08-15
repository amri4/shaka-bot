import discord
from discord.ext import commands

from utils.command import command


# =========================================
# CATEGORY CONVERTER
# =========================================

class CategoryConverter(commands.Converter):

    async def convert(self, ctx, argument):

        # Try category ID
        if argument.isdigit():

            category = ctx.guild.get_channel(
                int(argument)
            )

            if isinstance(
                category,
                discord.CategoryChannel
            ):
                return category

        # Try category name
        category = discord.utils.find(
            lambda c: (
                isinstance(
                    c,
                    discord.CategoryChannel
                )
                and c.name.lower() == argument.lower()
            ),
            ctx.guild.categories
        )

        if category:
            return category

        raise commands.BadArgument(
            "Category not found."
        )


# =========================================
# CHANNEL CONVERTER
# =========================================

class ChannelConverter(commands.Converter):

    async def convert(self, ctx, argument):

        # Try channel ID
        if argument.isdigit():

            channel = ctx.guild.get_channel(
                int(argument)
            )

            if channel:
                return channel

        # Try channel name
        channel = discord.utils.find(
            lambda c: (
                c.name.lower() == argument.lower()
                and isinstance(
                    c,
                    (
                        discord.TextChannel,
                        discord.VoiceChannel,
                        discord.ForumChannel,
                        discord.StageChannel
                    )
                )
            ),
            ctx.guild.channels
        )

        if channel:
            return channel

        raise commands.BadArgument(
            "Channel not found."
        )


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
        category: CategoryConverter,
        *,
        name: str
    ):

        # -------------------------------------
        # CHECK IF CHANNEL ALREADY EXISTS
        # -------------------------------------

        channel = discord.utils.find(
            lambda c: (
                c.name.lower() == name.lower()
                and isinstance(
                    c,
                    (
                        discord.TextChannel,
                        discord.VoiceChannel,
                        discord.ForumChannel,
                        discord.StageChannel
                    )
                )
            ),
            ctx.guild.channels
        )

        # -------------------------------------
        # EXISTING CHANNEL
        # -------------------------------------

        if channel:

            # Already in this category
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
            name=name,
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
        channel: ChannelConverter
    ):

        channel_name = channel.name

        await channel.delete(
            reason=f"Deleted by {ctx.author}"
        )

        await ctx.send(
            f"🗑️ Deleted **#{channel_name}**."
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
        channel: ChannelConverter,
        *,
        name: str
    ):

        old_name = channel.name

        await channel.edit(
            name=name,
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
        category: CategoryConverter
    ):

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
