import discord
from discord.ext import commands

import mycord


db = mycord.PunksDB()


class Welcome(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =========================================
    # GET SERVER CONFIG
    # =========================================

    def get_config(self, guild_id):

        return db.fetchone(
            "server_config",
            "guild_id = ?",
            (guild_id,)
        )

    # =========================================
    # MEMBER JOIN
    # =========================================

    @commands.Cog.listener()
    async def on_member_join(self, member):

        data = self.get_config(member.guild.id)

        if not data:
            return

        welcome_channel_id = data[1]
        welcome_role_id = data[3]
        member_role_id = data[4]

        # -------------------------------------
        # GET WELCOME CHANNEL
        # -------------------------------------

        channel = None

        if welcome_channel_id:
            channel = member.guild.get_channel(
                welcome_channel_id
            )

        # -------------------------------------
        # ADD WELCOME ROLE
        # -------------------------------------

        if welcome_role_id:

            role = member.guild.get_role(
                welcome_role_id
            )

            if role:

                try:
                    await member.add_roles(
                        role,
                        reason="Automatic welcome role"
                    )

                except discord.Forbidden:
                    pass

        # -------------------------------------
        # ADD MEMBER ROLE
        # -------------------------------------

        if member_role_id:

            role = member.guild.get_role(
                member_role_id
            )

            if role:

                try:
                    await member.add_roles(
                        role,
                        reason="Automatic member role"
                    )

                except discord.Forbidden:
                    pass

        # -------------------------------------
        # SEND WELCOME MESSAGE
        # -------------------------------------

        if not channel:
            return

        embed = discord.Embed(
            title="🏴‍☠️ NEW PIRATE ABOARD!",
            description=(
                f"Welcome to **{member.guild.name}**, "
                f"{member.mention}!\n\n"
                "⚓ Your journey begins here.\n"
                "Choose your path and set sail!"
            ),
            color=discord.Color.blue()
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        embed.add_field(
            name="👤 Member",
            value=member.mention,
            inline=True
        )

        embed.add_field(
            name="🏴‍☠️ Pirate #",
            value=str(member.guild.member_count),
            inline=True
        )

        embed.set_footer(
            text="Welcome aboard, pirate!"
        )

        await channel.send(
            embed=embed
        )

    # =========================================
    # MEMBER LEAVE
    # =========================================

    @commands.Cog.listener()
    async def on_member_remove(self, member):

        data = self.get_config(member.guild.id)

        if not data:
            return

        goodbye_channel_id = data[2]

        if not goodbye_channel_id:
            return

        channel = member.guild.get_channel(
            goodbye_channel_id
        )

        if not channel:
            return

        embed = discord.Embed(
            title="🌊 A PIRATE HAS LEFT",
            description=(
                f"**{member.display_name}** has left "
                f"**{member.guild.name}**.\n\n"
                "The seas are a little quieter now..."
            ),
            color=discord.Color.dark_blue()
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        embed.add_field(
            name="🏴‍☠️ Pirates Remaining",
            value=str(member.guild.member_count),
            inline=True
        )

        embed.set_footer(
            text="Fair winds, pirate."
        )

        await channel.send(
            embed=embed
        )


# =========================================
# SETUP
# =========================================

async def setup(bot):
    await bot.add_cog(Welcome(bot))
