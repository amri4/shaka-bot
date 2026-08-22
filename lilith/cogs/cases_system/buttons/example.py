from utils.discord_setup import *

from ..modals.example import (
    example_modal
)


@button(
    label="Open Modal",
    color="blue"
)
async def open_modal(
    interaction,
    button
):

    await interaction.response.send_modal(
        create_modal(
            example_modal
        )
    )
