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
# PROFILES TABLE
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
# PROFILE FIELDS TABLE
# =========================================

db.create_table(
    "profile_fields",
    """
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER,
    user_id INTEGER,
    name TEXT,
    value TEXT
    """
)


# =========================================
# GET PROFILE
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
            "user_id",
            "birthday_month",
            "birthday_day",
            "birthday_year",
            "bio",
            "banner",
            "profile_color"
        ),
        (
            guild_id,
            user_id,
            None,
            None,
            None,
            None,
            None,
            None
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
# GET PROFILE VALUE
# =========================================

def profile_value(
    profile,
    key
):

    if not profile:
        return None

    if isinstance(
        profile,
        dict
    ):

        return profile.get(key)

    return None


# =========================================
# GET EMBED COLOR
# =========================================

def get_embed_color(
    profile,
    member
):

    profile_color = profile_value(
        profile,
        "profile_color"
    )

    if profile_color is not None:

        try:

            return discord.Color(
                int(profile_color)
            )

        except (
            ValueError,
            TypeError
        ):

            pass

    if member.color != discord.Color.default():

        return member.color

    return discord.Color.blue()


# =========================================
# GET BIRTHDAY
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

    except ValueError:

        return None


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
            color=get_embed_color(
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
            name="Display Name",
            value=member.display_name,
            inline=True
        )

        # ---------------------------------
        # JOINED SERVER
        # ---------------------------------

        if member.joined_at:

            embed.add_field(
                name="Joined Server",
                value=discord.utils.format_dt(
                    member.joined_at,
                    "D"
                ),
                inline=True
            )

        # ---------------------------------
        # ACCOUNT CREATED
        # ---------------------------------

        embed.add_field(
            name="Account Created",
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
                name="About",
                value=bio,
                inline=False
            )

        # ---------------------------------
        # CUSTOM FIELDS
        # ---------------------------------

        fields = db.fetchall(
            "profile_fields"
        )

        for field in fields:

            if field.get(
                "guild_id"
            ) != ctx.guild.id:

                continue

            if field.get(
                "user_id"
            ) != member.id:

                continue

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
        "Set or remove your profile bio",
        usage="<bio>"
    )
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
                "❌ Your bio cannot be longer "
                "than **500 characters**."
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
    # SET BIRTHDAY
    # =====================================

    @command(
        "👤 Profile",
        "Set your birthday for your profile and future celebrations",
        usage="<DD/MM[/YYYY]>"
    )
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

        try:

            parsed = datetime.strptime(
                date,
                "%d/%m"
            )

        except ValueError:

            try:

                parsed = datetime.strptime(
                    date,
                    "%d/%m/%Y"
                )

            except ValueError:

                pass

        if not parsed:

            await ctx.send(
                "❌ Invalid birthday format.\n\n"
                "Use `DD/MM` or `DD/MM/YYYY`."
            )

            return

        parts = date.split("/")

        year = None

        if len(parts) == 3:

            year = parsed.year

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

        birthday_text = parsed.strftime(
            "%B %d"
        )

        await ctx.send(
            f"🎂 Your birthday has been set to "
            f"**{birthday_text}**!"
        )

    # =====================================
    # REMOVE BIRTHDAY
    # =====================================

    @command(
        "👤 Profile",
        "Remove your saved birthday"
    )
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
            "🎂 Your saved birthday has been removed."
        )

    # =====================================
    # SET BANNER
    # =====================================

    @command(
        "👤 Profile",
        "Set or remove your profile banner",
        usage="<image URL>"
    )
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
                "https://",
                "http://"
            )
        ):

            await ctx.send(
                "❌ Please provide a valid image URL."
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
        "Set or remove your profile embed color",
        usage="<color>"
    )
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
                "❌ I don't recognize that color.\n\n"
                "Use `Shaka colors` to see "
                "the available colors."
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
            f"🎨 Your profile color has been "
            f"set to **{color.lower()}**."
        )

    # =====================================
    # ADD / EDIT FIELD
    # =====================================

    @command(
        "👤 Profile",
        "Add or edit custom information on your profile",
        usage="<name> | <value>"
    )
    async def fieldadd(
        self,
        ctx,
        *,
        arguments: str = None
    ):

        if not arguments:

            await ctx.send(
                "❌ Please provide a field.\n\n"
                "Example:\n"
                "`Shaka fieldadd Favorite Game | "
                "Rocket League`"
            )

            return

        if "|" not in arguments:

            await ctx.send(
                "❌ Separate the field name "
                "and value with `|`."
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
                "❌ Both the field name "
                "and value are required."
            )

            return

        if len(name) > 50:

            await ctx.send(
                "❌ Field names can only be "
                "**50 characters** long."
            )

            return

        if len(value) > 200:

            await ctx.send(
                "❌ Field values can only be "
                "**200 characters** long."
            )

            return

        # ---------------------------------
        # FIND EXISTING FIELD
        # ---------------------------------

        fields = db.fetchall(
            "profile_fields"
        )

        existing = None

        for field in fields:

            if (
                field.get("guild_id")
                == ctx.guild.id
                and
                field.get("user_id")
                == ctx.author.id
                and
                field.get("name")
                == name
            ):

                existing = field

                break

        if existing:

            db.update(
                "profile_fields",
                {
                    "value": value
                },
                "id = ?",
                (
                    existing["id"],
                )
            )

            await ctx.send(
                f"✅ **{name}** has been updated."
            )

            return

        # ---------------------------------
        # COUNT FIELDS
        # ---------------------------------

        user_fields = []

        for field in fields:

            if (
                field.get("guild_id")
                == ctx.guild.id
                and
                field.get("user_id")
                == ctx.author.id
            ):

                user_fields.append(
                    field
                )

        if len(user_fields) >= 10:

            await ctx.send(
                "❌ You can have a maximum "
                "of **10 custom fields**."
            )

            return

        # ---------------------------------
        # CREATE FIELD
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
            f"✅ Added **{name}** "
            "to your profile."
        )

    # =====================================
    # REMOVE FIELD
    # =====================================

    @command(
        "👤 Profile",
        "Remove a custom field from your profile",
        usage="<name>"
    )
    async def fieldremove(
        self,
        ctx,
        *,
        name: str
    ):

        fields = db.fetchall(
            "profile_fields"
        )

        field = None

        for item in fields:

            if (
                item.get("guild_id")
                == ctx.guild.id
                and
                item.get("user_id")
                == ctx.author.id
                and
                item.get("name")
                == name
            ):

                field = item

                break

        if not field:

            await ctx.send(
                "❌ I couldn't find that "
                "profile field."
            )

            return

        db.delete(
            "profile_fields",
            "id = ?",
            (
                field["id"],
            )
        )

        await ctx.send(
            f"🗑️ Removed **{name}** "
            "from your profile."
        )

    # =====================================
    # CLEAR FIELDS
    # =====================================

    @command(
        "👤 Profile",
        "Remove all custom fields from your profile"
    )
    async def fieldclear(
        self,
        ctx
    ):

        db.delete(
            "profile_fields",
            "guild_id = ? AND user_id = ?",
            (
                ctx.guild.id,
                ctx.author.id
            )
        )

        await ctx.send(
            "🗑️ All your custom profile fields "
            "have been removed."
        )

    # =====================================
    # RESET PROFILE
    # =====================================

    @command(
        "👤 Profile",
        "Reset your profile customization"
    )
    async def profilereset(
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
            "Your birthday was kept because "
            "Edison will use it for birthday "
            "celebrations. 🎂"
        )


# =========================================
# SETUP
# =========================================

async def setup(bot):

    await bot.add_cog(
        Profile(bot)
)
