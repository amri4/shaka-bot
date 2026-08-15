import discord
import inspect
from discord.ext import commands


class HelpView(discord.ui.View):

    def __init__(self, bot):
        super().__init__(timeout=None)

        self.bot = bot
        self.categories = {}

        # =========================================
        # AUTOMATICALLY FIND COMMANDS
        # =========================================

        for cmd in bot.commands:

            if cmd.hidden:
                continue

            category = cmd.extras.get(
                "help_category"
            )

            if category:
                self.categories.setdefault(
                    category,
                    []
                ).append(cmd)

        self.add_item(
            HelpSelect(self)
        )

    # =========================================
    # GET COMMAND USAGE
    # =========================================

    def get_usage(self, cmd):

        # =====================================
        # CUSTOM USAGE
        # =====================================

        custom_usage = cmd.extras.get(
            "help_usage"
        )

        if custom_usage:

            prefix = self.bot.command_prefix

            if isinstance(
                prefix,
                (list, tuple)
            ):
                prefix = prefix[0]

            usage = (
                f"{prefix} "
                f"{cmd.name}"
            )

            if custom_usage.strip():

                usage += (
                    " "
                    + custom_usage.strip()
                )

            return usage

        # =====================================
        # AUTOMATIC USAGE
        # =====================================

        params = inspect.signature(
            cmd.callback
        ).parameters

        args = []

        for name, param in params.items():

            # Don't show self / ctx
            if name in (
                "self",
                "ctx",
                "context"
            ):
                continue

            # Ignore **kwargs
            if (
                param.kind
                == inspect.Parameter.VAR_KEYWORD
            ):
                continue

            # Required argument
            if (
                param.default
                is inspect.Parameter.empty
            ):

                args.append(
                    f"<{name}>"
                )

            # Optional argument
            else:

                args.append(
                    f"[{name}]"
                )

        prefix = self.bot.command_prefix

        if isinstance(
            prefix,
            (list, tuple)
        ):
            prefix = prefix[0]

        usage = (
            f"{prefix} "
            f"{cmd.name}"
        )

        if args:

            usage += (
                " "
                + " ".join(args)
            )

        return usage

    # =========================================
    # GET CATEGORY EMOJI
    # =========================================

    def get_category_emoji(self, category):

        if (
            category
            and not category[0].isalnum()
        ):
            return category[0]

        return "📚"

    # =========================================
    # HOME EMBED
    # =========================================

    def home_embed(self):

        total_commands = sum(
            len(command_list)
            for command_list
            in self.categories.values()
        )

        if self.categories:

            category_text = "\n".join(
                f"{category}"
                for category
                in sorted(self.categories)
            )

        else:

            category_text = (
                "No categories."
            )

        prefix = self.bot.command_prefix

        if isinstance(
            prefix,
            (list, tuple)
        ):
            prefix = prefix[0]

        embed = discord.Embed(
            title=(
                f"{self.bot.user.name} Help"
            ),
            description=(
                "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Welcome to **{self.bot.user.name}**'s "
                "command center.\n\n"
                "Select a category below to explore "
                "the available commands.\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=discord.Color.blue()
        )

        embed.add_field(
            name="📚 COMMAND CATEGORIES",
            value=category_text,
            inline=False
        )

        embed.add_field(
            name="⚡ COMMANDS",
            value=f"`{total_commands}`",
            inline=True
        )

        embed.add_field(
            name="🔧 PREFIX",
            value=f"`{prefix}`",
            inline=True
        )

        embed.set_footer(
            text="Select a category below"
        )

        return embed

    # =========================================
    # CATEGORY EMBED
    # =========================================

    def category_embed(self, category):

        emoji = self.get_category_emoji(
            category
        )

        category_name = category

        if category.startswith(emoji):

            category_name = (
                category[len(emoji):]
                .strip()
            )

        commands_list = self.categories[
            category
        ]

        command_text = []

        for cmd in commands_list:

            usage = self.get_usage(cmd)

            command_text.append(
                f"**{cmd.name}**\n"
                f"`{usage}`\n"
                f"{cmd.description or 'No description.'}"
            )

        embed = discord.Embed(
            title=(
                f"{emoji} "
                f"{category_name.upper()} COMMANDS"
            ),
            description=(
                "━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=discord.Color.blue()
        )

        embed.add_field(
            name="\u200b",
            value="\n\n".join(
                command_text
            ),
            inline=False
        )

        embed.add_field(
            name="\u200b",
            value=(
                "━━━━━━━━━━━━━━━━━━━━━━"
            ),
            inline=False
        )

        embed.add_field(
            name="\u200b",
            value=(
                f"**{len(commands_list)} commands**"
            ),
            inline=False
        )

        return embed


# =========================================
# SELECT MENU
# =========================================

class HelpSelect(discord.ui.Select):

    def __init__(self, help_view):

        self.help_view = help_view

        options = [
            discord.SelectOption(
                label="Home",
                value="__home__",
                emoji="🏠",
                description=(
                    "Return to the help home page"
                )
            )
        ]

        for category in sorted(
            help_view.categories
        ):

            emoji = (
                help_view
                .get_category_emoji(category)
            )

            name = category

            if category.startswith(emoji):

                name = (
                    category[len(emoji):]
                    .strip()
                )

            options.append(
                discord.SelectOption(
                    label=name[:100],
                    value=category[:100],
                    emoji=emoji,
                    description=(
                        f"View {name} commands"
                    )[:100]
                )
            )

        super().__init__(
            placeholder="Select a category...",
            options=options
        )

    async def callback(
        self,
        interaction
    ):

        category = self.values[0]

        if category == "__home__":

            embed = (
                self.help_view
                .home_embed()
            )

        else:

            embed = (
                self.help_view
                .category_embed(category)
            )

        await interaction.response.edit_message(
            embed=embed,
            view=self.help_view
        )


# =========================================
# HELP COG
# =========================================

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

    await bot.add_cog(
        Help(bot)
                )
