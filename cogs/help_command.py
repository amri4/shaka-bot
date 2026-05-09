import discord
from discord.ext import commands

COMMANDS_DATA = {
    "⚖️ Justice": {
        "shaka judge @user <reason>": "Pass a formal judgment on a user. Records the verdict in the database.",
        "shaka verdicts": "Show the 5 most recent judgments issued in this server.",
        "shaka verdict <id>": "Look up a specific judgment by its ID.",
        "shaka truth": "Shaka declares a philosophical truth.",
        "shaka scan @user": "Analyze a user's threat level.",
        "shaka siblings": "List all six Vegapunk satellites.",
    },
    "❓ Help": {
        "shaka?": "Show this help menu.",
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
            title=f"Shaka — {category}",
            color=discord.Color.blue(),
        )
        for name, desc in cmds.items():
            embed.add_field(name=f"`{name}`", value=desc, inline=False)
        embed.set_footer(text="Satellite 01 — Shaka (Good) | Prefix: shaka")
        await interaction.response.edit_message(embed=embed)


class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(CategorySelect())


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="?")
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="⚖️ Shaka — Satellite 01 (Good)",
            description=(
                "I am Shaka. Logic and justice are my domains.\n"
                "Select a category below to view available commands.\n\n"
                "**Prefix:** `shaka`"
            ),
            color=discord.Color.blue(),
        )
        embed.set_footer(text="Use the menu below to explore commands.")
        await ctx.send(embed=embed, view=HelpView())


async def setup(bot):
    await bot.add_cog(HelpCog(bot))
