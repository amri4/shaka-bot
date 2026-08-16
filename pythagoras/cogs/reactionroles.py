import asyncio

import discord
from discord.ext import commands

import mycord
from utils.command import command


db = mycord.PunksDB()


# =========================================
# DATABASE
# =========================================

db.create_table(
    "reactionrole_panels",
    """
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id INTEGER NOT NULL,
    channel_id INTEGER NOT NULL,
    message_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    color INTEGER NOT NULL
    """
)


db.create_table(
    "reactionrole_entries",
    """
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    panel_id INTEGER NOT NULL,
    emoji TEXT NOT NULL,
    role_id INTEGER NOT NULL
    """
)


# =========================================
# REACTION ROLES
# =========================================

class ReactionRoles(commands.Cog):

    def __init__(self, bot):

        self.bot = bot
        self.sessions = set()

    # =====================================
    # GET CONFIGURED CHANNEL
    # =====================================

    def get_reaction_channel(
        self,
        guild
    ):

        data = db.fetchone(
            "server_config",
            "guild_id = ?",
            (guild.id,)
        )

        if not data:
            return None

        if len(data) < 6:
            return None

        channel_id = data[5]

        if not channel_id:
            return None

        return guild.get_channel(
            channel_id
        )

    # =====================================
    # WAIT FOR MESSAGE
    # =====================================

    async def wait_message(
        self,
        ctx
    ):

        def check(message):

            return (
                message.author.id == ctx.author.id
                and message.channel.id == ctx.channel.id
            )

        try:

            return await self.bot.wait_for(
                "message",
                timeout=120,
                check=check
            )

        except asyncio.TimeoutError:

            await ctx.send(
                "⌛ Reaction-role setup timed out."
            )

            return None

    # =====================================
    # FIND ROLE
    # =====================================

    def find_role(
        self,
        guild,
        text
    ):

        text = text.strip()

        # Role mention
        if (
            text.startswith("<@&")
            and text.endswith(">")
        ):

            role_id = text[3:-1]

            if role_id.isdigit():

                return guild.get_role(
                    int(role_id)
                )

        # Role ID
        if text.isdigit():

            role = guild.get_role(
                int(text)
            )

            if role:

                return role

        # Exact role name
        lowered = text.casefold()

        for role in guild.roles:

            if role.name.casefold() == lowered:

                return role

        # Partial role name
        matches = [
            role
            for role in guild.roles
            if lowered in role.name.casefold()
        ]

        if len(matches) == 1:

            return matches[0]

        return None

    # =====================================
    # COLOR
    # =====================================

    def parse_color(
        self,
        value
    ):

        value = value.strip().casefold()

        colors = {

            "red": discord.Color.red(),
            "blue": discord.Color.blue(),
            "green": discord.Color.green(),
            "purple": discord.Color.purple(),
            "orange": discord.Color.orange(),
            "gold": discord.Color.gold(),
            "teal": discord.Color.teal(),
            "blurple": discord.Color.blurple(),

            "dark_red": discord.Color.dark_red(),
            "dark_blue": discord.Color.dark_blue(),
            "dark_green": discord.Color.dark_green(),
            "dark_purple": discord.Color.dark_purple(),
            "dark_orange": discord.Color.dark_orange(),
            "dark_teal": discord.Color.dark_teal(),

            "default": discord.Color.blue()
        }

        if value in colors:

            return colors[value]

        if value.startswith("#"):

            value = value[1:]

        if len(value) != 6:

            return None

        try:

            return discord.Color(
                int(value, 16)
            )

        except ValueError:

            return None

    # =====================================
    # CREATE
    # =====================================

    @command(
        "🔵 Reaction Roles",
        "Create a reaction-role panel"
    )
    @commands.has_guild_permissions(
        manage_roles=True
    )
    async def rrcreate(
        self,
        ctx
    ):

        if ctx.author.id in self.sessions:

            await ctx.send(
                "❌ You already have a reaction-role "
                "setup running."
            )

            return

        channel = self.get_reaction_channel(
            ctx.guild
        )

        if not channel:

            await ctx.send(
                "❌ No reaction-role channel is configured.\n\n"
                "Use `setrrchannel #channel` first."
            )

            return

        self.sessions.add(
            ctx.author.id
        )

        try:

            # =================================
            # TITLE
            # =================================

            await ctx.send(
                "📝 **Step 1/4 — Title**\n\n"
                "Send the title of the panel.\n"
                "Type `cancel` to stop."
            )

            message = await self.wait_message(
                ctx
            )

            if not message:
                return

            if message.content.casefold() == "cancel":

                await ctx.send(
                    "❌ Cancelled."
                )

                return

            title = message.content

            # =================================
            # DESCRIPTION
            # =================================

            await ctx.send(
                "📄 **Step 2/4 — Description**\n\n"
                "Send the panel description."
            )

            message = await self.wait_message(
                ctx
            )

            if not message:
                return

            if message.content.casefold() == "cancel":

                await ctx.send(
                    "❌ Cancelled."
                )

                return

            description = message.content

            # =================================
            # COLOR
            # =================================

            await ctx.send(
                "🎨 **Step 3/4 — Embed Color**\n\n"
                "Send a color name or HEX code.\n\n"
                "Examples:\n"
                "`blue`\n"
                "`red`\n"
                "`purple`\n"
                "`#5865F2`"
            )

            message = await self.wait_message(
                ctx
            )

            if not message:
                return

            if message.content.casefold() == "cancel":

                await ctx.send(
                    "❌ Cancelled."
                )

                return

            color = self.parse_color(
                message.content
            )

            if color is None:

                await ctx.send(
                    "❌ Invalid color."
                )

                return

            # =================================
            # ROLES
            # =================================

            await ctx.send(
                "🎭 **Step 4/4 — Reaction Roles**\n\n"
                "Add roles using:\n"
                "`🎮 Gamer`\n\n"
                "or:\n"
                "`🎮 @Gamer`\n\n"
                "Send `done` when finished."
            )

            entries = []

            while True:

                message = await self.wait_message(
                    ctx
                )

                if not message:
                    return

                content = message.content.strip()

                if content.casefold() == "done":

                    break

                if content.casefold() == "cancel":

                    await ctx.send(
                        "❌ Cancelled."
                    )

                    return

                parts = content.split(
                    maxsplit=1
                )

                if len(parts) != 2:

                    await ctx.send(
                        "❌ Use:\n"
                        "`emoji role_name`"
                    )

                    continue

                emoji = parts[0]
                role_text = parts[1]

                role = self.find_role(
                    ctx.guild,
                    role_text
                )

                if not role:

                    await ctx.send(
                        "❌ I couldn't find that role."
                    )

                    continue

                if role == ctx.guild.default_role:

                    await ctx.send(
                        "❌ You can't use @everyone."
                    )

                    continue

                if role >= ctx.guild.me.top_role:

                    await ctx.send(
                        "❌ I can't manage that role because "
                        "it is above my highest role."
                    )

                    continue

                if any(
                    entry["emoji"] == emoji
                    for entry in entries
                ):

                    await ctx.send(
                        "❌ That emoji is already being used."
                    )

                    continue

                entries.append(
                    {
                        "emoji": emoji,
                        "role": role
                    }
                )

                await ctx.send(
                    f"✅ Added `{emoji}` → **{role.name}**"
                )

            if not entries:

                await ctx.send(
                    "❌ No reaction roles were added."
                )

                return

            # =================================
            # PREVIEW
            # =================================

            role_text = "\n".join(
                f"{entry['emoji']} {entry['role'].mention}"
                for entry in entries
            )

            embed = discord.Embed(
                title=title,
                description=(
                    f"{description}\n\n"
                    f"{role_text}"
                ),
                color=color
            )

            embed.set_footer(
                text=(
                    "React below to receive or remove a role."
                )
            )

            await ctx.send(
                "👀 **Preview:**",
                embed=embed,
                allowed_mentions=discord.AllowedMentions(
                    roles=False
                )
            )

            # =================================
            # CONFIRM
            # =================================

            await ctx.send(
                "Send `yes` to create the panel.\n"
                "Send `no` to cancel."
            )

            message = await self.wait_message(
                ctx
            )

            if not message:
                return

            if message.content.casefold() != "yes":

                await ctx.send(
                    "❌ Cancelled."
                )

                return

            # =================================
            # SEND PANEL
            # =================================

            panel_message = await channel.send(
                embed=embed,
                allowed_mentions=discord.AllowedMentions(
                    roles=False
                )
            )

            # =================================
            # SAVE PANEL
            # =================================

            db.insert(
                "reactionrole_panels",
                (
                    "guild_id, "
                    "channel_id, "
                    "message_id, "
                    "title, "
                    "description, "
                    "color"
                ),
                (
                    ctx.guild.id,
                    channel.id,
                    panel_message.id,
                    title,
                    description,
                    color.value
                )
            )

            panel = db.fetchone(
                "reactionrole_panels",
                "guild_id = ? AND message_id = ?",
                (
                    ctx.guild.id,
                    panel_message.id
                )
            )

            if not panel:

                await ctx.send(
                    "⚠️ The panel was sent, but I couldn't "
                    "find its database record."
                )

                return

            panel_id = panel[0]

            # =================================
            # SAVE ROLES
            # =================================

            for entry in entries:

                db.insert(
                    "reactionrole_entries",
                    (
                        "panel_id, "
                        "emoji, "
                        "role_id"
                    ),
                    (
                        panel_id,
                        entry["emoji"],
                        entry["role"].id
                    )
                )

                try:

                    await panel_message.add_reaction(
                        entry["emoji"]
                    )

                except discord.HTTPException:

                    pass

            await ctx.send(
                f"✅ Reaction-role panel created in "
                f"{channel.mention}."
            )

        finally:

            self.sessions.discard(
                ctx.author.id
            )

    # =====================================
    # LIST
    # =====================================

    @command(
        "🔵 Reaction Roles",
        "Show reaction-role panels"
    )
    async def rrlist(
        self,
        ctx
    ):

        panels = db.fetchall(
            "reactionrole_panels"
        )

        panels = [
            panel
            for panel in panels
            if panel[1] == ctx.guild.id
        ]

        if not panels:

            await ctx.send(
                "📭 This server has no "
                "reaction-role panels."
            )

            return

        lines = []

        for number, panel in enumerate(
            panels,
            start=1
        ):

            channel = ctx.guild.get_channel(
                panel[2]
            )

            entries = db.fetchall(
                "reactionrole_entries"
            )

            entries = [
                entry
                for entry in entries
                if entry[1] == panel[0]
            ]

            lines.append(
                f"**{number}. {panel[4]}**\n"
                f"📢 "
                f"{channel.mention if channel else 'Unknown channel'}\n"
                f"🎭 {len(entries)} roles"
            )

        embed = discord.Embed(
            title="🔵 Reaction Role Panels",
            description="\n\n".join(lines),
            color=discord.Color.blue()
        )

        embed.set_footer(
            text=f"{len(panels)} panels"
        )

        await ctx.send(
            embed=embed
        )

    # =====================================
    # DELETE
    # =====================================

    @command(
        "🔵 Reaction Roles",
        "Delete a reaction-role panel"
    )
    @commands.has_guild_permissions(
        manage_roles=True
    )
    async def rrdelete(
        self,
        ctx
    ):

        panels = db.fetchall(
            "reactionrole_panels"
        )

        panels = [
            panel
            for panel in panels
            if panel[1] == ctx.guild.id
        ]

        if not panels:

            await ctx.send(
                "📭 This server has no "
                "reaction-role panels."
            )

            return

        lines = "\n".join(
            f"**{number}.** {panel[4]}"
            for number, panel in enumerate(
                panels,
                start=1
            )
        )

        await ctx.send(
            "🗑️ **Which panel should I delete?**\n\n"
            f"{lines}\n\n"
            "Send the number or `cancel`."
        )

        message = await self.wait_message(
            ctx
        )

        if not message:
            return

        if message.content.casefold() == "cancel":

            await ctx.send(
                "❌ Cancelled."
            )

            return

        try:

            index = int(
                message.content
            ) - 1

            panel = panels[index]

        except (
            ValueError,
            IndexError
        ):

            await ctx.send(
                "❌ Invalid panel number."
            )

            return

        channel = self.bot.get_channel(
            panel[2]
        )

        if channel:

            try:

                panel_message = await channel.fetch_message(
                    panel[3]
                )

                await panel_message.delete()

            except (
                discord.NotFound,
                discord.Forbidden,
                discord.HTTPException
            ):

                pass

        db.delete(
            "reactionrole_entries",
            "panel_id = ?",
            (panel[0],)
        )

        db.delete(
            "reactionrole_panels",
            "id = ?",
            (panel[0],)
        )

        await ctx.send(
            f"🗑️ Deleted **{panel[4]}**."
        )

    # =====================================
    # ADD ROLE
    # =====================================

    @commands.Cog.listener()
    async def on_raw_reaction_add(
        self,
        payload
    ):

        if payload.guild_id is None:
            return

        if (
            self.bot.user
            and payload.user_id == self.bot.user.id
        ):
            return

        panel = db.fetchone(
            "reactionrole_panels",
            "guild_id = ? AND message_id = ?",
            (
                payload.guild_id,
                payload.message_id
            )
        )

        if not panel:
            return

        emoji = str(
            payload.emoji
        )

        entry = db.fetchone(
            "reactionrole_entries",
            "panel_id = ? AND emoji = ?",
            (
                panel[0],
                emoji
            )
        )

        if not entry:
            return

        guild = self.bot.get_guild(
            payload.guild_id
        )

        if not guild:
            return

        role = guild.get_role(
            entry[3]
        )

        if not role:
            return

        member = guild.get_member(
            payload.user_id
        )

        if not member:
            return

        if role >= guild.me.top_role:
            return

        try:

            await member.add_roles(
                role,
                reason="Reaction role"
            )

        except discord.HTTPException:

            pass

    # =====================================
    # REMOVE ROLE
    # =====================================

    @commands.Cog.listener()
    async def on_raw_reaction_remove(
        self,
        payload
    ):

        if payload.guild_id is None:
            return

        if (
            self.bot.user
            and payload.user_id == self.bot.user.id
        ):
            return

        panel = db.fetchone(
            "reactionrole_panels",
            "guild_id = ? AND message_id = ?",
            (
                payload.guild_id,
                payload.message_id
            )
        )

        if not panel:
            return

        emoji = str(
            payload.emoji
        )

        entry = db.fetchone(
            "reactionrole_entries",
            "panel_id = ? AND emoji = ?",
            (
                panel[0],
                emoji
            )
        )

        if not entry:
            return

        guild = self.bot.get_guild(
            payload.guild_id
        )

        if not guild:
            return

        role = guild.get_role(
            entry[3]
        )

        if not role:
            return

        member = guild.get_member(
            payload.user_id
        )

        if not member:
            return

        if role >= guild.me.top_role:
            return

        try:

            await member.remove_roles(
                role,
                reason="Reaction role removed"
            )

        except discord.HTTPException:

            pass

    # =====================================
    # CLEAN DELETED PANELS
    # =====================================

    async def cleanup_deleted_panels(
        self
    ):

        panels = db.fetchall(
            "reactionrole_panels"
        )

        for panel in panels:

            channel = self.bot.get_channel(
                panel[2]
            )

            if not channel:
                continue

            try:

                await channel.fetch_message(
                    panel[3]
                )

            except discord.NotFound:

                db.delete(
                    "reactionrole_entries",
                    "panel_id = ?",
                    (panel[0],)
                )

                db.delete(
                    "reactionrole_panels",
                    "id = ?",
                    (panel[0],)
                )

            except (
                discord.Forbidden,
                discord.HTTPException
            ):

                pass

    # =====================================
    # READY
    # =====================================

    @commands.Cog.listener()
    async def on_ready(
        self
    ):

        if getattr(
            self,
            "_cleanup_done",
            False
        ):

            return

        self._cleanup_done = True

        await self.cleanup_deleted_panels()


# =========================================
# SETUP
# =========================================

async def setup(bot):

    await bot.add_cog(
        ReactionRoles(bot)
    )
