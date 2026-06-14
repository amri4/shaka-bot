import discord
from discord.ext import commands

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = mycord.Bot()  # assumes you set bot.db = DB()

        # tables
        self.db.create_table(
            "reaction_roles",
            """
            message_id INTEGER,
            emoji TEXT,
            role_id INTEGER
            """
        )

        self.db.create_table(
            "reaction_role_messages",
            """
            message_id INTEGER PRIMARY KEY,
            guild_id INTEGER,
            channel_id INTEGER
            """
        )

    # =========================
    # SETUP COMMAND
    # =========================
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reactionrole(self, ctx):

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        await ctx.send("📢 Mention the channel for the reaction role message.")

        msg = await self.bot.wait_for("message", check=check, timeout=300)

        if not msg.channel_mentions:
            return await ctx.send("❌ You must mention a channel.")

        channel = msg.channel_mentions[0]

        await ctx.send("📝 Enter embed title:")
        title = (await self.bot.wait_for("message", check=check, timeout=300)).content

        await ctx.send("📝 Enter embed description:")
        description = (await self.bot.wait_for("message", check=check, timeout=300)).content

        await ctx.send("🎨 Enter color (hex like #FFAA00):")
        color_msg = (await self.bot.wait_for("message", check=check, timeout=300)).content

        try:
            color = discord.Color(int(color_msg.replace("#", ""), 16))
        except:
            color = discord.Color.blue()

        # =========================
        # THUMBNAIL (UPLOAD ONLY)
        # =========================
        thumbnail_url = None
        await ctx.send("🖼️ Upload thumbnail image or type `skip`")

        thumb_msg = await self.bot.wait_for("message", check=check, timeout=300)

        if thumb_msg.content.lower() != "skip" and thumb_msg.attachments:
            att = thumb_msg.attachments[0]
            if att.content_type and att.content_type.startswith("image/"):
                thumbnail_url = att.url

        # =========================
        # MAIN IMAGE (UPLOAD ONLY)
        # =========================
        image_url = None
        await ctx.send("🖼️ Upload main image or type `skip`")

        img_msg = await self.bot.wait_for("message", check=check, timeout=300)

        if img_msg.content.lower() != "skip" and img_msg.attachments:
            att = img_msg.attachments[0]
            if att.content_type and att.content_type.startswith("image/"):
                image_url = att.url

        # =========================
        # CREATE EMBED
        # =========================
        embed = discord.Embed(
            title=title,
            description=description,
            color=color
        )

        if thumbnail_url:
            embed.set_thumbnail(url=thumbnail_url)

        if image_url:
            embed.set_image(url=image_url)

        message = await channel.send(embed=embed)

        # save message
        self.db.insert(
            "reaction_role_messages",
            "message_id, guild_id, channel_id",
            (message.id, ctx.guild.id, channel.id)
        )

        # =========================
        # ROLE SETUP LOOP
        # =========================
        roles = {}

        while True:
            await ctx.send("😀 Send emoji for role (or type `done`)")

            emoji_msg = await self.bot.wait_for("message", check=check, timeout=300)

            if emoji_msg.content.lower() == "done":
                break

            emoji = emoji_msg.content

            await ctx.send("🏷️ Mention the role for that emoji:")

            role_msg = await self.bot.wait_for("message", check=check, timeout=300)

            if not role_msg.role_mentions:
                await ctx.send("❌ Invalid role.")
                continue

            role = role_msg.role_mentions[0]

            roles[emoji] = role.id

            # save to db
            self.db.insert(
                "reaction_roles",
                "message_id, emoji, role_id",
                (message.id, emoji, role.id)
            )

            await message.add_reaction(emoji)

        await ctx.send(f"✅ Reaction role created!\nMessage ID: `{message.id}`")

    # =========================
    # ADD ROLE
    # =========================
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        data = self.db.fetchone(
            "reaction_roles",
            "message_id = ? AND emoji = ?",
            (payload.message_id, str(payload.emoji))
        )

        if not data:
            return

        role_id = data[2]

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        member = guild.get_member(payload.user_id)
        if not member:
            return

        role = guild.get_role(role_id)
        if role:
            await member.add_roles(role)

    # =========================
    # REMOVE ROLE
    # =========================
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):

        data = self.db.fetchone(
            "reaction_roles",
            "message_id = ? AND emoji = ?",
            (payload.message_id, str(payload.emoji))
        )

        if not data:
            return

        role_id = data[2]

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        member = guild.get_member(payload.user_id)
        if not member:
            return

        role = guild.get_role(role_id)
        if role:
            await member.remove_roles(role)


async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))
