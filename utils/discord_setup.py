import discord


# =========================================
# BUTTON COLORS
# =========================================

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


# =========================================
# BUTTON
# =========================================

def button(
    label,
    *,
    color="gray",
    emoji=None,
    row=None,
    disabled=False
):

    def decorator(func):

        func.__discord_button__ = {
            "label": label,
            "color": color,
            "emoji": emoji,
            "row": row,
            "disabled": disabled
        }

        return func

    return decorator


# =========================================
# SELECT MENU
# =========================================

def select(
    *,
    placeholder=None,
    options=None,
    min_values=1,
    max_values=1,
    row=None,
    disabled=False
):

    def decorator(func):

        func.__discord_select__ = {
            "placeholder": placeholder,
            "options": options or [],
            "min_values": min_values,
            "max_values": max_values,
            "row": row,
            "disabled": disabled
        }

        return func

    return decorator


# =========================================
# MODAL
# =========================================

def modal(
    title,
    *,
    timeout=180
):

    def decorator(func):

        func.__discord_modal__ = {
            "title": title,
            "timeout": timeout,
            "inputs": []
        }

        def input_field(
            name,
            label,
            *,
            placeholder=None,
            default=None,
            required=True,
            min_length=None,
            max_length=None,
            style=discord.TextStyle.short
        ):

            func.__discord_modal__["inputs"].append({
                "name": name,
                "label": label,
                "placeholder": placeholder,
                "default": default,
                "required": required,
                "min_length": min_length,
                "max_length": max_length,
                "style": style
            })

            return func

        func.input = input_field

        return func

    return decorator


# =========================================
# CREATE MODAL
# =========================================

def create_modal(func):

    data = getattr(
        func,
        "__discord_modal__"
    )

    class GeneratedModal(discord.ui.Modal):

        def __init__(self):

            super().__init__(
                title=data["title"],
                timeout=data["timeout"]
            )

            self.inputs = {}

            for field in data["inputs"]:

                text_input = discord.ui.TextInput(
                    label=field["label"],
                    placeholder=field["placeholder"],
                    default=field["default"],
                    required=field["required"],
                    min_length=field["min_length"],
                    max_length=field["max_length"],
                    style=field["style"]
                )

                self.add_item(text_input)

                self.inputs[
                    field["name"]
                ] = text_input

        async def on_submit(self, interaction):

            values = {
                name: field.value
                for name, field in self.inputs.items()
            }

            await func(
                interaction,
                values
            )

    return GeneratedModal()


# =========================================
# UI VIEW
# =========================================

def ui(
    *components,
    timeout=180
):

    class GeneratedView(discord.ui.View):

        def __init__(self):

            super().__init__(
                timeout=timeout
            )

            for component in components:

                # -------------------------
                # BUTTON
                # -------------------------

                if hasattr(
                    component,
                    "__discord_button__"
                ):

                    data = component.__discord_button__

                    item = discord.ui.Button(
                        label=data["label"],
                        style=get_button_style(
                            data["color"]
                        ),
                        emoji=data["emoji"],
                        row=data["row"],
                        disabled=data["disabled"]
                    )

                    async def callback(
                        interaction,
                        item=item,
                        func=component
                    ):

                        await func(
                            interaction,
                            item
                        )

                    item.callback = callback

                    self.add_item(item)

                    continue

                # -------------------------
                # SELECT
                # -------------------------

                if hasattr(
                    component,
                    "__discord_select__"
                ):

                    data = component.__discord_select__

                    options = []

                    for option in data["options"]:

                        if isinstance(
                            option,
                            discord.SelectOption
                        ):
                            options.append(option)

                        elif isinstance(
                            option,
                            dict
                        ):
                            options.append(
                                discord.SelectOption(
                                    **option
                                )
                            )

                        else:
                            options.append(
                                discord.SelectOption(
                                    label=str(option),
                                    value=str(option)
                                )
                            )

                    select_item = discord.ui.Select(
                        placeholder=data["placeholder"],
                        options=options,
                        min_values=data["min_values"],
                        max_values=data["max_values"],
                        row=data["row"],
                        disabled=data["disabled"]
                    )

                    async def callback(
                        interaction,
                        item=select_item,
                        func=component
                    ):

                        await func(
                            interaction,
                            item
                        )

                    select_item.callback = callback

                    self.add_item(
                        select_item
                    )

                    continue

                raise TypeError(
                    f"{component!r} is not a supported UI component."
                )

    return GeneratedView()
