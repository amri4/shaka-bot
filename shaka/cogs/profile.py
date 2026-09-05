import discord

from datetime import datetime

from discord.ext import commands

from utils.command import command
from utils.role_colors import parse_role_color

import mycord


# =========================================
# DATABASE
# =========================================

db = mycord.DB()


# =========================================
# CREATE PROFILE TABLE
# =========================================

try:

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

except Exception as error:

    print(
        "PunksDB profile table error:",
        error
    )


# =========================================
# CREATE CUSTOM FIELDS TABLE
# =========================================

try:

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

except Exception as error:

    print(
        "PunksDB profile fields table error:",
        error
    )


# =========================================
# SEND DATABASE ERROR
# =========================================

async def send_db_error(
    ctx,
    error
):

    error_text = (
        f"{type(error).__name__}: {error}"
    )

    # Discord message limit protection
    if len(error_text) > 1800:

        error_text = (
            error_text[:1800]
            + "\n..."
        )

    await ctx.send(
        "❌ **PunksDB Error**\n"
        f"```py\n{error_text}\n```"
    )


# =========================================
# GET PROFILE
# =========================================

def get_profile(
    guild_id,
    user_id
):

    return db.fetchone(
        "profiles",
        "guild_id = ? AND user_id = ?",
        (
            guild_id,
            user_id
        )
    )


# =========================================
# ENSURE PROFILE
# =========================================

def ensure_profile(
    guild_id,
    user_id
):

    profile = get_profile(
        guild_id,
        user_id
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

    return get_profile(
        guild_id,
        user_id
    )


# =========================================
# GET VALUE FROM PROFILE
# =========================================

def profile_value(
    profile,
    column,
    default=None
):

    if profile is None:

        return default

    # Dictionary result
    if isinstance(
        profile,
        dict
    ):

        return profile.get(
            column,
            default
        )

    # Some DB wrappers return tuples.
    # We don't assume a tuple layout here.
    return default


# =========================================
# BIRTHDAY FORMAT
# =========================================

def format_birthday(
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

        return datetime(
            2000,
            int(month),
            int(day)
        ).strftime(
            "%B %d"
        )

    except (
        ValueError,
        TypeError
    ):

        return None


# =========================================
# PROFILE COLOR
# =========================================

def get_profile_color(
    profile,
    member
):

    saved = profile_value(
        profile,
        "profile_color"
    )

    if saved is not None:

        try:

            return discord.Color(
                int(saved)
            )

        except (
            TypeError,
            ValueError
        ):

            pass

    # Fall back to member role color
    if member.color != discord.Color.default():

        return member.color

    return discord.Color.blue()


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

        # ---------------------------------
        # DATABASE
        # ---------------------------------

        try:

            profile = ensure_profile(
                ctx.guild.id,
                member.id
            )

        except Exception as error:

            await send_db_error(
                ctx,
                error
            )

            return

        # ---------------------------------
        # EMBED
        # ---------------------------------

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
        # SERVER JOINED
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
        # BIRTHDAY
        # ---------------------------------

        birthday = format_birthday(
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
    async def setbio(
        self,
        ctx,
        *,
        bio: str = None
    ):

        try:

            ensure_profile(
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
                    "📝 Your bio has been removed."
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

        except Exception as error:

            await send_db_error(
                ctx,
                error
            )

            return

        await ctx.send(
            "✅ Your profile bio has been updated."
        )

    # =====================================
    # BIRTHDAY
    # =====================================

    @command(
        "👤 Profile",
        "Save your birthday for your profile",
        usage="<DD/MM[/YYYY]>"
    )
    async def birthday(
        self,
        ctx,
        date: str = None
    ):

        if not date:

            await ctx.send(
                "❌ Usage:\n"
                "`Shaka birthday 12/08`\n"
                "or\n"
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

        if parsed is None:

            await ctx.send(
                "❌ Invalid birthday format.\n"
                "Use `DD/MM` or `DD/MM/YYYY`."
            )

            return

        # ---------------------------------
        # DATABASE
        # ---------------------------------

        try:

            ensure_profile(
                ctx.guild.id,
                ctx.author.id
            )

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

        except Exception as error:

            await send_db_error(
                ctx,
                error
            )

            return

        await ctx.send(
            "🎂 Birthday saved as "
            f"**{parsed.strftime('%B %d')}**!"
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

        try:

            ensure_profile(
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

        except Exception as error:

            await send_db_error(
                ctx,
                error
            )

            return

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
    async def banner(
        self,
        ctx,
        url: str = None
    ):

        try:

            ensure_profile(
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
                    "🖼️ Your profile banner "
                    "has been removed."
                )

                return

            if not url.startswith(
                (
                    "http://",
                    "https://"
                )
            ):

                await ctx.send(
                    "❌ Please provide a valid "
                    "image URL."
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

        except Exception as error:

            await send_db_error(
                ctx,
                error
            )

            return

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
    async def profilecolor(
        self,
        ctx,
        color: str = None
    ):

        try:

            ensure_profile(
                ctx.guild.id,
                ctx.author.id
            )

            # ---------------------------------
            # RESET COLOR
            # ---------------------------------

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

            # ---------------------------------
            # PARSE COLOR
            # ---------------------------------

            color_value = parse_role_color(
                color
            )

            if color_value is None:

                await ctx.send(
                    "❌ I don't recognize that color.\n"
                    "Use `Shaka colors` to see "
                    "the available colors."
                )

                return

            # ---------------------------------
            # SAVE
            # ---------------------------------

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

        except Exception as error:

            await send_db_error(
                ctx,
                error
            )

            return

        await ctx.send(
            f"🎨 Your profile color is now "
            f"**{color.lower()}**."
        )

    # =====================================
    # ADD CUSTOM FIELD
    # =====================================

    @command(
        "👤 Profile",
        "Add custom information to your profile",
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
                "❌ Usage:\n"
                "`Shaka fieldadd Favorite Game | "
                "Rocket League`"
            )

            return

        if "|" not in arguments:

            await ctx.send(
                "❌ Separate the name and value "
                "with `|`."
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

        try:

            # ---------------------------------
            # CHECK EXISTING
            # ---------------------------------

            rows = db.fetchall(
                "profile_fields"
            )

            existing = None

            if rows:

                for row in rows:

                    if not isinstance(
                        row,
                        dict
                    ):

                        continue

                    if (
                        row.get("guild_id")
                        == ctx.guild.id
                        and
                        row.get("user_id")
                        == ctx.author.id
                        and
                        str(
                            row.get(
                                "name",
                                ""
                            )
                        ).lower()
                        == name.lower()
                    ):

                        existing = row

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
                    f"✅ Updated **{name}**."
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

        except Exception as error:

            await send_db_error(
                ctx,
                error
            )

            return

        await ctx.send(
            f"✅ Added **{name}** to your profile."
        )

    # =====================================
    # REMOVE CUSTOM FIELD
    # =====================================

    @command(
        "👤 Profile",
        "Remove a custom profile field",
        usage="<name>"
    )
    async def fieldremove(
        self,
        ctx,
        *,
        name: str
    ):

        try:

            rows = db.fetchall(
                "profile_fields"
            )

            target = None

            if rows:

                for row in rows:

                    if not isinstance(
                        row,
                        dict
                    ):

                        continue

                    if (
                        row.get("guild_id")
                        == ctx.guild.id
                        and
                        row.get("user_id")
                        == ctx.author.id
                        and
                        str(
                            row.get(
                                "name",
                                ""
                            )
                        ).lower()
                        == name.lower()
                    ):

                        target = row

                        break

            if not target:

                await ctx.send(
                    "❌ I couldn't find that "
                    "profile field."
                )

                return

            db.delete(
                "profile_fields",
                "id = ?",
                (
                    target["id"],
                )
            )

        except Exception as error:

            await send_db_error(
                ctx,
                error
            )

            return

        await ctx.send(
            f"🗑️ Removed **{target['name']}** "
            "from your profile."
        )

    # =====================================
    # CLEAR CUSTOM FIELDS
    # =====================================

    @command(
        "👤 Profile",
        "Remove all custom profile fields"
    )
    async def fieldclear(
        self,
        ctx
    ):

        try:

            db.delete(
                "profile_fields",
                "guild_id = ? AND user_id = ?",
                (
                    ctx.guild.id,
                    ctx.author.id
                )
            )

        except Exception as error:

            await send_db_error(
                ctx,
                error
            )

            return

        await ctx.send(
            "🗑️ All your custom profile "
            "fields have been removed."
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

        try:

            ensure_profile(
                ctx.guild.id,
                ctx.author.id
            )

            # IMPORTANT:
            # Birthday is intentionally preserved
            # for Edison.

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

        except Exception as error:

            await send_db_error(
                ctx,
                error
            )

            return

        await ctx.send(
            "♻️ Your profile customization "
            "has been reset.\n"
            "🎂 Your birthday was kept."
        )

    # =====================================
    # COMMAND ERROR
    # =====================================

    @commands.Cog.listener()
    async def on_command_error(
        self,
        ctx,
        error
    ):

        # Only handle errors belonging
        # to commands from this cog.

        if ctx.command is None:

            return

        if ctx.command.cog is not self:

            return

        # ---------------------------------
        # MISSING ARGUMENT
        # ---------------------------------

        if isinstance(
            error,
            commands.MissingRequiredArgument
        ):

            await ctx.send(
                "❌ Missing required argument.\n"
                f"Use `{self.bot.command_prefix}"
                f" {ctx.command.name} "
                f"{ctx.command.signature}`"
            )

            return

        # ---------------------------------
        # BAD MEMBER
        # ---------------------------------

        if isinstance(
            error,
            commands.MemberNotFound
        ):

            await ctx.send(
                "❌ I couldn't find that member."
            )

            return

        # ---------------------------------
        # CONVERSION ERROR
        # ---------------------------------

        if isinstance(
            error,
            commands.BadArgument
        ):

            await ctx.send(
                f"❌ Invalid argument.\n"
                f"`{error}`"
            )

            return

        # ---------------------------------
        # OTHER ERROR
        # ---------------------------------

        original = getattr(
            error,
            "original",
            error
        )

        text = (
            f"{type(original).__name__}: "
            f"{original}"
        )

        if len(text) > 1800:

            text = (
                text[:1800]
                + "\n..."
            )

        await ctx.send(
            "❌ **Profile Command Error**\n"
            f"```py\n{text}\n```"
        )

        print(
            "Profile command error:",
            repr(original)
        )


# =========================================
# SETUP
# =========================================

async def setup(bot):

    await bot.add_cog(
        Profile(bot)
    )
