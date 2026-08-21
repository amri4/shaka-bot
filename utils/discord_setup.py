import discord

from discord.ext import commands

import importlib
import pkgutil
import functools


# =========================================================
# PUBLIC API
# =========================================================

__all__ = [
    "command",
    "listener",
    "button",
    "select",
    "modal",
    "ui",
    "create_modal",
    "setup_module",
    "setup_system",
]


# =========================================================
# MARKERS
# =========================================================

COMMAND_MARKER = "__discord_setup_command__"
LISTENER_MARKER = "__discord_setup_listener__"
BUTTON_MARKER = "__discord_setup_button__"
SELECT_MARKER = "__discord_setup_select__"
MODAL_MARKER = "__discord_setup_modal__"


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

    if isinstance(
        color,
        discord.ButtonStyle
    ):
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
# MODAL
# =========================================================

def modal(
    title,
    *,
    timeout=180
):

    def decorator(func):

        setattr(
            func,
            MODAL_MARKER,
            {
                "title": title,
                "timeout": timeout,
                "inputs": []
            }
        )

        # -------------------------------------------------
        # INPUT
        # -------------------------------------------------

        def input_field(
            name,
            label,
            *,
            placeholder=None,
            default=None,
            required=True,
            min_length=None,
            max_length=None,
            style=discord.TextStyle.short,
            row=None
        ):

            data = getattr(
                func,
                MODAL_MARKER
            )

            data["inputs"].append(
                {
                    "name": name,
                    "label": label,
                    "placeholder": placeholder,
                    "default": default,
                    "required": required,
                    "min_length": min_length,
                    "max_length": max_length,
                    "style": style,
                    "row": row
                }
            )

            return func

        func.input = input_field

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

        # ---------------------------------------------
        # SelectOption
        # ---------------------------------------------

        if isinstance(
            option,
            discord.SelectOption
        ):

            options.append(
                option
            )

        # ---------------------------------------------
        # Dictionary
        # ---------------------------------------------

        elif isinstance(
            option,
            dict
        ):

            options.append(
                discord.SelectOption(
                    **option
                )
            )

        # ---------------------------------------------
        # Simple value
        # ---------------------------------------------

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
# MAKE MODAL
# =========================================================

def _make_modal(func):

    data = getattr(
        func,
        MODAL_MARKER
    )

    class GeneratedModal(
        discord.ui.Modal
    ):

        def __init__(self):

            super().__init__(
                title=data["title"],
                timeout=data["timeout"]
            )

            self._inputs = {}

            for input_data in data["inputs"]:

                text_input = discord.ui.TextInput(
                    label=input_data["label"],
                    placeholder=input_data["placeholder"],
                    default=input_data["default"],
                    required=input_data["required"],
                    min_length=input_data["min_length"],
                    max_length=input_data["max_length"],
                    style=input_data["style"]
                )

                self.add_item(
                    text_input
                )

                self._inputs[
                    input_data["name"]
                ] = text_input

        async def on_submit(
            self,
            interaction: discord.Interaction
        ):

            values = {}

            for name, text_input in self._inputs.items():

                values[name] = text_input.value

            await func(
                interaction,
                values
            )

    return GeneratedModal


# =========================================================
# CREATE MODAL
# =========================================================

def create_modal(func):

    if not hasattr(
        func,
        MODAL_MARKER
    ):

        raise TypeError(
            f"{func!r} is not a discord_setup modal."
        )

    ModalClass = _make_modal(
        func
    )

    return ModalClass()


# =========================================================
# UI
# =========================================================

def ui(
    *components,
    timeout=180
):

    attributes = {}

    for component in components:

        # =============================================
        # BUTTON
        # =============================================

        if hasattr(
            component,
            BUTTON_MARKER
        ):

            attributes[
                component.__name__
            ] = _make_button(
                component
            )

            continue

        # =============================================
        # SELECT
        # =============================================

        if hasattr(
            component,
            SELECT_MARKER
        ):

            attributes[
                component.__name__
            ] = _make_select(
                component
            )

            continue

        raise TypeError(
            f"{component!r} is not a supported UI component."
        )

    # =============================================
    # CREATE VIEW CLASS
    # =============================================

    GeneratedView = type(
        "GeneratedView",
        (discord.ui.View,),
        attributes
    )

    # =============================================
    # CREATE VIEW INSTANCE
    # =============================================

    return GeneratedView(
        timeout=timeout
    )


# =========================================================
# BUILD COMMAND
# =========================================================

def _build_command(
    func,
    kwargs
):

    original = func

    @functools.wraps(
        original
    )
    async def command_wrapper(
        self,
        *args,
        **command_kwargs
    ):

        return await original(
            *args,
            **command_kwargs
        )

    return commands.command(
        **kwargs
    )(
        command_wrapper
    )


# =========================================================
# BUILD LISTENER
# =========================================================

def _build_listener(
    func,
    listener_name
):

    original = func

    @functools.wraps(
        original
    )
    async def listener_wrapper(
        self,
        *args,
        **kwargs
    ):

        return await original(
            *args,
            **kwargs
        )

    return commands.Cog.listener(
        name=listener_name
    )(
        listener_wrapper
    )


# =========================================================
# AUTOMATIC COG CREATION
# =========================================================

def _build_cog(
    bot,
    module
):

    attributes = {}

    print(
        f"🔧 Building Cog: {module.__name__}"
    )

    for name in dir(module):

        obj = getattr(
            module,
            name
        )

        if not callable(obj):
            continue

        # =============================================
        # COMMAND
        # =============================================

        if hasattr(
            obj,
            COMMAND_MARKER
        ):

            kwargs = getattr(
                obj,
                COMMAND_MARKER
            )

            attributes[name] = _build_command(
                obj,
                kwargs
            )

            print(
                f"  ├─ Registered command: {name}"
            )

            continue

        # =============================================
        # LISTENER
        # =============================================

        if hasattr(
            obj,
            LISTENER_MARKER
        ):

            listener_name = getattr(
                obj,
                LISTENER_MARKER
            )

            attributes[name] = _build_listener(
                obj,
                listener_name
            )

            print(
                f"  ├─ Registered listener: {name}"
            )

            continue

    # =============================================
    # NOTHING TO REGISTER
    # =============================================

    if not attributes:

        return None

    # =============================================
    # COG CONSTRUCTOR
    # =============================================

    def __init__(
        self,
        bot
    ):

        self.bot = bot

    attributes["__init__"] = __init__

    # =============================================
    # CREATE COG CLASS
    # =============================================

    CogClass = type(
        f"{module.__name__.split('.')[-1].title()}Cog",
        (commands.Cog,),
        attributes
    )

    print(
        f"  ✅ Created Cog: {CogClass.__name__}"
    )

    return CogClass(
        bot
    )


# =========================================================
# SETUP MODULE
# =========================================================

async def setup_module(
    bot,
    module
):

    cog = _build_cog(
        bot,
        module
    )

    if cog is None:

        return None

    await bot.add_cog(
        cog
    )

    print(
        f"  ✅ Loaded: {module.__name__}"
    )

    return cog


# =========================================================
# SETUP SYSTEM
# =========================================================

async def setup_system(
    bot,
    package_name
):

    print(
        f"🔍 Scanning system: {package_name}"
    )

    package = importlib.import_module(
        package_name
    )

    for module_info in pkgutil.walk_packages(
        package.__path__,
        prefix=f"{package.__name__}."
    ):

        module_name = module_info.name

        # ---------------------------------------------
        # Don't load cog.py again
        # ---------------------------------------------

        if module_name.endswith(
            ".cog"
        ):

            continue

        # ---------------------------------------------
        # Ignore private modules
        # ---------------------------------------------

        if any(
            part.startswith("_")
            for part in module_name.split(".")
        ):

            continue

        # =============================================
        # IMPORT MODULE
        # =============================================

        try:

            module = importlib.import_module(
                module_name
            )

        except Exception as e:

            print(
                f"  ❌ Failed to import "
                f"{module_name}: {e}"
            )

            continue

        # =============================================
        # SETUP MODULE
        # =============================================

        try:

            await setup_module(
                bot,
                module
            )

        except Exception as e:

            print(
                f"  ❌ Failed to setup "
                f"{module_name}: {e}"
        )
