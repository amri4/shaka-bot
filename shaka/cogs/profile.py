import discord

from datetime import datetime

from discord.ext import commands

from utils.command import command
from utils.role_colors import parse_role_color

import mycord


# =========================================
# DATABASE
# =========================================

db = mycord.PunksDB()


# =========================================
# PROFILES
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
# CUSTOM PROFILE FIELDS
# =========================================

db.create_table(
    "profile_fields",
    """
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER,
    user_id INTEGER,
    name TEXT,
    value TEXT,
    UNIQUE(guild_id, user_id, name)
    """
)


# =========================================
# GET / CREATE PROFILE
# =========================================

def get_profile(
    guild_id,
    user_id
):

    profile = db.fetchone(
        "profiles",
        "guild_id = ? AND user_id = ?",
        (
            guild_id,
            user_id
        )
    )

    if profile:
        return profile

    db.insert(
        "profiles",
        (
            "guild_id",
            "user_id"
        ),
        (
            guild_id,
            user_id
        )
    )

    return db.fetchone(
        "profiles",
        "guild_id = ? AND user_id = ?",
        (
            guild_id,
            user_id
        )
    )


# =========================================
# PROFILE VALUE
# =========================================

def profile_value(
    profile,
    key,
    default=None
):

    if not profile:
        return default

    if isinstance(profile, dict):

        return profile.get(
            key,
            default
        )

    return default


# =========================================
# PROFILE COLOR
# =========================================

def get_profile_color(
    profile,
    member
):

    color = profile_value(
        profile,
        "profile_color"
    )

    if color is not None:

        try:

            return discord.Color(
                int(color)
            )

        except (
            TypeError,
            ValueError
        ):

            pass

    # Use Discord role color if available
    if member.color != discord.Color.default():

        return member.color

    return discord.Color.blue()


# =========================================
# FORMAT BIRTHDAY
# =========================================

def get_birthday(
    profile
):

    month = profile_value(
        profile,
        "birthday_month"
    )

    day = profile_value(
        profile,
        "birthday_day"
    )

    if not month or not day:
        return None

    try:

        date = datetime(
            2000,
            int(month),
            int(day)
        )

        return date.strftime(
            "%B %d"
        )

    except (
        ValueError,
        TypeError
    ):

        return None


# =========================================
# GET CUSTOM FIELDS
# =========================================

def get_fields(
    guild_id,
    user_id
):

    rows = db.fetchall(
        "profile_fields"
    )

    fields = []

    for row in rows:

        if not isinstance(
            row,
            dict
        ):
            continue

        if row.get(
            "guild_id"
        ) != guild_id:

            continue

        if row.get(
            "user_id"
        ) != user_id:

            continue

        fields.append(row)

    return fields


# =========================================
# PROFILE COG
# =========================================

class Profile(commands.Cog):

    def __init__(
        self,
        bot
    ):

        self.bot = bot

    # =====================================
    # PROFILE
    # =====================================

    @command(
        "👤 Profile",
        "View your profile or another user's profile",
        usage="[user]"
    )
    @commands.guild_only()
    async def profile(
        self,
        ctx,
        member: discord.Member = None
    ):

        member = member or ctx.author

        profile = get_profile(
            ctx.guild.id,
            member.id
        )

        embed = discord.Embed(
            title=(
                f"{member.display_name}'s Profile"
            ),
            color=get_profile_color(
                profile,
                member
            )
        )

        # ---------------------------------
        # AVATAR
        # ---------------------------------

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        # ---------------------------------
        # BANNER
        # ---------------------------------

        banner = profile_value(
            profile,
            "banner"
        )

        if banner:

            embed.set_image(
                url=banner
            )

        # ---------------------------------
        # DISPLAY NAME
        # ---------------------------------

        embed.add_field(
            name="👤 Display Name",
            value=member.display_name,
            inline=True
        )

        # ---------------------------------
        # JOINED SERVER
        # ---------------------------------

        if member.joined_at:

            joined = discord.utils.format_dt(
                member.joined_at,
                "D"
            )

        else:

            joined = "Unknown"

        embed.add_field(
            name="📅 Joined Server",
            value=joined,
            inline=True
        )

        # ---------------------------------
        # ACCOUNT CREATED
        # ---------------------------------

        embed.add_field(
            name="🗓️ Account Created",
            value=discord.utils.format_dt(
                member.created_at,
                "D"
            ),
            inline=True
        )

        # ---------------------------------
        # BIRTHDAY
        # ---------------------------------

        birthday = get_birthday(
            profile
        )

        if birthday:

            embed.add_field(
                name="🎂 Birthday",
                value=birthday,
                inline=True
            )

        # ---------------------------------
        # BIO
        # ---------------------------------

        bio = profile_value(
            profile,
            "bio"
        )

        if bio:

            embed.add_field(
                name="📝 About",
                value=bio,
                inline=False
            )

        # ---------------------------------
        # CUSTOM FIELDS
        # ---------------------------------

        fields = get_fields(
            ctx.guild.id,
            member.id
        )

        for field in fields:

            name = field.get(
                "name"
            )

            value = field.get(
                "value"
            )

            if not name or not value:
                continue

            embed.add_field(
                name=name,
                value=value,
                inline=True
            )

        # ---------------------------------
        # FOOTER
        # ---------------------------------

        embed.set_footer(
            text=f"User ID: {member.id}"
        )

        await ctx.send(
            embed=embed
        )

    # =====================================
    # SET BIO
    # =====================================

    @command(
        "👤 Profile",
        "Set your profile bio",
        usage="<bio>"
    )
    @commands.guild_only()
    async def setbio(
        self,
        ctx,
        *,
        bio: str = None
    ):

        get_profile(
            ctx.guild.id,
            ctx.author.id
        )

        if not bio:

            db.update(
                "profiles",
                {
                    "bio": None
                },
                "guild_id = ? AND user_id = ?",
                (
                    ctx.guild.id,
                    ctx.author.id
                )
            )

            await ctx.send(
                "📝 Your profile bio has been removed."
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
            "✅ Your profile bio has been updated."
        )

    # =====================================
    # BIRTHDAY
    # =====================================

    @command(
        "👤 Profile",
        "Save your birthday for your profile and future Edison celebrations",
        usage="<DD/MM[/YYYY]>"
    )
    @commands.guild_only()
    async def birthday(
        self,
        ctx,
        date: str = None
    ):

        get_profile(
            ctx.guild.id,
            ctx.author.id
        )

        if not date:

            await ctx.send(
                "❌ Please provide your birthday.\n\n"
                "Examples:\n"
                "`Shaka birthday 12/08`\n"
                "`Shaka birthday 12/08/2008`"
            )

            return

        parsed = None
        year = None

        # ---------------------------------
        # DD/MM
        # ---------------------------------

        try:

            parsed = datetime.strptime(
                date,
                "%d/%m"
            )

        except ValueError:
            pass

        # ---------------------------------
        # DD/MM/YYYY
        # ---------------------------------

        if parsed is None:

            try:

                parsed = datetime.strptime(
                    date,
                    "%d/%m/%Y"
                )

                year = parsed.year

            except ValueError:
                pass

        # ---------------------------------
        # INVALID
        # ---------------------------------

        if parsed is None:

            await ctx.send(
                "❌ Invalid birthday.\n\n"
                "Use `DD/MM` or `DD/MM/YYYY`."
            )

            return

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

    # =====================================
    # REMOVE BIRTHDAY
    # =====================================

    @command(
        "👤 Profile",
        "Remove your saved birthday"
    )
    @commands.guild_only()
    async def removebirthday(
        self,
        ctx
    ):

        get_profile(
            ctx.guild.id,
            ctx.author.id
        )

        db.update(
            "profiles",
            {
                "birthday_month": None,
                "birthday_day": None,
                "birthday_year": None
            },
            "guild_id = ? AND user_id = ?",
            (
                ctx.guild.id,
                ctx.author.id
            )
        )

        await ctx.send(
            "🎂 Your birthday has been removed."
        )

    # =====================================
    # BANNER
    # =====================================

    @command(
        "👤 Profile",
        "Set your profile banner",
        usage="<image URL>"
    )
    @commands.guild_only()
    async def banner(
        self,
        ctx,
        url: str = None
    ):

        get_profile(
            ctx.guild.id,
            ctx.author.id
        )

        if not url:

            db.update(
                "profiles",
                {
                    "banner": None
                },
                "guild_id = ? AND user_id = ?",
                (
                    ctx.guild.id,
                    ctx.author.id
                )
            )

            await ctx.send(
                "🖼️ Your profile banner has been removed."
            )

            return

        if not url.startswith(
            (
                "http://",
                "https://"
            )
        ):

            await ctx.send(
                "❌ Please provide a valid image URL."
            )

            return

        if len(url) > 1000:

            await ctx.send(
                "❌ That URL is too long."
            )

            return

        db.update(
            "profiles",
            {
                "banner": url
            },
            "guild_id = ? AND user_id = ?",
            (
                ctx.guild.id,
                ctx.author.id
            )
        )

        await ctx.send(
            "✅ Your profile banner has been updated."
        )

    # =====================================
    # PROFILE COLOR
    # =====================================

    @command(
        "👤 Profile",
        "Set your profile embed color",
        usage="<color>"
    )
    @commands.guild_only()
    async def profilecolor(
        self,
        ctx,
        color: str = None
    ):

        get_profile(
            ctx.guild.id,
            ctx.author.id
        )

        if not color:

            db.update(
                "profiles",
                {
                    "profile_color": None
                },
                "guild_id = ? AND user_id = ?",
                (
                    ctx.guild.id,
                    ctx.author.id
                )
            )

            await ctx.send(
                "🎨 Your custom profile color "
                "has been removed."
            )

            return

        color_value = parse_role_color(
            color
        )

        if color_value is None:

            await ctx.send(
                "❌ I don't recognize that color.\n"
                "Use `Shaka colors` to see the "
                "available colors."
            )

            return

        db.update(
            "profiles",
            {
                "profile_color": color_value
            },
            "guild_id = ? AND user_id = ?",
            (
                ctx.guild.id,
                ctx.author.id
            )
        )

        await ctx.send(
            f"🎨 Your profile color is now "
            f"**{color.lower()}**."
        )

    # =====================================
    # ADD / EDIT FIELD
    # =====================================

    @command(
        "👤 Profile",
        "Add custom information to your profile",
        usage="<name> | <value>"
    )
    @commands.guild_only()
    async def fieldadd(
        self,
        ctx,
        *,
        arguments: str = None
    ):

        if not arguments:

            await ctx.send(
                "❌ Usage: "
                "`Shaka fieldadd <name> | <value>`"
            )

            return

        if "|" not in arguments:

            await ctx.send(
                "❌ Separate the name and value "
                "with `|`.\n\n"
                "Example:\n"
                "`Shaka fieldadd Favorite Game | "
                "Rocket League`"
            )

            return

        name, value = arguments.split(
            "|",
            1
        )

        name = name.strip()
        value = value.strip()

        if not name or not value:

            await ctx.send(
                "❌ Both the field name and "
                "value are required."
            )

            return

        if len(name) > 50:

            await ctx.send(
                "❌ Field names cannot exceed "
                "**50 characters**."
            )

            return

        if len(value) > 200:

            await ctx.send(
                "❌ Field values cannot exceed "
                "**200 characters**."
            )

            return

        fields = get_fields(
            ctx.guild.id,
            ctx.author.id
        )

        # ---------------------------------
        # CHECK EXISTING FIELD
        # ---------------------------------

        existing = None

        for field in fields:

            if field.get(
                "name",
                ""
            ).lower() == name.lower():

                existing = field

                break

        # ---------------------------------
        # UPDATE
        # ---------------------------------

        if existing:

            db.update(
                "profile_fields",
                {
                    "name": name,
                    "value": value
                },
                "id = ?",
                (
                    existing["id"],
                )
            )

            await ctx.send(
                f"✅ Updated profile field "
                f"**{name}**."
            )

            return

        # ---------------------------------
        # LIMIT
        # ---------------------------------

        if len(fields) >= 10:

            await ctx.send(
                "❌ You can have up to "
                "**10 custom fields**."
            )

            return

        # ---------------------------------
        # INSERT
        # ---------------------------------

        db.insert(
            "profile_fields",
            (
                "guild_id",
                "user_id",
                "name",
                "value"
            ),
            (
                ctx.guild.id,
                ctx.author.id,
                name,
                value
            )
        )

        await ctx.send(
            f"✅ Added **{name}** to your profile."
        )

    # =====================================
    # REMOVE FIELD
    # =====================================

    @command(
        "👤 Profile",
        "Remove a custom profile field",
        usage="<name>"
    )
    @commands.guild_only()
    async def fieldremove(
        self,
        ctx,
        *,
        name: str
    ):

        fields = get_fields(
            ctx.guild.id,
            ctx.author.id
        )

        target = None

        for field in fields:

            if field.get(
                "name",
                ""
            ).lower() == name.lower():

                target = field

                break

        if not target:

            await ctx.send(
                "❌ I couldn't find that profile field."
            )

            return

        db.delete(
            "profile_fields",
            "id = ?",
            (
                target["id"],
            )
        )

        await ctx.send(
            f"🗑️ Removed **{target['name']}** "
            "from your profile."
        )

    # =====================================
    # CLEAR FIELDS
    # =====================================

    @command(
        "👤 Profile",
        "Remove all custom profile fields"
    )
    @commands.guild_only()
    async def fieldclear(
        self,
        ctx
    ):

        fields = get_fields(
            ctx.guild.id,
            ctx.author.id
        )

        if not fields:

            await ctx.send(
                "ℹ️ You don't have any "
                "custom profile fields."
            )

            return

        db.delete(
            "profile_fields",
            "guild_id = ? AND user_id = ?",
            (
                ctx.guild.id,
                ctx.author.id
            )
        )

        await ctx.send(
            "🗑️ All custom profile fields "
            "have been removed."
        )

    # =====================================
    # RESET PROFILE
    # =====================================

    @command(
        "👤 Profile",
        "Reset your profile customization"
    )
    @commands.guild_only()
    async def profilereset(
        self,
        ctx
    ):

        get_profile(
            ctx.guild.id,
            ctx.author.id
        )

        # Keep birthday!
        db.update(
            "profiles",
            {
                "bio": None,
                "banner": None,
                "profile_color": None
            },
            "guild_id = ? AND user_id = ?",
            (
                ctx.guild.id,
                ctx.author.id
            )
        )

        db.delete(
            "profile_fields",
            "guild_id = ? AND user_id = ?",
            (
                ctx.guild.id,
                ctx.author.id
            )
        )

        await ctx.send(
            "♻️ Your profile customization "
            "has been reset.\n\n"
            "🎂 Your birthday was kept for "
            "future Edison celebrations."
        )


# =========================================
# SETUP
# =========================================

async def setup(bot):

    await bot.add_cog(
        Profile(bot)
            )
