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
    # GET REACTION ROLE CHANNEL
    # =====================================

    def get_reaction_role_channel(
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

        # server_config:
        #
        # 0 = guild_id
        # 1 = welcome_channel_id
        # 2 = goodbye_channel_id
        # 3 = welcome_role_id
        # 4 = member_role_id
        # 5 = reaction_role_channel_id

        channel_id = data[5]

        if not channel_id:
            return None

        return guild.get_channel(
            channel_id
        )

    # =====================================
    # WAIT FOR USER MESSAGE
    # =====================================

    async def wait_for_message(
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
    # PARSE COLOR
    # =====================================

    def parse_color(
        self,
        value
    ):

        value = value.casefold().strip()

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

        # HEX
        if value.startswith("#"):
            value = value[1:]

        try:

            if len(value) != 6:
                return None

            return discord.Color(
                int(value, 16)
            )

        except ValueError:

            return None

    # =====================================
    # CREATE PANEL
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
                "creation session running."
            )

            return

        channel = self.get_reaction_role_channel(
            ctx.guild
        )

        if not channel:

            await ctx.send(
                "❌ No Reaction Role Channel has "
                "been configured.\n\n"
                "Ask an administrator to configure "
                "one first."
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
                "📝 **What should the panel title be?**\n"
                "Type `cancel` to cancel."
            )

            message = await self.wait_for_message(
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
                "📄 **What should the panel description be?**"
            )

            message = await self.wait_for_message(
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
                "🎨 **What embed color should I use?**\n\n"
                "Examples:\n"
                "`blue`\n"
                "`red`\n"
                "`gold`\n"
                "`#5865F2`"
            )

            message = await self.wait_for_message(
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
                    "❌ Invalid color.\n"
                    "Use a color name or a 6-digit HEX code."
                )

                return

            # =================================
            # ROLES
            # =================================

            await ctx.send(
                "🎭 **Now add the reaction roles.**\n\n"
                "Send one at a time using:\n"
                "`emoji role`\n\n"
                "Example:\n"
                "`🎮 Gamer`\n\n"
                "Type `done` when you're finished."
            )

            entries = []

            while True:

                message = await self.wait_for_message(
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
                        "❌ Invalid format.\n"
                        "Use `emoji role`."
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
                        "it is higher than or equal to my "
                        "highest role."
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
                    f"✅ Added {emoji} → {role.mention}",
                    allowed_mentions=discord.AllowedMentions(
                        roles=False
                    )
                )

            if not entries:

                await ctx.send(
                    "❌ You didn't add any reaction roles."
                )

                return

            # =================================
            # CREATE EMBED
            # =================================

            role_lines = "\n".join(
                f"{entry['emoji']} {entry['role'].mention}"
                for entry in entries
            )

            embed = discord.Embed(
                title=title,
                description=(
                    f"{description}\n\n"
                    f"{role_lines}"
                ),
                color=color
            )

            embed.set_footer(
                text="React below to receive a role."
            )

            # =================================
            # PREVIEW
            # =================================

            await ctx.send(
                "👀 **Panel Preview:**",
                embed=embed,
                allowed_mentions=discord.AllowedMentions(
                    roles=False
                )
            )

            await ctx.send(
                "Send `yes` to create the panel "
                "or `no` to cancel."
            )

            message = await self.wait_for_message(
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

            panel_id = db.insert(
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

            # =================================
            # SAVE ROLES + REACTIONS
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
    # LIST PANELS
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
            "reactionrole_panels",
            "guild_id = ?",
            (ctx.guild.id,)
        )

        if not panels:

            await ctx.send(
                "📭 This server has no "
                "reaction-role panels."
            )

            return

        lines = []

        for panel in panels:

            channel = ctx.guild.get_channel(
                panel[2]
            )

            entries = db.fetchall(
                "reactionrole_entries",
                "panel_id = ?",
                (panel[0],)
            )

            lines.append(
                f"**{panel[4]}**\n"
                f"📢 {channel.mention if channel else 'Unknown channel'}\n"
                f"🎭 {len(entries)} reaction roles"
            )

        embed = discord.Embed(
            title="🔵 Reaction Role Panels",
            description="\n\n".join(lines),
            color=discord.Color.blue()
        )

        await ctx.send(
            embed=embed
        )

    # =====================================
    # DELETE PANEL
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
            "reactionrole_panels",
            "guild_id = ?",
            (ctx.guild.id,)
        )

        if not panels:

            await ctx.send(
                "📭 This server has no "
                "reaction-role panels."
            )

            return

        lines = []

        for index, panel in enumerate(
            panels,
            start=1
        ):

            lines.append(
                f"**{index}.** {panel[4]}"
            )

        await ctx.send(
            "🗑️ **Which panel do you want to delete?**\n\n"
            + "\n".join(lines)
            + "\n\n"
            "Type the number or `cancel`."
        )

        message = await self.wait_for_message(
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

        await self.delete_panel(
            panel
        )

        await ctx.send(
            f"🗑️ Deleted **{panel[4]}**."
        )

    # =====================================
    # DELETE PANEL DATA
    # =====================================

    async def delete_panel_data(
        self,
        panel_id
    ):

        db.delete(
            "reactionrole_entries",
            "panel_id = ?",
            (panel_id,)
        )

        db.delete(
            "reactionrole_panels",
            "id = ?",
            (panel_id,)
        )

    # =====================================
    # DELETE PANEL
    # =====================================

    async def delete_panel(
        self,
        panel
    ):

        channel = self.bot.get_channel(
            panel[2]
        )

        if channel:

            try:

                message = await channel.fetch_message(
                    panel[3]
                )

                await message.delete()

            except (
                discord.NotFound,
                discord.Forbidden,
                discord.HTTPException
            ):

                pass

        await self.delete_panel_data(
            panel[0]
        )

    # =====================================
    # REACTION ADD
    # =====================================

    @commands.Cog.listener()
    async def on_raw_reaction_add(
        self,
        payload
    ):

        if payload.guild_id is None:
            return

        if self.bot.user and (
            payload.user_id == self.bot.user.id
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
    # REACTION REMOVE
    # =====================================

    @commands.Cog.listener()
    async def on_raw_reaction_remove(
        self,
        payload
    ):

        if payload.guild_id is None:
            return

        if self.bot.user and (
            payload.user_id == self.bot.user.id
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

    async def cleanup_panels(
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

                await self.delete_panel_data(
                    panel[0]
                )

            except (
                discord.Forbidden,
                discord.HTTPException
            ):

                pass

    # =====================================
    # BOT READY
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

        await self.cleanup_panels()

    # =====================================
    # ERROR HANDLING
    # =====================================

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
                "❌ You need **Manage Roles** "
                "to use this command."
            )


# =========================================
# SETUP
# =========================================

async def setup(bot):

    await bot.add_cog(
        ReactionRoles(bot)
    )
