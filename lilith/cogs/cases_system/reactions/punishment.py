from utils.discord_setup import *

from ..punishments import *


PUNISHMENTS = {
    kick.EMOJI: kick,
    timeout.EMOJI: timeout,
}


async def get_selected_punishments(
    message,
    user_id
):

    selected = []

    for reaction in message.reactions:

        punishment = PUNISHMENTS.get(
            str(reaction.emoji)
        )

        if punishment is None:
            continue

        users = [
            user.id
            async for user in reaction.users()
        ]

        if user_id in users:

            selected.append(
                punishment
            )

    return selected
