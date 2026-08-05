# views/character.py

import discord

from utils import characters


class CharacterModal(discord.ui.Modal, title="Claim a Character"):

    name = discord.ui.TextInput(
        label="Character Name",
        placeholder="Example: Luffy, Trafalgar Law, Zoro...",
        max_length=100,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):

        if characters.user_has_character(interaction.user.id):
            return await interaction.response.send_message(
                "❌ You have already claimed a character.",
                ephemeral=True
            )

        character = characters.search(self.name.value)

        if character is None:
            return await interaction.response.send_message(
                "❌ Character not found.",
                ephemeral=True
            )

        if character["claimed_by"] is not None:
            return await interaction.response.send_message(
                f"❌ **{character['name']}** has already been claimed.",
                ephemeral=True
            )

        characters.claim(
            interaction.user.id,
            character["name"]
        )

        try:
            await interaction.user.edit(
                nick=character["name"]
            )
        except Exception:
            pass

        embed = discord.Embed(
            title="🏴 Character Claimed",
            description=(
                f"You are now playing as **{character['name']}**.\n\n"
                "Welcome to the Grand Line!"
            ),
            color=0x2ecc71
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


class CharacterView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Claim Character",
        emoji="🎭",
        style=discord.ButtonStyle.green,
        custom_id="character_claim"
    )
    async def claim(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            CharacterModal()
        )
