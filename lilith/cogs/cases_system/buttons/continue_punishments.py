from utils.discord_setup import *

from ..reactions.punishment import (
    get_selected_punishments
)


@button(
    label="Continue",
    color="blue"
)
async def continue_punishments(
    interaction,
    button
):

    selected = await get_selected_punishments(
        interaction.message,
        interaction.user.id
    )

    print(
        "Punishment selected:",
        [
            punishment.NAME
            for punishment in selected
        ]
    )

    if not selected:

        await interaction.response.send_message(
            "❌ Select at least one punishment first.",
            ephemeral=True
        )

        return

    await interaction.response.send_message(
        "Selected: " + ", ".join(
            punishment.NAME
            for punishment in selected
        ),
        ephemeral=True
    )
