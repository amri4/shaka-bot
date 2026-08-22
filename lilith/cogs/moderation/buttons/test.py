from utils.discord_setup import button


@button(
    "Test",
    color="blue"
)
async def test_button(
    interaction,
    button
):

    await interaction.response.send_message(
        "Button works!",
        ephemeral=True
    )
