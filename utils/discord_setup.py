import discord

from discord.ext import commands


# =========================================================
# MARKERS
# =========================================================

COMMAND_MARKER = "__discord_setup_command__"
LISTENER_MARKER = "__discord_setup_listener__"
BUTTON_MARKER = "__discord_setup_button__"
SELECT_MARKER = "__discord_setup_select__"


# =========================================================
# BUTTON COLORS
# =========================================================

BUTTON_COLORS = {
    "blue": discord.ButtonStyle.primary,
    "gray": discord.ButtonStyle.secondary,
    "grey": discord.ButtonStyle.secondary,
    "green": discord.ButtonStyle.success,
    "red": discord.ButtonStyle.danger,
}


def get_button_style(color):

    if isinstance(color, discord.ButtonStyle):
        return color

    return BUTTON_COLORS.get(
        str(color).lower(),
        discord.ButtonStyle.secondary
    )


# =========================================================
# COMMAND
# =========================================================

def command(**kwargs):

    def decorator(func):

        setattr(
            func,
            COMMAND_MARKER,
            kwargs
        )

        return func

    return decorator


# =========================================================
# LISTENER
# =========================================================

def listener(name=None):

    def decorator(func):

        setattr(
            func,
            LISTENER_MARKER,
            name
        )

        return func

    return decorator


# =========================================================
# BUTTON
# =========================================================

def button(
    label,
    *,
    color="gray",
    emoji=None,
    row=None,
    disabled=False
):

    def decorator(func):

        setattr(
            func,
            BUTTON_MARKER,
            {
                "label": label,
                "color": color,
                "emoji": emoji,
                "row": row,
                "disabled": disabled
            }
        )

        return func

    return decorator


# =========================================================
# SELECT
# =========================================================

def select(
    placeholder=None,
    *,
    options=None,
    min_values=1,
    max_values=1,
    row=None,
    disabled=False
):

    def decorator(func):

        setattr(
            func,
            SELECT_MARKER,
            {
                "placeholder": placeholder,
                "options": options or [],
                "min_values": min_values,
                "max_values": max_values,
                "row": row,
                "disabled": disabled
            }
        )

        return func

    return decorator


# =========================================================
# MAKE BUTTON
# =========================================================

def _make_button(func):

    data = getattr(
        func,
        BUTTON_MARKER
    )

    return discord.ui.button(
        label=data["label"],
        style=get_button_style(
            data["color"]
        ),
        emoji=data["emoji"],
        row=data["row"],
        disabled=data["disabled"]
    )(func)


# =========================================================
# MAKE SELECT
# =========================================================

def _make_select(func):

    data = getattr(
        func,
        SELECT_MARKER
    )

    options = []

    for option in data["options"]:

        # Already a SelectOption
        if isinstance(
            option,
            discord.SelectOption
        ):
            options.append(option)

        # Dictionary
        elif isinstance(
            option,
            dict
        ):
            options.append(
                discord.SelectOption(
                    **option
                )
            )

        # Simple string
        else:
            options.append(
                discord.SelectOption(
                    label=str(option),
                    value=str(option)
                )
            )

    return discord.ui.select(
        placeholder=data["placeholder"],
        options=options,
        min_values=data["min_values"],
        max_values=data["max_values"],
        row=data["row"],
        disabled=data["disabled"]
    )(func)


# =========================================================
# UI
# =========================================================

def ui(*components, timeout=180):

    """
    Creates a fresh discord.ui.View.

    Example:

        view = ui(
            approve,
            reject,
            close
        )

    Every call creates a new View.
    """

    class GeneratedView(discord.ui.View):

        def __init__(self):
            super().__init__(
                timeout=timeout
            )

    for component in components:

        component_type = getattr(
            component,
            BUTTON_MARKER,
            None
        )

        if component_type is not None:

            item = _make_button(
                component
            )

            setattr(
                GeneratedView,
                component.__name__,
                item
            )

            continue

        component_type = getattr(
            component,
            SELECT_MARKER,
            None
        )

        if component_type is not None:

            item = _make_select(
                component
            )

            setattr(
                GeneratedView,
                component.__name__,
                item
            )

            continue

        raise TypeError(
            f"{component!r} is not a supported UI component."
        )

    return GeneratedView()


# =========================================================
# AUTOMATIC COG CREATION
# =========================================================

def _build_cog(bot, module):

    attributes = {}

    for name in dir(module):

        obj = getattr(
            module,
            name
        )

        if not callable(obj):
            continue

        # ---------------------------------------------
        # COMMAND
        # ---------------------------------------------

        if hasattr(
            obj,
            COMMAND_MARKER
        ):

            kwargs = getattr(
                obj,
                COMMAND_MARKER
            )

            attributes[name] = commands.command(
                **kwargs
            )(obj)

        # ---------------------------------------------
        # LISTENER
        # ---------------------------------------------

        elif hasattr(
            obj,
            LISTENER_MARKER
        ):

            listener_name = getattr(
                obj,
                LISTENER_MARKER
            )

            attributes[name] = (
                commands.Cog.listener(
                    name=listener_name
                )(obj)
            )

    # Nothing to register
    if not attributes:
        return None

    # Cog constructor
    def __init__(self, bot):
        self.bot = bot

    attributes["__init__"] = __init__

    CogClass = type(
        f"{module.__name__.split('.')[-1].title()}Cog",
        (commands.Cog,),
        attributes
    )

    return CogClass(bot)


# =========================================================
# SETUP MODULE
# =========================================================

async def setup_module(bot, module):

    """
    Automatically turns decorated commands/listeners
    in a module into a Cog and loads it into the bot.
    """

    cog = _build_cog(
        bot,
        module
    )

    if cog is None:
        return None

    await bot.add_cog(
        cog
    )

    return cog
