from utils.discord_setup import *


@modal(
    "Example Modal"
)
async def example_modal(
    interaction,
    values
):

    name = values["name"]

    await interaction.response.send_message(
        f"Hello {name}!",
        ephemeral=True
    )


example_modal.input(
    "name",
    "Your Name",
    placeholder="Enter your name",
    required=True
)
