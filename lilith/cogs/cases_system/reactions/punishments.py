from utils.discord_setup import *
from ..punishments import *

PUNISHMENTS = {
  kick.EMOJI: kick,
  timeout.EMOJI: timeout
}
selected_punishments = {}

@listener("on_raw_reaction_add")
async def punishment_reaction_add(payload):
    if payload.guild_id is None:
        return 
    if payload.member is None:
        return
    if payload.member.bot:
        return

    punishment = PUNISHMENTS.get(str(payload.emoji))

    if punishment is None:
        return

    key = (payload.message_id, payload.user_id)
    selected_punishments.setdefault(key, set()).add(punishment)

@listener("on_raw_reaction_remove")
async def punishment_reaction_remove(
    payload
):

    punishment = PUNISHMENTS.get(
        str(payload.emoji)
    )

    if punishment is None:
        return

    key = (
        payload.message_id,
        payload.user_id
    )

    selected = selected_punishments.get(
        key
    )

    if selected is None:
        return

    selected.discard(
        punishment
    )

    if not selected:

        selected_punishments.pop(
            key
        )

def get_selected_punishments(
    message_id,
    user_id
):

    return selected_punishments.get(
        (
            message_id,
            user_id
        ),
        set()
    )
