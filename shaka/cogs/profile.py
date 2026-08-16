import discord

from datetime import datetime

from discord.ext import commands

from utils.command import command

import mycord


# =========================================
# DATABASE
# =========================================

db = mycord.PunksDB()


# =========================================
# PROFILE TABLE
# =========================================

db.create_table(
    "profiles",
    """
    guild_id INTEGER,
    user_id INTEGER,
    birthday_month INTEGER,
    birthday_day INTEGER,
    birthday_year INTEGER,
    bio TEXT,
    banner TEXT,
    profile_color INTEGER,
    PRIMARY KEY (guild_id, user_id)
    """
)


# =========================================
# PROFILE COG
# =========================================

class Profile(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

    # =====================================
    # PROFILE
    # =====================================

    @command(
        "👤 Profile",
        "View a user's profile",
        usage="[user]"
    )
    async def profile(
        self,
        ctx,
        member: discord.Member = None
    ):

        # ---------------------------------
        # TEST
        # ---------------------------------

        await ctx.send(
            "🔎 Profile command received."
        )

        member = member or ctx.author

        # ---------------------------------
        # CHECK DATABASE
        # ---------------------------------

        profile = db.fetchone(
            "profiles",
            "guild_id = ? AND user_id = ?",
            (
                ctx.guild.id,
                member.id
            )
        )

        # ---------------------------------
        # CREATE PROFILE
        # ---------------------------------

        if not profile:

            db.insert(
                "profiles",
                (
                    "guild_id",
                    "user_id"
                ),
                (
                    ctx.guild.id,
                    member.id
                )
            )

        # ---------------------------------
        # EMBED
        # ---------------------------------

        embed = discord.Embed(
            title=f"{member.display_name}'s Profile",
            description=(
                "This profile is ready to be customized!"
            ),
            color=discord.Color.blue()
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        embed.add_field(
            name="👤 Display Name",
            value=member.display_name,
            inline=True
        )

        embed.add_field(
            name="🆔 User ID",
            value=str(member.id),
            inline=True
        )

        await ctx.send(
            embed=embed
        )

    # =====================================
    # BIO
    # =====================================

    @command(
        "👤 Profile",
        "Set your profile bio",
        usage="<bio>"
    )
    async def setbio(
        self,
        ctx,
        *,
        bio: str = None
    ):

        if not bio:

            await ctx.send(
                "❌ Please provide a bio."
            )

            return

        if len(bio) > 500:

            await ctx.send(
                "❌ Your bio cannot exceed "
                "**500 characters**."
            )

            return

        db.update(
            "profiles",
            {
                "bio": bio
            },
            "guild_id = ? AND user_id = ?",
            (
                ctx.guild.id,
                ctx.author.id
            )
        )

        await ctx.send(
            "✅ Bio updated!"
        )

    # =====================================
    # BIRTHDAY
    # =====================================

    @command(
        "👤 Profile",
        "Set your birthday",
        usage="<DD/MM[/YYYY]>"
    )
    async def birthday(
        self,
        ctx,
        date: str = None
    ):

        if not date:

            await ctx.send(
                "❌ Usage: "
                "`Shaka birthday DD/MM[/YYYY]`"
            )

            return

        parsed = None
        year = None

        # DD/MM
        try:

            parsed = datetime.strptime(
                date,
                "%d/%m"
            )

        except ValueError:

            pass

        # DD/MM/YYYY
        if parsed is None:

            try:

                parsed = datetime.strptime(
                    date,
                    "%d/%m/%Y"
                )

                year = parsed.year

            except ValueError:

                pass

        if parsed is None:

            await ctx.send(
                "❌ Invalid birthday format.\n"
                "Use `DD/MM` or `DD/MM/YYYY`."
            )

            return

        # ---------------------------------
        # MAKE SURE PROFILE EXISTS
        # ---------------------------------

        profile = db.fetchone(
            "profiles",
            "guild_id = ? AND user_id = ?",
            (
                ctx.guild.id,
                ctx.author.id
            )
        )

        if not profile:

            db.insert(
                "profiles",
                (
                    "guild_id",
                    "user_id"
                ),
                (
                    ctx.guild.id,
                    ctx.author.id
                )
            )

        # ---------------------------------
        # SAVE
        # ---------------------------------

        db.update(
            "profiles",
            {
                "birthday_month": parsed.month,
                "birthday_day": parsed.day,
                "birthday_year": year
            },
            "guild_id = ? AND user_id = ?",
            (
                ctx.guild.id,
                ctx.author.id
            )
        )

        await ctx.send(
            f"🎂 Birthday saved as "
            f"**{parsed.strftime('%B %d')}**!"
        )


# =========================================
# SETUP
# =========================================

async def setup(bot):

    await bot.add_cog(
        Profile(bot)
        )
