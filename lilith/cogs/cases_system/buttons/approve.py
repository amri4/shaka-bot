from utils.discord_setup import *


@button(
    label="approve",
    color="green"
)
async def approve(interaction, button):

    await interaction.response.send_message(
        "✅ Approved",
        ephemeral=True
    )
