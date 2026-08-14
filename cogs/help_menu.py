import discord
from discord.ext import commands


class HelpView(discord.ui.View):

    def __init__(self, bot):
        super().__init__(timeout=120)

        self.bot = bot
        self.categories = {}

        for cmd in bot.commands:
            if cmd.hidden:
                continue

            category = getattr(cmd, "help_category", None)

            if category:
                self.categories.setdefault(category, []).append(cmd)

        self.add_item(HelpSelect(self))

    def home_embed(self):
        total_commands = sum(
            len(commands_list)
            for commands_list in self.categories.values()
        )

        category_text = "\n".join(
            f"• {category}"
            for category in sorted(self.categories)
        ) or "No categories."

        embed = discord.Embed(
            title=f"{self.bot.user.name} Help",
            description=(
                f"Welcome to **{self.bot.user.name}**'s help menu.\n\n"
                "Select a category below to view its commands."
            ),
            color=discord.Color.blue()
        )

        embed.add_field(
            name="📚 Categories",
            value=category_text,
            inline=False
        )

        embed.add_field(
            name="⚡ Commands",
            value=str(total_commands)
        )

        return embed

    def category_embed(self, category):
        embed = discord.Embed(
            title=category,
            color=discord.Color.blue()
        )

        for cmd in self.categories[category]:
            embed.add_field(
                name=cmd.name,
                value=cmd.description or "No description.",
                inline=False
            )

        return embed


class HelpSelect(discord.ui.Select):

    def __init__(self, help_view):
        self.help_view = help_view

        options = [
            discord.SelectOption(
                label="Home",
                value="__home__",
                emoji="🏠"
            )
        ]

        for category in sorted(help_view.categories):
            options.append(
                discord.SelectOption(
                    label=category,
                    value=category
                )
            )

        super().__init__(
            placeholder="Select a category...",
            options=options
        )

    async def callback(self, interaction):
        category = self.values[0]

        if category == "__home__":
            embed = self.help_view.home_embed()
        else:
            embed = self.help_view.category_embed(category)

        await interaction.response.edit_message(
            embed=embed,
            view=self.help_view
        )


class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        view = HelpView(self.bot)

        await ctx.send(
            embed=view.home_embed(),
            view=view
        )


async def setup(bot):
    await bot.add_cog(Help(bot))
