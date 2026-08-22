from utils.discord_setup import *

from ..reactions.punishments import (
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

    selected = get_selected_punishments(
        interaction.message.id,
        interaction.user.id
    )

    if not selected:

        await interaction.response.send_message(
            "❌ Select at least one punishment first.",
            ephemeral=True
        )

        return

    print(
        "Selected punishments:",
        [
            punishment.NAME
            for punishment in selected
        ]
    )

    await interaction.response.send_message(
        "Selected punishments: "
        + ", ".join(
            punishment.NAME
            for punishment in selected
        ),
        ephemeral=True
    )
