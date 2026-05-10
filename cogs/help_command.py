import discord
from discord.ext import commands

COMMANDS_DATA = {
    "🧠 Database & Stats": {
        "shaka stats [@user]": "View a user's berries, trust level, and profile.",
        "shaka top": "Berry leaderboard for this server.",
        "shaka logs": "Show the 8 most recent berry transactions.",
        "shaka system": "View the full SHAKA system status and server stats.",
    },
    "⚙️ Admin (Admins Only)": {
        "shaka give @user <amount>": "Grant berries to a user.",
        "shaka reset @user": "Wipe a user's data from the database.",
    },
    "❓ Help": {
        "shaka help": "Show this help menu.",
    },
}


class CategorySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=category, description=f"{len(cmds)} command(s)")
            for category, cmds in COMMANDS_DATA.items()
        ]
        super().__init__(placeholder="Select a command category...", options=options)

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        cmds = COMMANDS_DATA[category]
        embed = discord.Embed(
            title=f"🧠 Shaka — {category}",
            color=discord.Color.blue(),
        )
        for name, desc in cmds.items():
            embed.add_field(name=f"`{name}`", value=desc, inline=False)
        embed.set_footer(text="Satellite 01 — Shaka (Good) | Central Memory Core | Prefix: shaka")
        await interaction.response.edit_message(embed=embed)


class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(CategorySelect())


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", aliases=["?"])
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="🧠 SHAKA — Satellite 01 (Good)",
            description=(
                "I am the central memory core of the Vegapunk system.\n"
                "All berry and trust data passes through me.\n\n"
                "**Prefix:** `shaka`"
            ),
            color=discord.Color.blue(),
        )
        embed.set_footer(text="Select a category below to view commands.")
        await ctx.send(embed=embed, view=HelpView())


async def setup(bot):
    await bot.add_cog(HelpCog(bot))
